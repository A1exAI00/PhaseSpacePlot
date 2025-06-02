from numpy import sin

variable_names = ["p1", "p2"]
parameter_names = ["g1", "g2", "k", "d"]
time = "t"

def ODEs(U, p, t):
    p1, p2 = U
    g1, g2, k, d = p
    return [g1 - sin(p1) - k * sin(p2), 
            g2 - sin(p2) - d * sin(p1)]