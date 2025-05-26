import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from utils.integration import Trajectory

#########################################################################################

PARAMETER_FORMATING = "%f"
PARAMETER_STEP_FORMATING = "%.2E"
PARAMETER_WIDTH = 130
PARAMETER_STEP_WIDTH = 65
VARIABLE_FORMATING = "%f"
VARIABLE_STEP_FORMATING = "%.2E"
VARIABLE_WIDTH = 110
VARIABLE_STEP_WIDTH = 65

DEFAULT_T_START = 0.0
DEFAULT_T_END = 10.0
DEFAULT_T_STEPS = 1000

INTEGRATION_DIRECTIONS = ["+", "-"]

ALLOWED_SEPARATORS = [",", ";", ":"]
DEFAULT_SEPARATOR = ALLOWED_SEPARATORS[0]

#########################################################################################

class PhaseSpaceWorkbench:
    def __init__(self, app):
        self.app = app
        return

    def setup_dynamical_system_parameters_window(self):
        with dpg.window(label='Dynamical System Parameters', tag="dynamical_system_parameters_window", pos=(0,0)):
            for (i, parameter_name) in enumerate(self.app.parameter_names):

                # Create a row of parameter input and a parameter step input for every parameter_name
                with dpg.group(horizontal=True) as group:
                    dpg.add_input_float(label=parameter_name, tag=parameter_name, 
                                        default_value=self.app.parameter_defaults[i], 
                                        callback=self.callback_change_parameter, 
                                        width=PARAMETER_WIDTH, format=PARAMETER_FORMATING)
                    dpg.add_input_float(label=parameter_name+" step", tag=parameter_name+"_step", 
                                        default_value=self.app.parameter_step_defaults[i], 
                                        callback=self.callback_change_parameter_step,
                                        width=PARAMETER_STEP_WIDTH, step=0.0, format=PARAMETER_STEP_FORMATING)
                    
                    # Create a contect menu for the parameter
                    with dpg.popup(parent=group, no_move=True):
                        with dpg.group(label=parameter_name):
                            dpg.add_button(label="Copy parameter value", callback=self.callback_copy_parameter_value)
                            dpg.add_button(label="Copy parameter name=value", callback=self.callback_copy_parameter_value_w_name)
                            dpg.add_button(label="Copy all parameter values", callback=self.callback_copy_all_parameter_values)
                            dpg.add_button(label="Paste all parameter values", callback=self.callback_paste_all_parameter_values)
        return

    def setup_integration_parameters_window(self): # TODO add algorithm picker
        with dpg.window(label='Integration Parameters', tag="integration_parameters_window", pos=(0, 200)):
            dpg.add_text("Nothing here")
        return

    def setup_plot_parameters_window(self):
        with dpg.window(label='Plot Parameters', tag="plot_parameters_window", pos=(300, 0)):

            # Create two combo boxes to choose axis labels
            dpg.add_combo(label="X Axis Label", tag="x_axis_label",
                        default_value=self.app.x_axis_label_default, 
                        items=self.app.axis_posible_labels, 
                        callback=self.callback_change_axis_label, 
                        width=PARAMETER_WIDTH)
            dpg.add_combo(label="Y Axis Label", tag="y_axis_label",
                        default_value=self.app.y_axis_label_default, 
                        items=self.app.axis_posible_labels, 
                        callback=self.callback_change_axis_label,
                        width=PARAMETER_WIDTH)
        return

    def setup_dragpoint_init_state_window(self):
        with dpg.window(label='Drag Initial States', tag="dragpoint_init_state_window", pos=(0, 300), height=400):

            # Button to create new dragpoint
            dpg.add_button(label="Add Dragpoint Initial State",tag="add_dragpoint_init_state",
                        callback=self.callbcak_add_dragpoint)
            
            # Create a list of headers for dragpoint table
            header_for_variables = []
            for (i,variable_name) in enumerate(self.app.variable_names):
                header_for_variables.append(variable_name)
                header_for_variables.append(variable_name+" step")
            header_texts = ["n", "show", "dt", *header_for_variables, "t start", "t end", "t steps"]
        
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Create a table for dragpoints
            with dpg.table(header_row=True, row_background=True, tag="dragpoint_table",
                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                           borders_outerV=True, policy=dpg.mvTable_SizingFixedFit):
                
                # Add a colomn for each header item
                for header_text in header_texts:
                    dpg.add_table_column(label=header_text)
                
                # Add a row for each trajectory
                for (n, trajectory) in self.app.trajectories.items():
                    self.add_row_to_dragpoint_table(n)
        return
    
    def add_row_to_dragpoint_table(self, n):
        with dpg.table_row(parent="dragpoint_table"):
            
            # Ordinal number of dragpoint 
            dpg.add_text(str(n))

            # Chechbox show/hide dragpoint and trajectory
            with dpg.group(label=f"{n}") as group:
                dpg.add_checkbox(label="", default_value=True, tag=f"hide_{n}", callback=self.callback_toggle_visibility_dragpoint)

            # Direction of integration combo box
            with dpg.group(label=f"{n}") as group:
                dpg.add_combo(label="", tag=f"dt_{n}", 
                              width=40,
                              items=INTEGRATION_DIRECTIONS, 
                              default_value=INTEGRATION_DIRECTIONS[0], 
                              callback=self.callback_change_parameter)
            
            # Variable input and variable step input for every variable_name
            for (i, variable_name) in enumerate(self.app.variable_names):
                with dpg.group(label=f"{n}") as group:
                    dpg.add_input_float(label="", tag=f"{variable_name}_{n}", 
                                        default_value=0.0, 
                                        callback=self.callback_change_variable_in_dragpoint_table, 
                                        width=VARIABLE_WIDTH, format=VARIABLE_FORMATING)
                    
                # Context menu for variable input
                with dpg.popup(parent=group):
                    with dpg.group(label=f"{variable_name}_{n}") as group1:
                        dpg.add_button(label="Copy variable value", callback=self.callback_copy_variable)
                        dpg.add_button(label="Copy variable name=value", callback=self.callback_copy_variable_w_name)
                        dpg.add_button(label="Copy init state", callback=self.callback_copy_init_state)
                        dpg.add_button(label="Paste init state", callback=self.callback_paste_init_state)
                        dpg.add_button(label="Copy last state", callback=self.callback_copy_last_state)

                # Variable step input
                with dpg.group(label=f"{n}") as group:
                    dpg.add_input_float(label="", tag=f"{variable_name}_step_{n}", 
                                        default_value=0.1, 
                                        callback=self.callback_change_variable_step, 
                                        width=VARIABLE_STEP_WIDTH, step=0.0, format=VARIABLE_STEP_FORMATING)
            
            # Integration start, end and steps inputs
            dpg.add_input_float(label="", tag=f"t_start_{n}",
                                callback=self.callback_change_parameter,
                                default_value=DEFAULT_T_START, step=0.0, width=50)
            dpg.add_input_float(label="", tag=f"t_end_{n}",
                                callback=self.callback_change_parameter,
                                default_value=DEFAULT_T_END, step=0.0, width=50)
            dpg.add_input_int(label="", tag=f"t_steps_{n}",
                                callback=self.callback_change_parameter,
                                default_value=DEFAULT_T_STEPS, step=0.0, width=50)
        return

    def setup_phase_space_plot_window(self):
        with dpg.window(label='Phase Space Plot', tag="plot_w", pos=(750, 0)):
            with dpg.plot(label='', tag="phase_space_plot", width=700, height=700):

                # Add x and y axis
                dpg.add_plot_axis(dpg.mvXAxis, 
                                label=self.app.x_axis_label_default, tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, 
                                label=self.app.y_axis_label_default, tag="y_axis")

                # Add dragpoint and plot for every trajectory
                for (n,trajectory) in self.app.trajectories.items():
                    dpg.add_drag_point(label=f"Init. State {n}", tag=f"init_state_{n}", 
                                    callback=self.callback_change_dragpoint_position,
                                    color=[255, 0, 0, 150])
                    dpg.add_line_series([], [], label="", parent='y_axis', tag="plot"+str(n))

        # Refresh all trajectories
        self.callback_change_parameter(None, None)
        return
    
    def setup_all(self):
        self.setup_dynamical_system_parameters_window()
        # self.setup_integration_parameters_window()
        self.setup_plot_parameters_window()
        self.setup_dragpoint_init_state_window()
        self.setup_phase_space_plot_window()

    def get_axis_labels(self):
        x_axis_label = dpg.get_value("x_axis_label")
        y_axis_label = dpg.get_value("y_axis_label")
        x_axis_i = self.app.axis_posible_labels.index(x_axis_label)
        y_axis_i = self.app.axis_posible_labels.index(y_axis_label)
        return (x_axis_label, y_axis_label, x_axis_i, y_axis_i)
    
    def get_init_state(self,n):
        variable_tags = [f"{variable_name}_{n}" for (i, variable_name) in enumerate(self.app.variable_names)]
        return np.array(dpg.get_values(variable_tags))
    
    def get_last_state(self, n):
        last_state = []
        for (i, variable_name) in enumerate(self.app.variable_names):
            last_state.append(self.app.trajectories[n].sol[i][-1])
        return np.array(last_state)

    def update_from_dragpoint_to_dragpoint_table(self, n):
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()

        # Get dragpoint position
        x_dragpoint, y_dragpoint = dpg.get_value(f"init_state_{n}")
        if x_axis_i != len(self.app.variable_names):
            dpg.set_value(f"{x_axis_label}_{n}", x_dragpoint)
        if y_axis_i != len(self.app.variable_names):
            dpg.set_value(f"{y_axis_label}_{n}", y_dragpoint)
        return

    def update_from_dragpoint_table_to_dragpoint(self, n):
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()

        if x_axis_i == len(self.app.variable_names) and y_axis_i == len(self.app.variable_names):
            dpg.set_value(f"init_state_{n}", [0.0, 0.0])
            return
        if x_axis_i == len(self.app.variable_names):
            y_data = dpg.get_value(f"{y_axis_label}_{n}")
            dpg.set_value(f"init_state_{n}", [0.0, y_data])
            return
        if y_axis_i == len(self.app.variable_names):
            x_data = dpg.get_value(f"{x_axis_label}_{n}")
            dpg.set_value(f"init_state_{n}", [x_data, 0.0])
            return
        x_data = dpg.get_value(f"{x_axis_label}_{n}")
        y_data = dpg.get_value(f"{y_axis_label}_{n}")
        dpg.set_value(f"init_state_{n}", [x_data, y_data])
        return
    
    def update_from_init_state_table_to_trajectory(self, n):
        # Get parameters from GUI
        pars = [dpg.get_value(parameter_name) for parameter_name in self.app.parameter_names]
        integration_t_start = dpg.get_value(f"t_start_{n}")
        integration_t_end = dpg.get_value(f"t_end_{n}")
        integration_t_steps = dpg.get_value(f"t_steps_{n}")
        dt = dpg.get_value(f"dt_{n}")
        if dt == "-":
            integration_t_start, integration_t_end = integration_t_end, integration_t_start

        # Get init state from table
        init_state = self.get_init_state(n)

        # Reintegrate with new parameters
        trajectory = self.app.trajectories[n]
        trajectory.init_state = init_state
        trajectory.integrate_scipy(self.app.ODEs, pars, integration_t_start, integration_t_end, integration_t_steps)
        return

    def update_from_trajectory_to_plot(self, n):
        _, _, x_axis_i, y_axis_i = self.get_axis_labels()

        sol, t_sol = self.app.trajectories[n].sol, self.app.trajectories[n].t_sol
        if x_axis_i == len(self.app.variable_names):
            x_axis_data = t_sol
        else:
            x_axis_data = sol[x_axis_i]

        if y_axis_i == len(self.app.variable_names):
            y_axis_data = t_sol
        else:
            y_axis_data = sol[y_axis_i]
        dpg.set_value(f"plot{n}", [x_axis_data, y_axis_data])
        return

    def callback_change_parameter(self, sender, app_data): # TODO consider sender
        for (n, trajectory) in self.app.trajectories.items():
            self.update_from_init_state_table_to_trajectory(n)
            self.update_from_trajectory_to_plot(n)

    def callback_change_parameter_step(self, sender, app_data):
        for (i, parameter_name) in enumerate(self.app.parameter_names):
            new_step = dpg.get_value(f"{parameter_name}_step")
            dpg.configure_item(parameter_name, step=new_step)
        return
    
    def callback_change_variable_in_dragpoint_table(self, sender, app_data):
        n = int(dpg.get_item_label(dpg.get_item_parent(sender)))
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_init_state_table_to_trajectory(n)
        self.update_from_trajectory_to_plot(n)
        return

    def callback_change_variable_step(self, sender, app_data):
        for (n, trajectory) in self.app.trajectories.items():
            for (i, variable_name) in enumerate(self.app.variable_names):
                new_step = dpg.get_value(f"{variable_name}_step_{n}")
                dpg.configure_item(f"{variable_name}_{n}", step=new_step)
        return

    def callback_change_axis_label(self, sender, app_data):
        # Update axis labels and consider them to know what to plot
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()
        dpg.configure_item('x_axis', label=x_axis_label)
        dpg.configure_item('y_axis', label=y_axis_label)

        # Redraw every trajectory and dragpoint because of new axis
        for (n,trajectory) in self.app.trajectories.items():
            curr_sol = trajectory.sol
            curr_t_sol = trajectory.t_sol
            if x_axis_i == len(self.app.variable_names):
                new_x_dragpoint = 0.0
                x_axis_data = curr_t_sol
            else:
                x_axis_data = curr_sol[x_axis_i]
                new_x_dragpoint = x_axis_data[0]

            if y_axis_i == len(self.app.variable_names):
                new_y_dragpoint = 0.0
                y_axis_data = curr_t_sol
            else:
                y_axis_data = curr_sol[y_axis_i]
                new_y_dragpoint = y_axis_data[0]
            dpg.set_value(f"init_state_{n}", [new_x_dragpoint, new_y_dragpoint])
            dpg.set_value(f"plot{n}", [x_axis_data, y_axis_data])
        return 
    
    def callback_copy_all_parameter_values(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Create a strings of "par_n=val_n"
        result = [f"{parameter_name}={dpg.get_value(parameter_name)}" for parameter_name in self.app.parameter_names]

        sep = DEFAULT_SEPARATOR
        clip.copy(sep.join(result))
        return
    
    def callback_paste_all_parameter_values(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Read clipboard
        parameter_values_str = clip.paste().replace(" ", "")

        # For every separator, check if it is used, split with ir, split with "=" and set parameter
        for sep in ALLOWED_SEPARATORS:
            if sep not in parameter_values_str:
                continue
            parameter_values_split = parameter_values_str.split(sep)
            for split in parameter_values_split:
                parameter_name = split[:split.find("=")]
                parameter_value = split[split.find("=")+1:]
                dpg.set_value(parameter_name, float(parameter_value))

        # Refresh all trajectories
        self.callback_change_parameter(None, None)
        return
    
    def callback_copy_parameter_value(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Get parameter_name from the layout of the context menu
        parameter_name = dpg.get_item_label(dpg.get_item_parent(sender))

        clip.copy(dpg.get_value(parameter_name))
        return
    
    def callback_copy_parameter_value_w_name(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Get parameter_name from the layout of the context menu
        parameter_name = dpg.get_item_label(dpg.get_item_parent(sender))

        clip.copy(f"{parameter_name}={dpg.get_value(parameter_name)}")
        return

    def callbcak_add_dragpoint(self, sender, app_data):
        # New ordinal number bigger then others, create new trajectory
        n_new = max(self.app.trajectories.keys())+1
        trajectory_new = Trajectory(np.zeros(len(self.app.variable_names)))
        self.app.trajectories[n_new] = trajectory_new

        # New row in the dragpoint table
        self.add_row_to_dragpoint_table(n_new)
        
        # Add new dragpoint and plot
        dpg.add_drag_point(label=f"Init. State {n_new}",
                        tag=f"init_state_{n_new}", 
                        parent="phase_space_plot",
                        callback=self.callback_change_dragpoint_position, 
                        color=[255, 0, 0, 150])
        dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag=f"plot{n_new}")

        # Refresh this trajectory
        self.update_from_dragpoint_to_dragpoint_table(n_new)
        self.update_from_dragpoint_table_to_dragpoint(n_new)
        self.update_from_init_state_table_to_trajectory(n_new)
        self.update_from_trajectory_to_plot(n_new)
        return

    def callback_change_dragpoint_position(self, sender, app_data):
        n = int(dpg.get_item_configuration(sender)["label"][len("Init. State "):])
        self.update_from_dragpoint_to_dragpoint_table(n)
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_init_state_table_to_trajectory(n)
        self.update_from_trajectory_to_plot(n)
        return
    
    def callback_change_dragpoint_color(self, sender, app_data):
        return 

    def callback_toggle_visibility_dragpoint(self, sender, app_data):
        show = dpg.get_value(sender) 
        n = int(dpg.get_item_configuration(dpg.get_item_parent(sender))["label"])
        if show:
            dpg.show_item(f"init_state_{n}")
            dpg.show_item(f"plot{n}")
        else:
            dpg.hide_item(f"init_state_{n}")
            dpg.hide_item(f"plot{n}")
        return
    
    def callback_copy_variable(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Get variable_name_n from the layout of the context menu
        variable_n = dpg.get_item_label(dpg.get_item_parent(sender))

        variable_value = dpg.get_value(variable_n)
        clip.copy(variable_value)
        return
    
    def callback_copy_variable_w_name(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Get variable_name_n from the layout of the context menu
        variable_n = dpg.get_item_label(dpg.get_item_parent(sender))
        variable_name, _ = variable_n.split("_")

        clip.copy(f"{variable_name}={dpg.get_value(variable_n)}")
        return

    def callback_copy_init_state(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Get variable_name_n from the layout of the context menu
        variable_n = dpg.get_item_label(dpg.get_item_parent(sender))
        variable_name, n = variable_n.split("_")
        n = int(n)

        # Create a strings of "var_n=val_n"
        init_state = self.get_init_state(n)
        result = [f"{variable_name}={init_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = DEFAULT_SEPARATOR
        clip.copy(sep.join(result))
        return

    def callback_paste_init_state(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Which n trajectory has been clicked
        variable_n = dpg.get_item_label(dpg.get_item_parent(sender))
        _, n = variable_n.split("_")
        n = int(n)

        # Read the clipboard
        variable_values_str = clip.paste().replace(" ", "")

        for sep in ALLOWED_SEPARATORS:
            if sep not in variable_values_str:
                continue
            variable_values_split = variable_values_str.split(sep)
            for split in variable_values_split:
                variable_name = split[:split.find("=")]
                variable_value = split[split.find("=")+1:]
                dpg.set_value(f"{variable_name}_{n}", float(variable_value))
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_init_state_table_to_trajectory(n)
        self.update_from_trajectory_to_plot(n)
        return
    
    def callback_copy_last_state(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(dpg.get_item_parent(sender)))

        # Which n trajectory has been clicked
        variable_n = dpg.get_item_label(dpg.get_item_parent(sender))
        _, n = variable_n.split("_")
        n = int(n)

        last_state = self.get_last_state(n)
        result = [f"{variable_name}={last_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = DEFAULT_SEPARATOR
        clip.copy(sep.join(result))
        return