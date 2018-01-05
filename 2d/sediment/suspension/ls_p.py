from proteus import StepControl
from proteus import *
from proteus.default_p import *
from proteus.mprans import NCLS3P
from proteus import Context

ct = Context.get()
domain = ct.domain
nd = ct.domain.nd
mesh = domain.MeshOptions


genMesh = mesh.genMesh
movingDomain = ct.movingDomain
T = ct.T

LevelModelType = NCLS3P.LevelModel

if ct.sedimentDynamics:
    LS_model=2
    RD_model=3
    V_model=6
else:
    LS_model=1
    RD_model=2
    V_model=4

coefficients = NCLS3P.Coefficients(V_model=V_model,
                                   RD_model=RD_model,
                                   ME_model=LS_model,
                                   checkMass=False,
                                   useMetrics=ct.useMetrics,
                                   epsFact=ct.epsFact_consrv_heaviside,
                                   sc_uref=ct.ls_sc_uref,
                                   sc_beta=ct.ls_sc_beta,
                                   movingDomain=ct.movingDomain)

dirichletConditions = {0: lambda x, flag: None}

advectiveFluxBoundaryConditions = {}

diffusiveFluxBoundaryConditions = {0: {}}

class PHI_IC:
    def uOfXT(self, x, t):
        return x[nd-1] - ct.waterLevel

initialConditions = {0: PHI_IC()}
