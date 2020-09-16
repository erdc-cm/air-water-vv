from math import *
import proteus.MeshTools
from proteus import Domain
from proteus.default_n import *   
from proteus.Profiling import logEvent
#from proteus.MeshAdaptPUMI import MeshAdaptPUMI
from proteus import Context
from proteus import Gauges
from proteus.Gauges import PointGauges, LineIntegralGauges

opts = Context.Options([
    ("gauges", True, "Collect data for validation"),
    ])

if opts.gauges:
    pressure_gauges = PointGauges(gauges=((('p',),
                                          ((2.3950,0.4745,0.020),
                                           (2.3950,0.4745,0.100),
                                           (2.4195,0.5255,0.161),
                                           (2.4995,0.5255,0.161))),),
                                  fileName="pressure.csv")
    height_gauges = LineIntegralGauges(gauges=((("vof",),
                                                (((2.724, 0.5, 0.0),
                                                  (2.724, 0.5, 1.0)),
                                                 ((2.228, 0.5, 0.0),
                                                  (2.228, 0.5, 1.0)),
                                                 ((1.732, 0.5, 0.0),
                                                  (1.732, 0.5, 1.0)),
                                                 ((0.582, 0.5, 0.0),
                                                  (0.582, 0.5, 1.0)))),),
                                       fileName="height.csv")



#  Discretization -- input options    
#Refinement=8#4-32 cores
#Refinement=12
runCFL=0.9
Refinement=24
genMesh=True
useOldPETSc=False
useSuperlu=False
spaceOrder = 1
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
applyCorrection=True
useVF = 0.0
useOnlyVF = False
redist_Newton = True
useRANS = 0 # 0 -- None
            # 1 -- K-Epsilon
            # 2 -- K-Omega
# Input checks
if spaceOrder not in [1,2]:
    print "INVALID: spaceOrder" + spaceOrder
    sys.exit()    
    
if useRBLES not in [0.0, 1.0]:
    print "INVALID: useRBLES" + useRBLES 
    sys.exit()

if useMetrics not in [0.0, 1.0]:
    print "INVALID: useMetrics"
    sys.exit()
    
#  Discretization   
nd = 3
if spaceOrder == 1:
    hFactor=1.0
    if useHex:
	 basis=C0_AffineLinearOnCubeWithNodalBasis
         elementQuadrature = CubeGaussQuadrature(nd,2)
         elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,2)     	 
    else:
    	 basis=C0_AffineLinearOnSimplexWithNodalBasis
         elementQuadrature = SimplexGaussQuadrature(nd,3)
         elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,3) 	    
elif spaceOrder == 2:
    hFactor=0.5
    if useHex:    
	basis=C0_AffineLagrangeOnCubeWithNodalBasis
        elementQuadrature = CubeGaussQuadrature(nd,4)
        elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,4)    
    else:    
	basis=C0_AffineQuadraticOnSimplexWithNodalBasis	
        elementQuadrature = SimplexGaussQuadrature(nd,4)
        elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,4)


# Domain and mesh
nLevels = 1
parallelPartitioningType = proteus.MeshTools.MeshParallelPartitioningTypes.node
nLayersOfOverlapForParallel = 0
use_petsc4py=True#False
usePUMI=0

if useHex: 
    hex=True 

    comm=Comm.get()	
    if comm.isMaster():	
        size = numpy.array([[0.520,0.510   ,0.520],
	                    [0.330,0.335833,0.330],
			    [0.320,0.325   ,0.000]])/float(Refinement)
        numpy.savetxt('size.mesh', size)
        failed = os.system("../../scripts/marinHexMesh")      
     
    domain = Domain.MeshHexDomain("marinHex") 
elif usePUMI:
    boundaries=['bottom','top','front','right','back','left','box_top','box_front','box_right','box_back','box_left']
    boundaryTags=dict([(key,i+1) for (i,key) in enumerate(boundaries)])
    domain = Domain.PUMIDomain() #initialize the domain
    domain.faceList=[[1],[2],[3],[4],[5],[6],[8],[9],[10],[11],[12]]
    #set max edge length, min edge length, number of meshadapt iterations and initialize the MeshAdaptPUMI object
    #these are now inputs to the numerics
    he = 0.01#0.015
    he_max = he*2.0#he*3.375
    adaptMesh = False#True
    adaptMesh_nSteps = 10#40
    adaptMesh_numIter = 3
    #
    #domain.PUMIMesh=MeshAdaptPUMI.MeshAdaptPUMI(hmax=0.08, hmin=he, numIter=adaptMesh_numIter,sfConfig="ERM")
    domain.PUMIMesh=MeshAdaptPUMI.MeshAdaptPUMI(hmax=he_max, hmin=he, numIter=adaptMesh_numIter,sfConfig="isotropic",logType="off")
    #read the geometry and mesh
    comm = Comm.init()
    model_dir = "%s-Proc" % comm.size()
    case_mesh = "Marin.smb"
    input_mesh = "%s/%s" % (model_dir,case_mesh)
    domain.PUMIMesh.loadModelAndMesh("Marin.dmg", input_mesh)
    #domain.PUMIMesh.loadModelAndMesh("Marin.dmg", "meshRun0/removedFields.smb")

else:
    L      = [3.22,1.0,1.0]
    box_L  = [0.161,0.403,0.161]
    box_xy = [2.3955,0.2985]
    #he = L[0]/float(6.5*Refinement)
    he = 0.02#L[0]/64.0
    #he*=0.5#256
    boundaries=['left','right','bottom','top','front','back','box_left','box_right','box_top','box_front','box_back',]
    boundaryTags=dict([(key,i+1) for (i,key) in enumerate(boundaries)])
    bt = boundaryTags
    holes = [[0.5*box_L[0]+box_xy[0],0.5*box_L[1]+box_xy[1],0.5*box_L[2]]]
    vertices=[[0.0,0.0,0.0],#0
              [L[0],0.0,0.0],#1
              [L[0],L[1],0.0],#2
              [0.0,L[1],0.0],#3
              [0.0,0.0,L[2]],#4
              [L[0],0.0,L[2]],#5
              [L[0],L[1],L[2]],#6
              [0.0,L[1],L[2]],#7
              [box_xy[0],box_xy[1],0.0],#8
              [box_xy[0]+box_L[0],box_xy[1],0.0],#9
              [box_xy[0]+box_L[0],box_xy[1]+box_L[1],0.0],#10
              [box_xy[0],box_xy[1]+box_L[1],0.0],#11
              [box_xy[0],box_xy[1],box_L[2]],#12
              [box_xy[0]+box_L[0],box_xy[1],box_L[2]],#13
              [box_xy[0]+box_L[0],box_xy[1]+box_L[1],box_L[2]],#14
              [box_xy[0],box_xy[1]+box_L[1],box_L[2]]]#15
    vertexFlags=[boundaryTags['left'],
                 boundaryTags['right'],
                 boundaryTags['right'],
                 boundaryTags['left'],
                 boundaryTags['left'],
                 boundaryTags['right'],
                 boundaryTags['right'],
                 boundaryTags['left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left'],
                 boundaryTags['box_left']]
    facets=[[[0,1,2,3],[8,9,10,11]],
            [[0,1,5,4]],
            [[1,2,6,5]],
            [[2,3,7,6]],
            [[3,0,4,7]],
            [[4,5,6,7]],
            [[8,9,13,12]],
            [[9,10,14,13]],
            [[10,11,15,14]],
            [[11,8,12,15]],
            [[12,13,14,15]]]
    facetFlags=[boundaryTags['bottom'],
                boundaryTags['front'],
                boundaryTags['right'],
                boundaryTags['back'],
                boundaryTags['left'],
                boundaryTags['top'],
                boundaryTags['box_front'],
                boundaryTags['box_right'],
                boundaryTags['box_back'],
                boundaryTags['box_left'],
                boundaryTags['box_top']]
    domain = Domain.PiecewiseLinearComplexDomain(vertices=vertices,
                                                 vertexFlags=vertexFlags,
                                                 facets=facets,
                                                 facetFlags=facetFlags,
                                                 holes=holes)
						 
						 
    #go ahead and add a boundary tags member 
    domain.boundaryTags = boundaryTags
    domain.writePoly("mesh")
    domain.writePLY("mesh")
    domain.writeAsymptote("mesh")
    triangleOptions="VApq1.25q12feena%e" % ((he**3)/6.0,)
#logEvent("""Mesh generated using: tetgen -%s %s"""  % (triangleOptions,domain.polyfile+".poly"))
domain.MeshOptions.setParallelPartitioningType('node')
# Time stepping
T=0.45#6.0
dt_init  =0.001
dt_fixed = 0.005#0.1/Refinement
nDTout = int(round(T/dt_fixed))

# Numerical parameters
ns_forceStrongDirichlet = False#True
if useMetrics:
    ns_shockCapturingFactor  = 0.75
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = 0.75
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = 1.5
    vof_shockCapturingFactor = 0.75
    vof_lag_shockCapturing = True
    vof_sc_uref = 1.0
    vof_sc_beta = 1.5
    rd_shockCapturingFactor  = 0.75
    rd_lag_shockCapturing = False
    epsFact_density    = 1.5
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = 10.0
    redist_Newton = True
else:
    ns_shockCapturingFactor  = 0.9
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = 0.9
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = 1.0
    vof_shockCapturingFactor = 0.9
    vof_lag_shockCapturing = True
    vof_sc_uref  = 1.0
    vof_sc_beta  = 1.0
    rd_shockCapturingFactor  = 0.9
    rd_lag_shockCapturing = False
    epsFact_density    = 1.5
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = 10.0
    redist_Newton = False
    kappa_shockCapturingFactor = 0.9
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref  = 1.0
    kappa_sc_beta  = 1.0
    dissipation_shockCapturingFactor = 0.9
    dissipation_lag_shockCapturing = True#False
    dissipation_sc_uref  = 1.0
    dissipation_sc_beta  = 1.0

ns_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)
vof_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)
ls_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)
rd_nl_atol_res = max(1.0e-8,0.01*he)
mcorr_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)
kappa_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)
dissipation_nl_atol_res = max(1.0e-8,0.01*he**2/2.0)

#turbulence
ns_closure=0 #1-classic smagorinsky, 2-dynamic smagorinsky, 3 -- k-epsilon, 4 -- k-omega
if useRANS == 1:
    ns_closure = 3
elif useRANS == 2:
    ns_closure == 4
# Water
rho_0 = 998.2
nu_0  = 1.004e-6

# Air
rho_1 = 1.205
nu_1  = 1.500e-5 

# Surface tension
sigma_01 = 0.0

# Gravity
g = [0.0,0.0,-9.8]

# Initial condition
waterLine_x = 1.22
waterLine_z = 0.55

def signedDistance(x):
    phi_x = x[0]-waterLine_x
    phi_z = x[2]-waterLine_z 
    if phi_x < 0.0:
        if phi_z < 0.0:
            return max(phi_x,phi_z)
        else:
            return phi_z
    else:
        if phi_z < 0.0:
            return phi_x
        else:
            return sqrt(phi_x**2 + phi_z**2)



