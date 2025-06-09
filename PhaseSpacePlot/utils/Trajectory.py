import numpy as np
from scipy.integrate import solve_ivp

class Trajectory():
    def __init__(self, alg:str="RK45", rtol:float=1e-5, atol:float=1e-5) -> None:
        self._alg:str = alg
        self._rtol:float = rtol
        self._atol:float = atol

        self.sol = None
        self.t_sol = None
        return
    
    def get_sol(self): # TODO refactor gui files to use this
        return self.sol
    
    def get_t_sol(self): # TODO refactor gui files to use this
        return self.t_sol
    
    def _set_sol(self, sol):
        self.sol = sol
        return
    
    def _set_t_sol(self, t_sol):
        self.t_sol = t_sol
        return
    
    def get_init_state(self): # NOTE this should not be used in gui files, USE init state from GUI inputs
        return np.array([sol_i[0] for sol_i in self.sol])
    
    def get_last_state(self): # TODO refactor gui files to use this
        return np.array([sol_i[-1] for sol_i in self.sol])
    
    def integrate_scipy(self, ODEs, init_state, pars, t_start, t_end, t_N):
        t_span = (t_start, t_end)
        t_eval = np.arange(t_start, t_end, (t_end-t_start)/t_N)
        sol = solve_ivp(lambda t, U0: ODEs(U0, np.array(pars), t), 
                    t_span=t_span, 
                    y0=init_state, 
                    t_eval=t_eval, 
                    method=self._alg, 
                    rtol=self._rtol, 
                    atol=self._atol)
        self._set_sol(sol.y)
        self._set_t_sol(sol.t)
        return
