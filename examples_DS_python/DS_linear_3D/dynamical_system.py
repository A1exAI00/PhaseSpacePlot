variable_names = ["x", "y", "z"]
parameter_names = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
time = "t"

def ODEs(U, p, t):
    x, y, z = U
    a, b, c, d, e, f, g, h, i = p
    return [a * x + b * y + c * z, 
            d * x + i * y + f * z,
            g * x + h * y + i * z]