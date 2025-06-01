import numpy as np
from scipy.integrate import solve_ivp

def euler_integrate(ODEs, U0, p, t, dt):
    sol = []
    t_sol = []
    sol.append(U0)
    curr_t = 0.0
    t_sol.append(0.0)
    while curr_t < t:
        dU = ODEs(sol[-1], p, t)
        dU = [_dU*dt for _dU in dU]
        sol.append([sol[-1][i]+dU[i] for i in range(len(U0))])
        t_sol.append(t_sol[-1]+dt)
        curr_t += dt
    return (sol, t_sol)

#########################################################################################

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
