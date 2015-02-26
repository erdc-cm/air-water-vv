from proteus import *
from redist_p import *
from proteus.default_n import *   
ct = Context.get()
triangleOptions = ct.triangleOptions
nLayersOfOverlapForParallel = ct.nLayersOfOverlapForParallel
parallelPartitioningType=ct.parallelPartitioningType
nLevels = ct.nLevels
elementQuadrature=ct.elementQuadrature
elementBoundaryQuadrature=ct.elementBoundaryQuadrature

nl_atol_res = ct.rd_nl_atol_res
tolFac = 0.0
nl_atol_res = ct.rd_nl_atol_res

linTolFac = 0.01
l_atol_res = 0.01*ct.rd_nl_atol_res

if ct.redist_Newton:
    timeIntegration = NoIntegration
    stepController = Newton_controller
    maxNonlinearIts = 50
    maxLineSearches = 0
    nonlinearSolverConvergenceTest = 'r'
    levelNonlinearSolverConvergenceTest = 'r'
    linearSolverConvergenceTest = 'r-true'
    useEisenstatWalker = False
else:
    timeIntegration = BackwardEuler_cfl
    stepController = RDLS.PsiTC
    runCFL=2.0
    psitc['nStepsForce']=3
    psitc['nStepsMax']=50
    psitc['reduceRatio']=2.0
    psitc['startRatio']=1.0
    rtol_res[0] = 0.0
    atol_res[0] = ct.rd_nl_atol_res
    useEisenstatWalker = False
    maxNonlinearIts = 1
    maxLineSearches = 0
    nonlinearSolverConvergenceTest = 'rits'
    levelNonlinearSolverConvergenceTest = 'rits'
    linearSolverConvergenceTest = 'r-true'

femSpaces = {0:ct.basis}
       
massLumping       = False
numericalFluxType = DoNothing    
conservativeFlux  = None
subgridError      = RDLS.SubgridError(coefficients,nd)
shockCapturing    = RDLS.ShockCapturing(coefficients,nd,shockCapturingFactor=ct.rd_shockCapturingFactor,lag=ct.rd_lag_shockCapturing)

fullNewtonFlag = True
multilevelNonlinearSolver  = Newton
levelNonlinearSolver       = Newton

nonlinearSmoother = NLGaussSeidel
linearSmoother    = None

matrix = SparseMatrix

if ct.useOldPETSc:
    multilevelLinearSolver = PETSc
    levelLinearSolver      = PETSc
else:
    multilevelLinearSolver = KSP_petsc4py
    levelLinearSolver      = KSP_petsc4py

if ct.useSuperlu:
    multilevelLinearSolver = LU
    levelLinearSolver      = LU

linear_solver_options_prefix = 'rdls_'

