"""
Dambreak flow with obstacle -Ubbink (1997)
"""
import numpy as np
from math import sqrt
from proteus import (Domain, Context,
                     FemTools as ft,
                     #SpatialTools as st,
                     MeshTools as mt,
                     WaveTools as wt)
from proteus.mprans import SpatialTools as st
from proteus.SpatialTools import Shape
from proteus.Profiling import logEvent
from proteus.mprans.SpatialTools import TankWithObstacles2D
from proteus.ctransportCoefficients import (smoothedHeaviside,
                                            smoothedHeaviside_integral)
import proteus.TwoPhaseFlow.TwoPhaseFlowProblem as TpFlow


# Context Options

opts=Context.Options([
    # water column 
    ("mwl", 0.292, "Height of water column in m"),
    ("water_width", 0.146, "Width of  water column in m"),
    ("rho_0",998.2,"water density"),
    ("nu_0",1.004e-6,"water viscosity"),
    ("rho_1",1.205,"air density"),
    ("nu_1",1.500e-5,"air viscosity"),
    ("sigma",0.0, "surface tension"),
    # tank
    ("tank_dim", (0.584, 0.584), "Dimensions of the tank  in m"),
    #obstacle
    ("obstacle_dim", (0.024, 0.048),"Dimensions of the obstacle in m"),
    ("obstacle_x_start", 0.292,"x location of start of obstacle  in m"),
    #gravity 
    ("g",(0,-9.81,0), "Gravity vector in m/s^2"),
    # gauges
    ("gauge_output", True, "Produce gauge data"),
    ("gauge_location_p", (3.219999, 0.12, 0), "Pressure gauge location in m"),
    # mesh refinement and timestep
    ("he",0.015,"mesh cell size"),
    ("cfl", 0.33 ,"Target cfl"),
    ("ecH", 1.5,"Smoothing Coefficient"),
    # run time options
    ("duration",10.,"duration of simulation"),
    ("T", 0.09 ,"Simulation time in s"),
    ("dt_fixed", 0.01, "Fixed time step in s"),
    ("dt_init", 0.001 ,"Maximum initial time step in s"),
    ("dt_output",0.05, "output stepping")
    ])

# Domain 
domain = Domain.PlanarStraightLineGraphDomain()

# Tank
tank = TankWithObstacles2D(domain=domain,
			   dim=opts.tank_dim
		           )


shape1=st.Rectangle(domain,dim=[opts.obstacle_dim[0],opts.obstacle_dim[1]],coords=[0.304,0.024])
shape1.setHoles([[0.304,0.024]])

# Gauges
if opts.gauge_output:
    tank.attachPointGauges('twp',
        	           gauges = ((('p',), (opts.gauge_location_p,)),),
                           activeTime=(0, opts.T),
                           sampleRate=0,
                           fileName='pressureGauge.csv'
                           )

# Boundary Conditions 
tank.BC['y+'].setAtmosphere()
tank.BC['y-'].setFreeSlip()
tank.BC['x+'].setFreeSlip()
tank.BC['x-'].setFreeSlip()

for bc in shape1.BC_list:
    bc.setFreeSlip()

# Mesh 
domain.MeshOptions.he = opts.he


# Initial conditions
def signedDistance(x):
    phi_x = x[0] - opts.water_width
    phi_z = x[1] - opts.mwl
    if phi_x < 0.0:
        if phi_z < 0.0:
            return max(phi_x, phi_z)
        else:
            return phi_z
    else:
        if phi_z < 0.0:
            return phi_x
        else:
            return sqrt(phi_x ** 2 + phi_z ** 2)

class P_IC:
    def __init__(self):
        self.mwl=opts.mwl
    def uOfXT(self,x,t):
        if signedDistance(x) < 0:
            return -(opts.tank_dim[1] - opts.mwl)*opts.rho_1*opts.g[1] - (opts.mwl - x[1])*opts.rho_0*opts.g[1]
        else:
            return -(opts.tank_dim[1] - opts.mwl)*opts.rho_1*opts.g[1]
class AtRest:
    def uOfXT(self, x, t):
        return 0.0

class VOF_IC:
    def uOfXT(self,x,t):
        return smoothedHeaviside(opts.ecH * opts.he, signedDistance(x))

class LS_IC:
    def uOfXT(self,x,t):
        return signedDistance(x)

initialConditions = {'pressure': P_IC(),
                     'vel_u': AtRest(),
                     'vel_v': AtRest(),
                     'vel_w': AtRest()}

initialConditions['vof'] = VOF_IC()
initialConditions['ncls'] = LS_IC()
initialConditions['rdls'] = LS_IC()


outputStepping = TpFlow.OutputStepping(final_time=opts.duration,
                                       dt_init=opts.dt_init,
                                       # cfl=cfl,
                                       dt_output=opts.dt_output,
                                       nDTout=None,
                                       dt_fixed=None)

myTpFlowProblem = TpFlow.TwoPhaseFlowProblem(ns_model=None,
                                             ls_model=None,
                                             nd=domain.nd,
                                             cfl=opts.cfl,
                                             outputStepping=outputStepping,
                                             structured=False,
                                             he=opts.he,
                                             nnx=None,
                                             nny=None,
                                             nnz=None,
                                             domain=domain,
                                             initialConditions=initialConditions,
                                             boundaryConditions=None, # set with SpatialTools,
                                             )

params = myTpFlowProblem.Parameters

myTpFlowProblem.useSuperLu=False#True
params.physical.densityA = opts.rho_0  # water
params.physical.densityB = opts.rho_1  # air
params.physical.kinematicViscosityA = opts.nu_0  # water
params.physical.kinematicViscosityB = opts.nu_1  # air
params.physical.surf_tension_coeff = opts.sigma

# index in order of
m = params.Models
m.rans2p.index = 0
m.vof.index = 1
m.ncls.index = 2
m.rdls.index = 3
m.mcorr.index = 4
m.rdls.p.coefficients.epsFact=0.75
#m.rans2p.p.CoefficientsOptions.useVF=0.

#Assemble domain
st.assembleDomain(domain)
myTpFlowProblem.Parameters.Models.rans2p.auxiliaryVariables += domain.auxiliaryVariables['twp']
