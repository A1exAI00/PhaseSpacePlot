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


def update_plot():
    integration_t_start = dpg.get_value('integration_t_start')
    integration_t_end = dpg.get_value('integration_t_end')
    integration_t_steps = dpg.get_value('integration_t_steps')
    dt = (integration_t_end-integration_t_start)/integration_t_steps

    pars = [dpg.get_value(pars_name) for pars_name in pars_names]
    x_init, y_init = dpg.get_value('init_state')

    sol, t_sol = euler_integrate(ODEs, [x_init, y_init], pars, integration_t_end, dt)

    x_axis_label = dpg.get_value("x_axis_label")
    y_axis_label = dpg.get_value("y_axis_label")

    x_axis_i = axis_posible_labels.index(x_axis_label)
    y_axis_i = axis_posible_labels.index(y_axis_label)

    if x_axis_i == len(vars_names):
        x_axis_data = t_sol
    else:
        x_axis_data = [state[x_axis_i] for state in sol]

    if y_axis_i == len(vars_names):
        y_axis_data = t_sol
    else:
        y_axis_data = [state[y_axis_i] for state in sol]


    dpg.set_value('main_plot_series', [x_axis_data, y_axis_data])

def update_par_steps():
    for (i, pars_name) in enumerate(pars_names):
        new_step = dpg.get_value(pars_name+"_step")
        dpg.configure_item(pars_name, step=new_step)


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

# TODO replace because not general
pars_defaults = [0.0 for _ in pars_names]
par_step_default = 0.1

#########################################################################################

# Integration setup
integration_par_names = ["integration_t_start",
                        "integration_t_end",
                        "integration_t_steps"]
integration_par_types = ["float", "float", "int"]
integration_par_defaults = [0.0, 1.0, 100]

#########################################################################################


# TODO add Dynamical System Initial State setup
# init_states = []

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
                                          callback=update_plot, 
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
    integration_par_dpg_objs = []
    for (i, par_name) in enumerate(integration_par_names):
            if integration_par_types[i] == "float":
                integration_par_dpg_obj = dpg.add_input_float(label=par_name, 
                                                              tag=par_name,
                                                              default_value=integration_par_defaults[i], 
                                                              width=150) 
            elif integration_par_types[i] == "int":
                integration_par_dpg_obj = dpg.add_input_int(label=par_name, 
                                                            tag=par_name,
                                                            default_value=integration_par_defaults[i], 
                                                            width=150) 
            else:
                continue
            integration_par_dpg_objs.append(integration_par_dpg_obj)
    _ = [dpg.set_item_callback(par_dpg_obj, update_plot) for par_dpg_obj in integration_par_dpg_objs]

#########################################################################################

with dpg.window(label='Plot Parameters', tag="plot_pars_w", pos=(0, 400)):
    plot_par_dpg_objs = []
    plot_par_dpg_objs.append(dpg.add_combo(label="X Axis Label", 
                                           tag="x_axis_label",
                                           default_value=x_axis_label_default, 
                                           items=axis_posible_labels, 
                                           callback=update_plot))
    plot_par_dpg_objs.append(dpg.add_combo(label="Y Axis Label", 
                                           tag="y_axis_label",
                                           default_value=y_axis_label_default, 
                                           items=axis_posible_labels, 
                                           callback=update_plot))

#########################################################################################

with dpg.window(label='Phase Space Plot', tag="plot_w", pos=(350, 0)):
    with dpg.plot(label='Series', width=700, height=700):

        # Add axis labels
        dpg.add_plot_axis(dpg.mvXAxis, 
                          label=vars_names[0], 
                          tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, 
                          label=vars_names[1], 
                          tag="y_axis")

        # Add drag point, set callback function
        dpg.add_drag_point(label='Init. State', 
                           tag='init_state', 
                           callback=update_plot, 
                           color=[255, 0, 0, 150])

        # Add the actual line plot
        dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag='main_plot_series')

        update_plot()

#########################################################################################

dpg.create_viewport(title='PhaseSpacePlot', width=1100, height=750)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
