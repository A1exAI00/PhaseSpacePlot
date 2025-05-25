import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from utils.integration import Trajectory

#########################################################################################

class PhaseSpaceWorkbench:
    def __init__(self, app):
        self.app = app
        return

    def setup_dynamical_system_parameters_window(self):
        with dpg.window(label='Dynamical System Parameters', tag="dynamical_system_parameters_window", pos=(0,0)):
            for (i, par_name) in enumerate(self.app.parameter_names):
                with dpg.group(horizontal=True):
                    dpg.add_input_float(label=par_name, tag=par_name, 
                                        default_value=self.app.parameter_defaults[i], 
                                        callback=self.callback_change_parameter, 
                                        width=150)
                    dpg.add_input_float(label=par_name+" step", tag=par_name+"_step", 
                                        default_value=self.app.parameter_step_defaults[i], 
                                        callback=self.callback_change_parameter_step,
                                        width=100, step=0.0)
                with dpg.popup(parent=par_name):
                        dpg.add_button(label="Copy all parameter values", callback=self.callback_copy_all_parameter_values)
                        dpg.add_button(label="Paste all parameter values", callback=self.callback_paste_all_parameter_values)
                        dpg.add_button(label="Copy value: "+par_name, callback=self.callback_copy_parameter_value)
        return

    def setup_integration_parameters_window(self):
        with dpg.window(label='Integration Parameters', tag="integration_parameters_window", pos=(0, 200)):
            for (i, parameter_name) in enumerate(self.app.integration_parameter_names):
                    current_type = self.app.integration_parameter_types[i]
                    if current_type == "float":
                        tmp_add_input = dpg.add_input_float
                    elif current_type == "int":
                        tmp_add_input = dpg.add_input_int
                    tmp_add_input(label=parameter_name, tag=parameter_name,
                                default_value=self.app.integration_parameter_defaults[i], 
                                width=150,
                                callback=self.callback_change_parameter)
        return

    def setup_plot_parameters_window(self):
        with dpg.window(label='Plot Parameters', tag="plot_parameters_window", pos=(0, 400)):
            dpg.add_combo(label="X Axis Label", tag="x_axis_label",
                        default_value=self.app.x_axis_label_default, 
                        items=self.app.axis_posible_labels, 
                        callback=self.callback_change_axis_label, 
                        width=100)
            dpg.add_combo(label="Y Axis Label", tag="y_axis_label",
                        default_value=self.app.y_axis_label_default, 
                        items=self.app.axis_posible_labels, 
                        callback=self.callback_change_axis_label,
                        width=100)
            # with dpg.group(horizontal=True):
            #     dpg.add_input_float(label="X Axis min", tag="x_axis_min", 
            #                         default_value=-1.0, 
            #                         callback=self.callback_change_axis_limits, 
            #                         width=100, step=0.0)
            #     dpg.add_input_float(label="X Axis max", tag="x_axis_max", 
            #                         default_value=1.0, 
            #                         callback=self.callback_change_axis_limits, 
            #                         width=100, step=0.0)
            # with dpg.group(horizontal=True):
            #     dpg.add_input_float(label="Y Axis min", tag="y_axis_min", 
            #                         default_value=-1.0, 
            #                         callback=self.callback_change_axis_limits, 
            #                         width=100, step=0.0)
            #     dpg.add_input_float(label="Y Axis max", tag="y_axis_max", 
            #                         default_value=1.0, 
            #                         callback=self.callback_change_axis_limits, 
            #                         width=100, step=0.0)
        return

    def setup_dragpoint_init_state_window(self):
        with dpg.window(label='Drag Initial States', tag="dragpoint_init_state_window", pos=(0, 600)):
            dpg.add_button(label="Add Dragpoint Initial State",tag="add_dragpoint_init_state",
                        callback=self.callbcak_add_dragpoint)
        return

    def setup_phase_space_plot_window(self):
        with dpg.window(label='Phase Space Plot', tag="plot_w", pos=(370, 0)):
            with dpg.plot(label='', tag="phase_space_plot", width=700, height=700):
                dpg.add_plot_axis(dpg.mvXAxis, 
                                label=self.app.x_axis_label_default, tag="x_axis")
                dpg.add_plot_axis(dpg.mvYAxis, 
                                label=self.app.y_axis_label_default, tag="y_axis")

                for (n,trajectory) in enumerate(self.app.trajectories):
                    dpg.add_drag_point(label="Init. State "+str(n), tag="init_state_"+str(n), 
                                    callback=self.callback_change_dragpoint_position, # TODO callback individual dragpoints
                                    color=[255, 0, 0, 150])
                    dpg.add_line_series([], [], label="", parent='y_axis', tag="plot"+str(n))

        self.callback_change_parameter(None, None)
        return
    
    def setup_all(self):
        self.setup_dynamical_system_parameters_window()
        self.setup_integration_parameters_window()
        self.setup_plot_parameters_window()
        self.setup_dragpoint_init_state_window()
        self.setup_phase_space_plot_window()


    def callback_change_parameter(self, sender, app_data):
        # Update integration parameters
        integration_t_start = dpg.get_value('integration_t_start')
        integration_t_end = dpg.get_value('integration_t_end')
        integration_t_steps = dpg.get_value('integration_t_steps')

        # Update dynamical system parameters
        pars = [dpg.get_value(parameter_name) for parameter_name in self.app.parameter_names]

        # Get axis labels to know what to plot
        x_axis_label = dpg.get_value("x_axis_label")
        y_axis_label = dpg.get_value("y_axis_label")
        x_axis_i = self.app.axis_posible_labels.index(x_axis_label)
        y_axis_i = self.app.axis_posible_labels.index(y_axis_label)

        for trajectory in self.app.trajectories:
            # Reintegrate with new parameters
            trajectory.integrate_scipy(self.app.ODEs, pars, integration_t_start, integration_t_end, integration_t_steps)
            curr_sol = trajectory.sol
            curr_t_sol = trajectory.t_sol
            if x_axis_i == len(self.app.variable_names):
                x_axis_data = curr_t_sol
            else:
                x_axis_data = curr_sol[x_axis_i]

            if y_axis_i == len(self.app.variable_names):
                y_axis_data = curr_t_sol
            else:
                y_axis_data = curr_sol[y_axis_i]
            dpg.set_value("init_state_"+str(trajectory.n), [x_axis_data[0], y_axis_data[0]])
            dpg.set_value("plot"+str(trajectory.n), [x_axis_data, y_axis_data])
        return

    def callback_change_parameter_step(self, sender, app_data):
        for (i, parameter_name) in enumerate(self.app.parameter_names):
            new_step = dpg.get_value(parameter_name+"_step")
            dpg.configure_item(parameter_name, step=new_step)
        return

    def callback_change_axis_label(self, sender, app_data):
        # Update axis labels and consider them to know what to plot
        x_axis_label = dpg.get_value("x_axis_label")
        y_axis_label = dpg.get_value("y_axis_label")
        dpg.configure_item('x_axis', label=x_axis_label)
        dpg.configure_item('y_axis', label=y_axis_label)
        x_axis_i = self.app.axis_posible_labels.index(x_axis_label)
        y_axis_i = self.app.axis_posible_labels.index(y_axis_label)
        for trajectory in self.app.trajectories:
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
            dpg.set_value("init_state_"+str(trajectory.n), [new_x_dragpoint, new_y_dragpoint])
            dpg.set_value("plot"+str(trajectory.n), [x_axis_data, y_axis_data])
        return 

    def callback_change_axis_limits(self, sender, app_data):
        x_axis_min = dpg.get_value("x_axis_min")
        x_axis_max = dpg.get_value("x_axis_max")
        y_axis_min = dpg.get_value("y_axis_min")
        y_axis_max = dpg.get_value("y_axis_max")
        dpg.set_axis_limits("x_axis", x_axis_min, x_axis_max)
        dpg.set_axis_limits("y_axis", y_axis_min, y_axis_max)
        return
    
    def callback_copy_all_parameter_values(self, sender, app_data):
        result = ""
        for (i, parameter_name) in enumerate(self.app.parameter_names):
            result += parameter_name + " = " + str(dpg.get_value(parameter_name)) + ", "
        clip.copy(result[:-2])
        return
    
    def callback_paste_all_parameter_values(self, sender, app_data):
        parameter_values_str = clip.paste()
        separater_charecters = [",", ";"]
        for sep in separater_charecters:
            if sep not in parameter_values_str:
                continue
            parameter_values_split = parameter_values_str.split(sep)
            for split in parameter_values_split:
                parameter_name = split[:split.find("=")].replace(" ", "")
                parameter_value = split[split.find("=")+1:].replace(" ", "")
                dpg.set_value(parameter_name, float(parameter_value))
        self.callback_change_parameter(None, None)
        return
    
    def callback_copy_parameter_value(self, sender, app_data):
        sender_label = dpg.get_item_label(sender)
        parameter_name = sender_label[sender_label.find(":")+1:].replace(" ", "")
        parameter_value = dpg.get_value(parameter_name)
        clip.copy(parameter_value)
        return

    def callbcak_add_dragpoint(self, sender, app_data):
        n_new = len(self.app.trajectories)
        trajectory_new = Trajectory(n_new, np.zeros(len(self.app.variable_names)))
        self.app.trajectories.append(trajectory_new)
        dpg.add_drag_point(label="Init. State "+str(n_new),
                        tag="init_state_"+str(n_new), 
                        parent="phase_space_plot",
                        callback=self.callback_change_dragpoint_position, 
                        color=[255, 0, 0, 150])
        dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag="plot"+str(n_new))
        self.dragpoint_update_position_integrate_draw(n_new)
        return

    def dragpoint_update_position_integrate_draw(self, n):
        trajectory = self.app.trajectories[n]
        # Get new drag point coordinates
        new_x_dragpoint, new_y_dragpoint = dpg.get_value("init_state_"+str(n))

        # Get axis labels to know what to plot
        x_axis_label = dpg.get_value("x_axis_label")
        y_axis_label = dpg.get_value("y_axis_label")
        x_axis_i = self.app.axis_posible_labels.index(x_axis_label)
        y_axis_i = self.app.axis_posible_labels.index(y_axis_label)

        # Update old initial state
        if x_axis_i == len(self.app.variable_names):
            dpg.set_value("init_state_"+str(n), [0.0, new_y_dragpoint])
        else:
            trajectory.init_state[x_axis_i] = new_x_dragpoint

        if y_axis_i == len(self.app.variable_names):
            dpg.set_value("init_state_"+str(n), [new_x_dragpoint, 0.0])
        else:
            trajectory.init_state[y_axis_i] = new_y_dragpoint
        
        # Reintegrate solution
        pars = [dpg.get_value(pars_name) for pars_name in self.app.parameter_names]
        integration_t_start = dpg.get_value('integration_t_start')
        integration_t_end = dpg.get_value('integration_t_end')
        integration_t_steps = dpg.get_value('integration_t_steps')
        trajectory.integrate_scipy(self.app.ODEs, pars, integration_t_start, integration_t_end, integration_t_steps)

        # Update solution plot
        if x_axis_i == len(self.app.variable_names):
            x_axis_data = trajectory.t_sol
        else:
            x_axis_data = trajectory.sol[x_axis_i]

        if y_axis_i == len(self.app.variable_names):
            y_axis_data = trajectory.t_sol
        else:
            y_axis_data = trajectory.sol[y_axis_i]

        dpg.set_value("plot"+str(n), [x_axis_data, y_axis_data])

    def callback_change_dragpoint_position(self, sender, app_data):
        n = int(dpg.get_item_configuration(sender)["label"][len("Init. State "):])
        self.dragpoint_update_position_integrate_draw(n)
        return
    
    def callback_change_dragpoint_color(self, sender, app_data):
        return 

    def callback_delete_dragpoint(self, sender, app_data):
        return

    def callback_hide_dragpoint(self, sender, app_data):
        return