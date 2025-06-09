import numpy as np
from scipy.integrate import solve_ivp

class Trajectory():
    def __init__(self):
        self.sol = None
        self.t_sol = None
        self.alg = "RK45"
        self.rtol = 1e-5
        self.atol = 1e-5
        return
    
    def integrate_scipy(self, ODEs, init_state, pars, t_start, t_end, t_N):
        t_span = (t_start, t_end)
        t_eval = np.arange(t_start, t_end, (t_end-t_start)/t_N)
        sol = solve_ivp(lambda t, U0: ODEs(U0, np.array(pars), t), 
                    t_span=t_span, 
                    y0=init_state, 
                    t_eval=t_eval, 
                    method=self.alg, 
                    rtol=self.rtol, 
                    atol=self.atol)
        self.sol = sol.y
        self.t_sol = sol.t
        return
