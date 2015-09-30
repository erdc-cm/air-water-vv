from proteus import *
from proteus.default_p import *
from tank3D import *
from proteus.mprans import NCLS

LevelModelType = NCLS.LevelModel

coefficients = NCLS.Coefficients(V_model=0,RD_model=3,ME_model=2,
                                 checkMass=False, useMetrics=useMetrics,
                                 epsFact=epsFact_consrv_heaviside,sc_uref=ls_sc_uref,sc_beta=ls_sc_beta,movingDomain=movingDomain)

def getDBC_ls(x,flag):
    if flag == boundaryTags['left']:
        return wavePhi
#    elif flag == boundaryTags['right']:
#        return  outflowPhi
    else:
        return None

dirichletConditions = {0:getDBC_ls}

advectiveFluxBoundaryConditions =  {}
diffusiveFluxBoundaryConditions = {0:{}}

class PerturbedSurface_phi:
    def uOfXT(self,x,t):
        return signedDistance(x)#wavePhi(x,t)

initialConditions  = {0:PerturbedSurface_phi()}