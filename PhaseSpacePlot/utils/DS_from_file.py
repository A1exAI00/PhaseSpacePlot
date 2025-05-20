# def unpack_kwarg(kwargs, kwarg_key, default):
#     if kwarg_key not in kwargs.keys(): 
#         return kwargs[kwarg_key]
#     else:
#         return default

def load_DS_from_file(file_path, **kwargs):

    # Markers that define variables, parameters, equations and equation index brackets 
    var_marker = "var"
    par_marker = "par"
    eq_marker = "F"
    eq_open_bracket = "["
    eq_close_bracket = "]"

    # A temporary placeholder for equation string
    empty_eq_placeholder = "empty_eq"


    with open(file_path, "r") as file:
        lines = file.readlines()

    vars_str = ""
    pars_str = ""
    vars_found = False
    pars_found = False

    for line in lines:
        if var_marker in line:
            vars_str = (line[len(var_marker):-1]).replace(" ", "")
            vars_found = True
        elif par_marker in line:
            pars_str = (line[len(par_marker):-1]).replace(" ", "")
            pars_found = True
    
    if not vars_found:
        raise RuntimeError(f"Variables not found in '{file_path}'. Check if '{var_marker}' is included.")
    if not pars_found:
        raise RuntimeError(f"Parameters not found in '{file_path}'. Check if '{par_marker}' is included.")

    # Split string with a comma as a separator
    vars_names = vars_str.split(",")
    pars_names = pars_str.split(",")
    vars_N = len(vars_names)
    pars_N = len(pars_names)
    
    # Find lines in DYNSYS_FILE that define equations
    equations = [empty_eq_placeholder for _ in range(vars_N)]
    for line in lines:
        if eq_marker in line:

            if eq_open_bracket not in line:
                raise RuntimeError(f"Open bracket '{eq_open_bracket}' in not found in '{file_path}' at line '{line[0:-1]}'.")
            if eq_close_bracket not in line:
                raise RuntimeError(f"Close bracket '{eq_close_bracket}' in not found in '{file_path}' at line '{line[0:-1]}'.")
            
            # Extract string with an integer between eq_open_bracket and eq_close_bracket
            str_with_integer = (line[line.find("[")+1:line.find("]")]).replace(" ", "")

            # Index of the equation for python (starting from 0)
            N_eq = int(str_with_integer)-1

            if (N_eq < 0) or (N_eq > vars_N-1):
                RuntimeError(f"Invalid index '{N_eq}' in line '{line[0:-1]}'")
            
            equations[N_eq] = (line[line.find("=")+1:-1]).replace(" ", "")

    # Check if all equations are defined
    if any([equations[i]==empty_eq_placeholder for i in range(vars_N)]):
        raise RuntimeError(f"Some of the equations are not defined")

    return (vars_names, pars_names, equations)