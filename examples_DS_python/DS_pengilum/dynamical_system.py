from numpy import sin

variable_names = ["phi", "y"]
parameter_names = ["g", "mu"]
time = "t"

def ODEs(U, p, t):
    phi, y = U
    g, mu = p
    return [y, g - mu*y - sin(phi)]