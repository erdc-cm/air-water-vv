from proteus import *
from proteus.default_p import *
from tank import *
from proteus.mprans import RANS3PF
from proteus import Context
import tank_so

ct = Context.get()

LevelModelType = RANS3PF.LevelModel

if useRANS >= 1:
    Closure_0_model = 5; Closure_1_model=6
    if useOnlyVF:
        Closure_0_model=2; Closure_1_model=3
    if movingDomain:
        Closure_0_model += 1; Closure_1_model += 1
else:
    Closure_0_model = None
    Closure_1_model = None

coefficients = RANS3PF.Coefficients(epsFact=epsFact_viscosity,
                                    sigma=0.0,
                                    rho_0 = rho_0,
                                    nu_0 = nu_0,
                                    rho_1 = rho_1,
                                    nu_1 = nu_1,
                                    g=g,
                                    nd=nd,
                                    ME_model=tank_so.FLOW_model,
                                    PRESSURE_model=tank_so.P_model,
                                    SED_model=tank_so.SED_model,
                                    VOF_model=tank_so.VOF_model,
                                    VOS_model=tank_so.VOS_model,
                                    LS_model=tank_so.NCLS_model,
                                    Closure_0_model=Closure_0_model,
                                    Closure_1_model=Closure_1_model,
                                    epsFact_density=epsFact_density,
                                    stokes=False,
                                    useVF=useVF,
                                    useRBLES=useRBLES,
                                    useMetrics=useMetrics,
                                    eb_adjoint_sigma=1.0,
                                    eb_penalty_constant=weak_bc_penalty_constant,
                                    forceStrongDirichlet=ns_forceStrongDirichlet,
                                    turbulenceClosureModel=ns_closure,
                                    movingDomain=movingDomain,
                                    dragAlpha=dragAlpha,
                                    PSTAB=ct.opts.PSTAB,
                                    CORRECT_VELOCITY=ct.CORRECT_VELOCITY,
                                    aDarcy = sedClosure.aDarcy,
                                    betaForch = sedClosure.betaForch,
                                    grain = sedClosure.grain,
                                    packFraction = sedClosure.packFraction,
                                    maxFraction = sedClosure.maxFraction,
                                    frFraction = sedClosure.frFraction,
                                    sigmaC = sedClosure.sigmaC,
                                    C3e = sedClosure.C3e,
                                    C4e = sedClosure.C4e,
                                    eR = sedClosure.eR,
                                    fContact = sedClosure.fContact,
                                    mContact = sedClosure.mContact,
                                    nContact = sedClosure.nContact,
                                    angFriction = sedClosure.angFriction,
                                    nParticles=0)

dirichletConditions = {0: lambda x, flag: domain.bc[flag].u_dirichlet.init_cython(),
                       1: lambda x, flag: domain.bc[flag].v_dirichlet.init_cython()}

advectiveFluxBoundaryConditions = {0: lambda x, flag: domain.bc[flag].u_advective.init_cython(),
                                   1: lambda x, flag: domain.bc[flag].v_advective.init_cython()}

diffusiveFluxBoundaryConditions = {0: {0: lambda x, flag: domain.bc[flag].u_diffusive.init_cython()},
                                   1: {1: lambda x, flag: domain.bc[flag].v_diffusive.init_cython()}}

if nd == 3:
    dirichletConditions[2] = lambda x, flag: domain.bc[flag].w_dirichlet.init_cython()
    advectiveFluxBoundaryConditions[2] = lambda x, flag: domain.bc[flag].w_advective.init_cython()
    diffusiveFluxBoundaryConditions[2] = {2: lambda x, flag: domain.bc[flag].w_diffusive.init_cython()}

class AtRest:
    def __init__(self):
        pass
    def uOfXT(self,x,t):
        return 0.0

initialConditions = {0:AtRest(),
                     1:AtRest()}
