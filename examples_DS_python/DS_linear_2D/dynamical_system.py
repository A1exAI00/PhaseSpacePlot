variable_names = ["x", "y"]
parameter_names = ["a", "b", "c", "d"]
time = "t"

def ODEs(U, p, t):
    x, y = U
    a, b, c, d = p
    return [a * x + b * y, 
            c * x + d * y]