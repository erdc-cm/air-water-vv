from math import *
import proteus.MeshTools
from proteus import Domain
from proteus.default_n import *   
from proteus.Profiling import logEvent

from proteus import Context
#===============================================================================
# Context
#===============================================================================
ct = Context.Options([
    ("H",                       4,"height of the domain is ct.H*D"),
    ("parallel",                False,"Use parallel or not"),
    ###############################################
    ("T",                       1.0,"Time interval [0, T]"),
    ("Refinement",              5, "Specify initial mesh size by giving number of cells in each direction"),
    ("use_TaylorHood",          1, "True or false"),
    ("only_vof",                0, "without LS, RD and MC"),
    ###############################################
    ("use_supg",                1.0,"Use supg or not"),
    ("use_gmsh",                0,"use gmsh generated .ele .node .edge files"),
    ("spaceOrder",              1,"FE space for velocity"),
    ("forceStrongDirichlet",    False,"strong or weak"),
], mutable=True)

#===============================================================================
# Parameters
#===============================================================================
use_supg = ct.use_supg
Refinement = ct.Refinement
genMesh=True
movingDomain=False
useOldPETSc=False
useSuperlu=True
if ct.parallel:
   usePETSc = True
   useSuperlu=False
else:
   usePETSc = False

timeDiscretization='be'#'vbdf'#'be','flcbdf'
spaceOrder = ct.spaceOrder
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
useVF = 1.0
useRANS = 0 # 0 -- None
            # 1 -- K-Epsilon
            # 2 -- K-Omega
gatherAtClose=True
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
    
#===============================================================================
# FE space
#===============================================================================
nd = 2

if spaceOrder == 1:
    hFactor = 1.0
    if useHex:
        basis = C0_AffineLinearOnCubeWithNodalBasis
        elementQuadrature = CubeGaussQuadrature(nd, 2)
        elementBoundaryQuadrature = CubeGaussQuadrature(nd - 1, 2)
    else:
        basis = C0_AffineLinearOnSimplexWithNodalBasis
        elementQuadrature = SimplexGaussQuadrature(nd, 3)
        elementBoundaryQuadrature = SimplexGaussQuadrature(nd - 1, 3)
elif spaceOrder == 2:
    hFactor = 0.5
    if useHex:
        basis = C0_AffineLagrangeOnCubeWithNodalBasis
        elementQuadrature = CubeGaussQuadrature(nd, 4)
        elementBoundaryQuadrature = CubeGaussQuadrature(nd - 1, 4)
    else:
        basis = C0_AffineQuadraticOnSimplexWithNodalBasis
        elementQuadrature = SimplexGaussQuadrature(nd, 5)
        elementBoundaryQuadrature = SimplexGaussQuadrature(nd - 1, 5)
basis_p = basis
basis_v = basis
if ct.use_TaylorHood:
    basis = C0_AffineLinearOnSimplexWithNodalBasis
    basis_p = basis
    basis_v = C0_AffineQuadraticOnSimplexWithNodalBasis
    elementQuadrature = SimplexGaussQuadrature(nd, 5)
    elementBoundaryQuadrature = SimplexGaussQuadrature(nd - 1, 5)

# Domain and mesh
D = 0.146
L = (4*D, ct.H*D)
he = L[0]/float(2**Refinement+1)

weak_bc_penalty_constant = 100.0
nLevels = 1
parallelPartitioningType = proteus.MeshTools.MeshParallelPartitioningTypes.node
nLayersOfOverlapForParallel = 0


structured =False 
use_gmsh = ct.use_gmsh
if use_gmsh:
    domain = Domain.PlanarStraightLineGraphDomain()
    genMesh = False
    domain.use_gmsh = True
    domain.geofile = "my_mesh"

    boundaries = ['bottom', 'right', 'top', 'left', 'front', 'back']
    boundaryTags = dict([(key, i + 1) for (i, key) in enumerate(boundaries)])
    ##TODO: how to get h to compute fixed dt?
else:
    if useHex:
        nnx = 4 * Refinement + 1
        nny = 2 * Refinement + 1
        hex = True
        domain = Domain.RectangularDomain(L)
    else:
        boundaries = ['bottom', 'right', 'top', 'left', 'front', 'back']
        boundaryTags = dict([(key, i + 1) for (i, key) in enumerate(boundaries)])
        if structured:
            N = 2**Refinement+1
            nnx = int(L[0]/D)*N
            nny = int(L[1]/D)*N
            triangleFlag=1
            domain = Domain.RectangularDomain(L=[L[0],L[1]])
        else:
            vertices = [[0.0, 0.0],  #0
                        [L[0], 0.0],  #1
                        [L[0], L[1]],  #2
                        [0.0, L[1]],  #3
                        # [0.2-0.16,L[1]*0.2],
                        # [0.2-0.16,L[1]*0.8],
                        # [0.2+0.3,L[1]*0.8],
                        # [0.2+0.3,L[1]*0.2],
                        # # the following are set for refining the mesh
                        # [0.2-0.06,0.2-0.06],
                        # [0.2-0.06,0.2+0.06],
                        # [0.2+0.1,0.2+0.06],
                        # [0.2+0.1,0.2-0.06],
                        ]

                        
                        
            vertexFlags = [boundaryTags['bottom'],
                        boundaryTags['bottom'],
                        boundaryTags['top'],
                        boundaryTags['top'],
                        # the interior vertices should be flaged to 0
                        #    0, 0, 0, 0,
                        #    0, 0, 0, 0,
                            ]

            segments = [[0, 1],
                        [1, 2],
                        [2, 3],
                        [3, 0],
                        #Interior segments
                        # [4, 5],
                        # [5, 6],
                        # [6, 7],
                        # [7,4],
                        # [8,9],
                        # [9,10],
                        # [10,11],
                        # [11,8],
                        ]
            segmentFlags = [boundaryTags['bottom'],
                            boundaryTags['right'],
                            boundaryTags['top'],
                            boundaryTags['left'],
                            # 0,
                            # 0,
                            # 0,
                            # 0,
                            # 0,
                            # 0,
                            # 0,
                            # 0,
                            ]

            regions = [
                        [0.95*L[0], 0.2],
                        # [0.2-0.15,0.2],[0.2,0.2],
                        ]
            regionFlags = [1,
                            #2,3,
                            ]
            regionConstraints=[0.5*he**2,
                            #0.5*(he/2.0)**2,0.5*(he/6.0)**2
                            ]
            domain = Domain.PlanarStraightLineGraphDomain(vertices=vertices,
                                                        vertexFlags=vertexFlags,
                                                        segments=segments,
                                                        segmentFlags=segmentFlags,
                                                        regions=regions,
                                                        regionFlags=regionFlags,
                                                        regionConstraints=regionConstraints)
            #go ahead and add a boundary tags member
            domain.boundaryTags = boundaryTags
            domain.writePoly("mesh")
            domain.writePLY("mesh")
            domain.writeAsymptote("mesh")
            #triangleOptions = "VApq30Dena%8.8f" % ((he ** 2) / 2.0,)
            triangleOptions = "KkVApq30Dena"
            logEvent("""Mesh generated using: tetgen -%s %s""" % (triangleOptions, domain.polyfile + ".poly"))

# Time stepping
T=ct.T
dt_fixed = he/5.0
dt_init = min(0.1*dt_fixed,0.1*he)
runCFL=0.1
nDTout = int(T/dt_fixed)

# Numerical parameters
ns_forceStrongDirichlet = ct.forceStrongDirichlet 
if useMetrics:
    ns_shockCapturingFactor  = 0.25
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
    epsFact_consrv_diffusion = 0.1
    redist_Newton = False#True
    kappa_shockCapturingFactor = 0.25
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref = 1.0
    kappa_sc_beta = 1.0
    dissipation_shockCapturingFactor = 0.25
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
    epsFact_consrv_diffusion = 1.0
    redist_Newton = False
    kappa_shockCapturingFactor = 0.9
    kappa_lag_shockCapturing = True#False
    kappa_sc_uref  = 1.0
    kappa_sc_beta  = 1.0
    dissipation_shockCapturingFactor = 0.9
    dissipation_lag_shockCapturing = True#False
    dissipation_sc_uref  = 1.0
    dissipation_sc_beta  = 1.0

ns_nl_atol_res = max(1.0e-8,0.001*he**2)
vof_nl_atol_res = max(1.0e-8,0.001*he**2)
ls_nl_atol_res = max(1.0e-8,0.001*he**2)
rd_nl_atol_res = max(1.0e-8,0.005*he)
mcorr_nl_atol_res = max(1.0e-8,0.001*he**2)
kappa_nl_atol_res = max(1.0e-8,0.001*he**2)
dissipation_nl_atol_res = max(1.0e-8,0.001*he**2)

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
g = [0.0,-9.8]

# Initial condition
waterLine_x = D
waterLine_z = 2*D

def signedDistance(x):
    phi_x = x[0]-waterLine_x
    phi_z = x[1]-waterLine_z 
    if x[0] < waterLine_x:
        if x[1] < waterLine_z:
            return max(phi_x,phi_z) ## negative = fluid domain
        else:
            return phi_z
    else:
        if phi_z < 0.0:
            return phi_x
        else:
            return sqrt(phi_x**2 + phi_z**2)

particle_sdfList = []
particle_velocityList = []

def p1_sdf(t, x):
    cx = L[0]
    cy = 0.0
    r = math.sqrt( (x[0]-cx)**2 + (x[1]-cy)**2) + 1e-10
    n = ((x[0]-cx)/r,(x[1]-cy)/r,0.0)
    return  r - D,n

def p1_vel(t, x):
    return (0.0,0.0,0.0)

use_ball_as_particle = 0
nParticles = 1
particle_sdfList = [p1_sdf]
particle_velocityList = [p1_vel]
