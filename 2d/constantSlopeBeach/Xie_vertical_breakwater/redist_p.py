from proteus.default_p import *
from proteus.mprans import RDLS
from proteus import Context

"""
The redistancing equation in the sloshbox test problem.
"""

ct = Context.get()
domain = ct.domain
nd = domain.nd
mesh = domain.MeshOptions
genMesh = mesh.genMesh
movingDomain = ct.movingDomain
T = ct.T

LevelModelType = RDLS.LevelModel

coefficients = RDLS.Coefficients(applyRedistancing=ct.applyRedistancing,
                                 epsFact=ct.epsFact_redistance,
                                 nModelId=int(movingDomain) + 2,
                                 rdModelId=int(movingDomain) + 3,
                                 useMetrics=ct.useMetrics)

def getDBC_rd(x,flag):
    pass
    
dirichletConditions     = {0:getDBC_rd}
weakDirichletConditions = {0:RDLS.setZeroLSweakDirichletBCsSimple}

advectiveFluxBoundaryConditions =  {}
diffusiveFluxBoundaryConditions = {0:{}}

class PerturbedSurface_phi:       
    def uOfXT(self,x,t):
        return ct.signedDistance(x)
    
initialConditions  = {0:PerturbedSurface_phi()}
