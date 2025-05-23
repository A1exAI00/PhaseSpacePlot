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

def scipy_integrate(ODEs, U0, p, t_start, t_end, dt):
    import numpy as np
    from scipy.integrate import solve_ivp

    sol = solve_ivp(lambda t, U0: ODEs(U0, np.array(p), t), 
                    t_span=(t_start, t_end), 
                    y0=U0, 
                    t_eval=np.arange(t_start, t_end, dt), 
                    method="RK45", 
                    rtol = 1e-5, atol = 1e-5)
    return (sol.y, sol.t)
