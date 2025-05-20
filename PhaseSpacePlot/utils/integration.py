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