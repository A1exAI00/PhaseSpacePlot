from scipy.optimize import fsolve
from scipy.differentiate import jacobian
from scipy.linalg import eig

def solve(ODEs, x0, pars):
    res = fsolve(lambda x: ODEs(x, pars, 0.0), x0, full_output=True)
    return (res[0], res[2]==1)

def eigenvalues_and_eigenvectors(ODEs, x0, pars):
    _jacobian = jacobian(lambda x: ODEs(x, pars, 0.0), x0).df
    res = eig(_jacobian)
    return (res[0], res[1])