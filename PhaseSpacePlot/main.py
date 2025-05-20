import os
import dearpygui.dearpygui as dpg

# To convert string with an equation into a callable object
from Equation import Expression

# Reading dynamical system from file
from utils.DS_from_file import load_DS_from_file

# Tmp implementation for DS integration
from utils.integration import euler_integrate


#########################################################################################
#########################################################################################


def update_par_steps():
    for (i, pars_name) in enumerate(pars_names):
        new_step = dpg.get_value(pars_name+"_step")
        dpg.configure_item(pars_name, step=new_step)

def callback_axis_label_change():
    # Update axis labels and consider them to know what to plot
    x_axis_label = dpg.get_value("x_axis_label")
    y_axis_label = dpg.get_value("y_axis_label")
    dpg.configure_item('x_axis', label=x_axis_label)
    dpg.configure_item('y_axis', label=y_axis_label)
    x_axis_i = axis_posible_labels.index(x_axis_label)
    y_axis_i = axis_posible_labels.index(y_axis_label)
    for SaS in SaSs:
        curr_sol = SaS.sol
        curr_t_sol = SaS.t_sol
        if x_axis_i == len(vars_names):
            new_x_dragpoint = 0.0
            x_axis_data = curr_t_sol
        else:
            x_axis_data = [state[x_axis_i] for state in curr_sol]
            new_x_dragpoint = x_axis_data[0]

        if y_axis_i == len(vars_names):
            new_y_dragpoint = 0.0
            y_axis_data = curr_t_sol
        else:
            y_axis_data = [state[y_axis_i] for state in curr_sol]
            new_y_dragpoint = y_axis_data[0]
        dpg.set_value("init_state_"+str(SaS.n), [new_x_dragpoint, new_y_dragpoint])
        dpg.set_value("plot"+str(SaS.n), [x_axis_data, y_axis_data])

def callback_parameter_change():
    # Update integration parameters
    integration_t_start = dpg.get_value('integration_t_start')
    integration_t_end = dpg.get_value('integration_t_end')
    integration_t_steps = dpg.get_value('integration_t_steps')

    # Update dynamical system parameters
    pars = [dpg.get_value(pars_name) for pars_name in pars_names]

    # Get axis labels to know what to plot
    x_axis_label = dpg.get_value("x_axis_label")
    y_axis_label = dpg.get_value("y_axis_label")
    x_axis_i = axis_posible_labels.index(x_axis_label)
    y_axis_i = axis_posible_labels.index(y_axis_label)

    for SaS in SaSs:
        SaS.integrate(ODEs, pars, integration_t_start, integration_t_end, integration_t_steps)
        curr_sol = SaS.sol
        curr_t_sol = SaS.t_sol
        if x_axis_i == len(vars_names):
            x_axis_data = curr_t_sol
        else:
            x_axis_data = [state[x_axis_i] for state in curr_sol]

        if y_axis_i == len(vars_names):
            y_axis_data = curr_t_sol
        else:
            y_axis_data = [state[y_axis_i] for state in curr_sol]
        dpg.set_value("init_state_"+str(SaS.n), [x_axis_data[0], y_axis_data[0]])
        dpg.set_value("plot"+str(SaS.n), [x_axis_data, y_axis_data])

def callback_init_state_change():
    for i in range(len(SaSs)):
        callback_init_state_change_n(i)

def callback_init_state_change_n(n):
    SaS = SaSs[n]
    
    # Get new drag point coordinates
    new_x_dragpoint, new_y_dragpoint = dpg.get_value("init_state_"+str(n))

    # Get axis labels to know what to plot
    x_axis_label = dpg.get_value("x_axis_label")
    y_axis_label = dpg.get_value("y_axis_label")
    x_axis_i = axis_posible_labels.index(x_axis_label)
    y_axis_i = axis_posible_labels.index(y_axis_label)

    # Update old initial state
    if x_axis_i == len(vars_names):
        dpg.set_value("init_state_"+str(n), [0.0, new_y_dragpoint])
    else:
        SaS.init_state[x_axis_i] = new_x_dragpoint

    if y_axis_i == len(vars_names):
        dpg.set_value("init_state_"+str(n), [new_x_dragpoint, 0.0])
    else:
        SaS.init_state[y_axis_i] = new_y_dragpoint
    
    # Reintegrate solution
    pars = [dpg.get_value(pars_name) for pars_name in pars_names]
    integration_t_start = dpg.get_value('integration_t_start')
    integration_t_end = dpg.get_value('integration_t_end')
    integration_t_steps = dpg.get_value('integration_t_steps')
    SaS.integrate(ODEs, pars, integration_t_start, integration_t_end, integration_t_steps)

    # Update solution plot
    if x_axis_i == len(vars_names):
        x_axis_data = SaS.t_sol
    else:
        x_axis_data = [state[x_axis_i] for state in SaS.sol]

    if y_axis_i == len(vars_names):
        y_axis_data = SaS.t_sol
    else:
        y_axis_data = [state[y_axis_i] for state in SaS.sol]

    dpg.set_value("plot"+str(n), [x_axis_data, y_axis_data])
    
def callback_add_drag_init_state():
    n_new = len(SaSs)
    SaSs.append(StateAndSolution(n_new, [0.0 for _ in range(len(vars_names))]))
    dpg.add_drag_point(label="Init. State "+str(n_new),
                               tag="init_state_"+str(n_new), 
                               parent="phase_space_plot",
                               callback=callback_init_state_change, # TODO callback individual dragpoints
                               color=[255, 0, 0, 150])
    dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag="plot"+str(n_new))
    callback_init_state_change_n(n_new)

#########################################################################################
#########################################################################################


# TODO: create a DS folder setup window
DS_folder_path = "test_folder_DS"
DS_filename = "dynamical_system.txt"
DS_filepath = os.path.join(DS_folder_path, DS_filename)

#########################################################################################

# Dynamical System setup
vars_names, pars_names, equations = load_DS_from_file(DS_filepath)
equations_objs = [Expression(eq, vars_names+pars_names) for (i,eq) in enumerate(equations)]
ODEs = lambda U, p, t: [eq_obj(*(U+p)) for eq_obj in equations_objs]

print("Variable names: ", vars_names)
print("Parameter names: ", pars_names)

pars_defaults = [0.0 for _ in pars_names]
par_step_default = 0.1

#########################################################################################

# Integration setup
integration_par_names = ["integration_t_start",
                        "integration_t_end",
                        "integration_t_steps"]
integration_par_types = ["float", "float", "int"]
integration_par_defaults = [0.0, 10.0, 1000]

#########################################################################################

class StateAndSolution():
    def __init__(self, n, init_state):
        self.n = n
        self.init_state = init_state
        self.sol = None
        self.t_sol = None
    
    def integrate(self, ODEs, pars, t_start, t_end, t_N):
        sol, t_sol = euler_integrate(ODEs, self.init_state, pars, t_end, (t_end-t_start)/t_N) # TODO change integration algorithm
        self.sol = sol
        self.t_sol = t_sol

SaSs = []

#########################################################################################

# Plot parameters
x_axis_label_default = vars_names[0]
y_axis_label_default = vars_names[1]
axis_posible_labels = vars_names + ["t",]


#########################################################################################
#########################################################################################


dpg.create_context()

with dpg.window(label='Dynamical System Parameters', tag="DS_pars_w", pos=(0,0)):
    global par_objs, par_s
    par_objs = []
    par_step_objs = []
    for (i, par_name) in enumerate(pars_names):
        with dpg.group(horizontal=True):
            par_obj = dpg.add_input_float(label=par_name, 
                                          default_value=pars_defaults[i], 
                                          tag=par_name, 
                                          callback=callback_parameter_change, 
                                          width=150)
            par_step_obj = dpg.add_input_float(label=par_name+" step", 
                                               default_value=par_step_default, 
                                               tag=par_name+"_step", 
                                               callback=update_par_steps,
                                               width=100,
                                               step=0.0)
            par_objs.append(par_obj)
            par_step_objs.append(par_step_obj)

#########################################################################################

with dpg.window(label='Integration Parameters', tag="integration_pars_w", pos=(0, 200)):
    for (i, par_name) in enumerate(integration_par_names):
            if integration_par_types[i] == "float":
                tmp_add_input = dpg.add_input_float
            elif integration_par_types[i] == "int":
                tmp_add_input = dpg.add_input_int
            integration_par_dpg_obj = tmp_add_input(label=par_name, 
                                               tag=par_name,
                                               default_value=integration_par_defaults[i], 
                                               width=150,
                                               callback=callback_parameter_change)

#########################################################################################

with dpg.window(label='Plot Parameters', tag="plot_pars_w", pos=(0, 400)):
    dpg.add_combo(label="X Axis Label", 
                  tag="x_axis_label",
                  default_value=x_axis_label_default, 
                  items=axis_posible_labels, 
                  callback=callback_parameter_change)
    dpg.add_combo(label="Y Axis Label", 
                  tag="y_axis_label",
                  default_value=y_axis_label_default, 
                  items=axis_posible_labels, 
                  callback=callback_parameter_change)

#########################################################################################

with dpg.window(label='Drag Initial States', tag="drag_init_states_w", pos=(0, 600)):
    dpg.add_button(label="Add Drag Initial State",
                   tag="add_drag_init_state",
                   callback=callback_add_drag_init_state)

#########################################################################################

with dpg.window(label='Phase Space Plot', tag="plot_w", pos=(350, 0)):
    with dpg.plot(label='Phase Space Plot', tag="phase_space_plot", width=700, height=700):
        dpg.add_plot_axis(dpg.mvXAxis, 
                          label=x_axis_label_default, 
                          tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, 
                          label=y_axis_label_default, 
                          tag="y_axis")

        for i in range(len(SaSs)):
            dpg.add_drag_point(label="Init. State "+str(i),
                               tag="init_state_"+str(i), 
                               callback=callback_init_state_change, # TODO callback individual dragpoints
                               color=[255, 0, 0, 150])
            dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag="plot"+str(i))

        callback_parameter_change()

#########################################################################################

dpg.create_viewport(title='PhaseSpacePlot', width=1100, height=750)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
