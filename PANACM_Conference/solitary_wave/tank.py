from math import *
import proteus.MeshTools
from proteus import Domain
from proteus.default_n import *   
from proteus.Profiling import logEvent
from proteus.ctransportCoefficients import smoothedHeaviside
from proteus.ctransportCoefficients import smoothedHeaviside_integral
#wave generator
windVelocity = (0.0,0.0)
inflowHeightMean = 1.0
inflowVelocityMean = (0.0,0.0)
#period = 1.94
#omega = 2.0*math.pi/period
waveheight = 0.05
amplitude = waveheight/ 2.0
#wavelength = 5.0
k = sqrt(3.0*waveheight/(4.0*inflowHeightMean**3.0))
   
#  Discretization -- input options  
genMesh=True
movingDomain=False
applyRedistancing=True
useOldPETSc=False
useSuperlu=False
timeDiscretization='be'#'vbdf'#'be','flcbdf'
spaceOrder = 1
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
applyCorrection=True
useVF = 1.0
useOnlyVF = False
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
nd = 2
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

#for debugging, make the tank short
L = (60.0,2.0)
he = L[0]/1200 #try this first


weak_bc_penalty_constant = 100.0
nLevels = 1
#parallelPartitioningType = proteus.MeshTools.MeshParallelPartitioningTypes.element
parallelPartitioningType = proteus.MeshTools.MeshParallelPartitioningTypes.node
nLayersOfOverlapForParallel = 0
structured=False
if useHex:   
    nnx=ceil(L[0]/he)+1
    nny=ceil(L[1]/he)+1
    hex=True    
    domain = Domain.RectangularDomain(L)
else:
    boundaries=['left','right','bottom','top','front','back']
    boundaryTags=dict([(key,i+1) for (i,key) in enumerate(boundaries)])
    if structured:
        nnx=ceil(L[0]/he)+1
        nny=ceil(L[1]/he)+1
    else:
        vertices=[[0.0,0.0],#0
                  [L[0],0.0],#1
                  [L[0],L[1]],#2
                  [0.0,L[1]]]#3

        vertexFlags=[boundaryTags['bottom'],
                     boundaryTags['bottom'],
                     boundaryTags['top'],  
                     boundaryTags['top']]
        segments=[[0,1],
                  [1,2],
                  [2,3],  
                  [3,0]
                  ]
        segmentFlags=[boundaryTags['bottom'],
                      boundaryTags['right'],
                      boundaryTags['top'],
                      boundaryTags['left']]

        regions=[ [ 0.1*L[0] , 0.1*L[1] ],
                  [0.95*L[0] , 0.95*L[1] ] ]
        regionFlags=[1,2]
        domain = Domain.PlanarStraightLineGraphDomain(vertices=vertices,
                                                      vertexFlags=vertexFlags,
                                                      segments=segments,
                                                      segmentFlags=segmentFlags,
                                                      regions=regions,
                                                      regionFlags=regionFlags)
        #go ahead and add a boundary tags member 
        domain.boundaryTags = boundaryTags
        domain.writePoly("mesh")
        domain.writePLY("mesh")
        domain.writeAsymptote("mesh")
        triangleOptions="VApq30Dena%8.8f" % ((he**2)/2.0,)

        logEvent("""Mesh generated using: tetgen -%s %s"""  % (triangleOptions,domain.polyfile+".poly"))
# Time stepping
T=60.0
dt_fixed = 0.2
dt_init = min(0.1*dt_fixed,0.001)
runCFL=0.9
nDTout = int(round(T/dt_fixed))

# Numerical parameters
ns_forceStrongDirichlet = False#True
backgroundDiffusionFactor=0.01
if useMetrics:
    ns_shockCapturingFactor  = 0.5
    ns_lag_shockCapturing = True
    ns_lag_subgridError = True
    ls_shockCapturingFactor  = 0.25
    ls_lag_shockCapturing = True
    ls_sc_uref  = 1.0
    ls_sc_beta  = 1.0
    vof_shockCapturingFactor = 0.25
    vof_lag_shockCapturing = True
    vof_sc_uref = 1.0
    vof_sc_beta = 1.0
    rd_shockCapturingFactor  = 0.25
    rd_lag_shockCapturing = False
    epsFact_density    = 3.0
    epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
    epsFact_redistance = 0.33
    epsFact_consrv_diffusion = 1.0
    redist_Newton = False
    kappa_shockCapturingFactor = 0.1
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref = 1.0
    kappa_sc_beta = 1.0
    dissipation_shockCapturingFactor = 0.1
    dissipation_lag_shockCapturing = True#False
    dissipation_sc_uref = 1.0
    dissipation_sc_beta = 1.0
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

ns_nl_atol_res = max(1.0e-10,0.001*he**2)
vof_nl_atol_res = max(1.0e-10,0.001*he**2)
ls_nl_atol_res = max(1.0e-10,0.001*he**2)
rd_nl_atol_res = max(1.0e-10,0.005*he)
mcorr_nl_atol_res = max(1.0e-10,0.001*he**2)
kappa_nl_atol_res = max(1.0e-10,0.001*he**2)
dissipation_nl_atol_res = max(1.0e-10,0.001*he**2)

#turbulence
ns_closure=2 #1-classic smagorinsky, 2-dynamic smagorinsky, 3 -- k-epsilon, 4 -- k-omega
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
g = [0.0,-9.8]

# Initial condition
waterLine_x = 2*L[0]
waterLine_z = inflowHeightMean
#waterLine_x = 0.5*L[0]
#waterLine_z = 0.9*L[1]

trans=10

def signedDistance(x):
    try :
      a0=cosh(k*(x[0]+trans))
    except Exception:
      a0=1e300
    try :
      eta= waveheight/(a0)**2.0 + inflowHeightMean
    except Exception:
      eta=1e-300
 
    phi_x = x[0]-waterLine_x
    phi_z = x[1]-eta
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

def z(x):
    return x[1] - inflowHeightMean

h = inflowHeightMean # - transect[0][1] if lower left hand corner is not at z=0
H_w= waveheight
celerity = sqrt(abs(g[1])*(waveheight+inflowHeightMean))

def waveHeight(x,t):
   try :
      a0=cosh(k*(celerity * t - (x[0]+trans)))
   except Exception:
      a0=1e300
  
   try :
      eta= waveheight/(a0)**2.0 + inflowHeightMean
   except Exception:
      eta=1e-300

   return eta 


def waveVelocity_u(x,t):
    try :
      a1=cosh(sqrt( 3.0 * H_w / h**3.0) * (celerity  * t - (x[0]+trans)))
    except Exception:
      a1=1e300

    try :
      a2=cosh(k*(celerity * t - (x[0]+trans)))
    except Exception:
      a2=1e300
    
    try :
      Uhorz =  1.0 /(4.0 * h**4 ) * sqrt(abs(g[1]) * h) *  H_w  * (             
               2.0 * h**3 + h**2 * H_w  + 12.0 * h * H_w * z(x) + 6.0 *  H_w * z(x)**2.0 +
              (2.0 * h**3 - h**2 * H_w - 6.0 * h * H_w * z(x) - 3.0 * H_w * z(x)**2 ) * a1)/(a2)**4
    except Exception:
      Uhorz=1e-300

    return Uhorz


def waveVelocity_v(x,t):
    try:
      Uvert =   1.0 / ( 4.0 * sqrt( abs(g[1])* h) ) * sqrt(3.0) * abs(g[1]) * (H_w / h**3.0)** 1.5  * (h + z(x))*(
                2.0 * h**3 - 7.0 * h**2.0 * H_w + 10.0 * h * H_w * z(x) + 5.0 * H_w * z(x)**2.0 +
                (2.0 * h**3.0 + h**2.0 * H_w - 2.0 * h * H_w * z(x) - H_w * z(x)**2.0)*
                cosh(sqrt( 3.0 * H_w / h**3.0) * (celerity * t - (x[0]+trans) )))/(
                cosh(sqrt( 3.0 * H_w / ( 4.0 * h**3.0))*
                (celerity * t - (x[0]+trans)))   )** 4.0*( 
                tanh( sqrt( 3.0 * H_w / ( 4.0 * h**3.0))*(celerity * t - (x[0]+trans))))
    except Exception:
      Uvert=1e-300    

    return -Uvert

#solution variables

def wavePhi(x,t):
    return x[1] - waveHeight(x,t)

def waveVF(x,t):
    return smoothedHeaviside(epsFact_consrv_heaviside*he,wavePhi(x,t))

def twpflowVelocity_u(x,t):
    waterspeed = waveVelocity_u(x,t)
    H = smoothedHeaviside(epsFact_consrv_heaviside*he,wavePhi(x,t)-epsFact_consrv_heaviside*he)
    u = H*windVelocity[0] + (1.0-H)*waterspeed
    return u

def twpflowVelocity_v(x,t):
    waterspeed = 0.0
    H = smoothedHeaviside(epsFact_consrv_heaviside*he,wavePhi(x,t)-epsFact_consrv_heaviside*he)
    return H*windVelocity[1]+(1.0-H)*waterspeed

def twpflowFlux(x,t):
    return -twpflowVelocity_u(x,t)

def outflowVF(x,t):
    return smoothedHeaviside(epsFact_consrv_heaviside*he,x[1] - outflowHeight)
