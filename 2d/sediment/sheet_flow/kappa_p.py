from proteus import *
from proteus.default_p import *
from tank import *
from proteus.mprans import Kappa
from proteus import Context
import sheetflowBC as sfbc

ct = Context.get()

LevelModelType = Kappa.LevelModel

dissipation_model_flag = 1
if ct.useRANS >= 2:
    dissipation_model_flag=2

coefficients = Kappa.Coefficients(V_model=ct.V_model,
                                  ME_model=ct.K_model,
                                  LS_model=ct.LS_model,
                                  RD_model=ct.RD_model,
                                  dissipation_model=ct.EPS_model,
                                  SED_model=ct.SED_model,
                                  dissipation_model_flag=dissipation_model_flag+int(ct.movingDomain),#1 -- K-epsilon, 2 -- K-omega
                                  useMetrics=useMetrics,
                                  rho_0=rho_0,nu_0=nu_0,
                                  rho_1=rho_1,nu_1=nu_1,
                                  g=g,
                                  nd = ct.nd,
                                  c_mu=ct.opts.Cmu,sigma_k=ct.opts.sigma_k, 
                                  sc_uref=kappa_sc_uref,
                                  sc_beta=kappa_sc_beta,
                                  closure = ct.sedClosure)

kInflow=ct.kInflow

manualbc = ct.manualbc
if manualbc == True:
	parallelPeriodic=sfbc.kapp_parallelPeriodic
	periodicDirichletConditions 	= sfbc.kapp_periodic
	dirichletConditions 			= sfbc.kapp_dirichlet
	advectiveFluxBoundaryConditions = sfbc.kapp_advective
	diffusiveFluxBoundaryConditions = sfbc.kapp_diffusive
else:
	dirichletConditions = {0: lambda x, flag: domain.bc[flag].k_dirichlet.init_cython()}
	advectiveFluxBoundaryConditions = {0: lambda x, flag: domain.bc[flag].k_advective.init_cython()}
	diffusiveFluxBoundaryConditions = {0: {},
    	                               1: {1: lambda x, flag: domain.bc[flag].k_diffusive.init_cython()}}

class ConstantIC:
    def __init__(self,cval=0.0):
        self.cval=cval
    def uOfXT(self,x,t):
        return self.cval

   
initialConditions  = {0:ConstantIC(cval=kInflow)}
