import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from utils.integration import Trajectory

#########################################################################################

class PhaseSpaceWorkbenchDragpoint:
    def get_dragpoint_table_init_state(self,n):
        variable_tags = [f"dragpoint_table_{variable_name}_{n}" for (i, variable_name) in enumerate(self.app.variable_names)]
        return np.array(dpg.get_values(variable_tags))

    def get_dragpoint_last_state(self, n):
        return np.array([self.dragpoint_trajectories[n].sol[i][-1] for (i, variable_name) in enumerate(self.app.variable_names)])

    def setup_dragpoint_init_state_window(self):
        with dpg.window(label='Dragpoint Initial States', tag="dragpoint_init_state_window", pos=(0, 150), height=400):

            # Button to create new dragpoint
            dpg.add_button(label="Add Dragpoint Initial State", callback=self.callbcak_add_dragpoint)
            
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
            with dpg.table(header_row=True, row_background=True, tag="dragpoint_init_state_table",
                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                           borders_outerV=True, policy=dpg.mvTable_SizingFixedFit):
                
                # Add a colomn for each header item
                for header_text in header_texts:
                    dpg.add_table_column(label=header_text)
                
                # Add a row for each trajectory
                for (n, trajectory) in self.dragpoint_trajectories.items():
                    self.add_row_to_dragpoint_table(n)
        return

    def delete_dragpoint_init_state_window(self):
        dpg.delete_item("dragpoint_init_state_window")
        return

    def add_row_to_dragpoint_table(self, n):
        with dpg.table_row(parent="dragpoint_init_state_table"):
            
            # Ordinal number of dragpoint 
            dpg.add_text(str(n))

            # Chechbox show/hide dragpoint and trajectory
            dpg.add_checkbox(label="", 
                             default_value=True, 
                             callback=self.callback_dragpoint_table_toggle_visibility,
                             user_data={"n":n})

            # Direction of integration combo box
            dpg.add_combo(label="", 
                          tag=f"dragpoint_table_dt_{n}", 
                          width=40,
                          items=self.integrate_directions, 
                          default_value=self.integrate_direction_default, 
                          callback=self.callback_dragpoint_table_change_option,
                          user_data={"n":n})
            
            # Variable input and variable step input for every variable_name
            for (i, variable_name) in enumerate(self.app.variable_names):
                dpg.add_input_float(label="", 
                                    tag=f"dragpoint_table_{variable_name}_{n}", 
                                    default_value=self.dragpoint_table_default_variable_value, 
                                    callback=self.callback_dragpoint_table_change_variable, 
                                    user_data={"n":n},
                                    width=self.dragpoint_table_variable_input_width, 
                                    format=self.dragpoint_table_variable_format,
                                    step=self.dragpoint_table_default_variable_step_value)
        
                # Context menu for variable input
                with dpg.popup(parent=dpg.last_item()):
                    dpg.add_button(label="Copy name=value", callback=self.callback_dragpoint_table_copy_variable, user_data={"n":n, "variable":variable_name, "name":True})
                    dpg.add_button(label="Copy init state", callback=self.callback_dragpoint_table_copy_init_state, user_data={"n":n})
                    dpg.add_button(label="Copy last state", callback=self.callback_dragpoint_table_copy_last_state, user_data={"n":n})
                    dpg.add_separator()
                    dpg.add_button(label="Paste init state", callback=self.callback_dragpoint_table_paste_init_state, user_data={"n":n})
                    dpg.add_separator()
                    dpg.add_button(label="Copy trajectory as python lists", callback=self.callback_dragpoint_table_copy_trajectory, user_data={"n":n, "type":"python"})
                    dpg.add_button(label="Copy trajectory as numpy array", callback=self.callback_dragpoint_table_copy_trajectory, user_data={"n":n, "type":"numpy"})

                # Variable step input
                dpg.add_input_float(label="", 
                                    tag=f"dragpoint_table_{variable_name}_step_{n}", 
                                    default_value=self.dragpoint_table_default_variable_step_value, 
                                    callback=self.callback_dragpoint_table_change_variable_step, 
                                    width=self.dragpoint_table_variable_step_input_width, 
                                    format=self.dragpoint_table_variable_step_format,
                                    step=0.0)
            
            # Integration start, end and steps inputs
            dpg.add_input_float(label="", 
                                tag=f"dragpoint_table_t_start_{n}",
                                callback=self.callback_dragpoint_table_change_option,
                                user_data={"n":n},
                                default_value=self.dragpoint_table_default_t_start, 
                                width=self.dragpoint_table_option_input_width,
                                step=0.0)
            dpg.add_input_float(label="", 
                                tag=f"dragpoint_table_t_end_{n}",
                                callback=self.callback_dragpoint_table_change_option,
                                user_data={"n":n},
                                default_value=self.dragpoint_table_default_t_end, 
                                width=self.dragpoint_table_option_input_width,
                                step=0.0)
            dpg.add_input_int(label="", 
                              tag=f"dragpoint_table_t_steps_{n}",
                              callback=self.callback_dragpoint_table_change_option,
                              user_data={"n":n},
                              default_value=self.dragpoint_table_default_t_steps, 
                              width=self.dragpoint_table_option_input_width,
                              step=0.0)
        return

    def update_from_dragpoint_to_dragpoint_table(self, n):
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()

        # Get dragpoint position
        x_dragpoint, y_dragpoint = dpg.get_value(f"dragpoint_{n}")
        if x_axis_i != len(self.app.variable_names):
            dpg.set_value(f"dragpoint_table_{x_axis_label}_{n}", x_dragpoint)
        if y_axis_i != len(self.app.variable_names):
            dpg.set_value(f"dragpoint_table_{y_axis_label}_{n}", y_dragpoint)
        return

    def update_from_dragpoint_table_to_dragpoint(self, n):
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()

        if x_axis_i == len(self.app.variable_names) and y_axis_i == len(self.app.variable_names):
            dpg.set_value(f"dragpoint_{n}", [0.0, 0.0])
            return
        if x_axis_i == len(self.app.variable_names):
            y_data = dpg.get_value(f"dragpoint_table_{y_axis_label}_{n}")
            dpg.set_value(f"dragpoint_{n}", [0.0, y_data])
            return
        if y_axis_i == len(self.app.variable_names):
            x_data = dpg.get_value(f"dragpoint_table_{x_axis_label}_{n}")
            dpg.set_value(f"dragpoint_{n}", [x_data, 0.0])
            return
        x_data = dpg.get_value(f"dragpoint_table_{x_axis_label}_{n}")
        y_data = dpg.get_value(f"dragpoint_table_{y_axis_label}_{n}")
        dpg.set_value(f"dragpoint_{n}", [x_data, y_data])
        return
    
    def update_from_dragpoint_table_to_trajectory(self, n):
        # Get parameters from GUI
        pars = [dpg.get_value(parameter_name) for parameter_name in self.app.parameter_names]
        integration_t_start = dpg.get_value(f"dragpoint_table_t_start_{n}")
        integration_t_end = dpg.get_value(f"dragpoint_table_t_end_{n}")
        integration_t_steps = dpg.get_value(f"dragpoint_table_t_steps_{n}")
        dt = dpg.get_value(f"dragpoint_table_dt_{n}")
        if dt == "-":
            integration_t_start, integration_t_end = integration_t_end, integration_t_start

        # Get init state from table
        init_state = self.get_dragpoint_table_init_state(n)

        # Reintegrate with new parameters
        trajectory = self.dragpoint_trajectories[n]
        trajectory.init_state = init_state
        trajectory.integrate_scipy(self.app.ODEs, init_state, pars, integration_t_start, integration_t_end, integration_t_steps)
        return

    def update_from_dragpoint_trajectory_to_plot(self, n):
        _, _, x_axis_i, y_axis_i = self.get_axis_labels()

        sol, t_sol = self.dragpoint_trajectories[n].sol, self.dragpoint_trajectories[n].t_sol
        if x_axis_i == len(self.app.variable_names):
            x_axis_data = t_sol
        else:
            x_axis_data = sol[x_axis_i]

        if y_axis_i == len(self.app.variable_names):
            y_axis_data = t_sol
        else:
            y_axis_data = sol[y_axis_i]
        dpg.set_value(f"dragpoint_plot_{n}", [x_axis_data, y_axis_data])
        return

    def callback_dragpoint_table_change_option(self, sender, app_data, user_data):
        n = user_data["n"]
        self.update_from_dragpoint_table_to_trajectory(n)
        self.update_from_dragpoint_trajectory_to_plot(n)
        return

    def callback_dragpoint_table_change_variable(self, sender, app_data, user_data):
        n = user_data["n"]
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_dragpoint_table_to_trajectory(n)
        self.update_from_dragpoint_trajectory_to_plot(n)
        return

    def callback_dragpoint_table_change_variable_step(self, sender, app_data):
        for (n, trajectory) in self.dragpoint_trajectories.items():
            for (i, variable_name) in enumerate(self.app.variable_names):
                new_step = dpg.get_value(f"dragpoint_table_{variable_name}_step_{n}")
                dpg.configure_item(f"dragpoint_table_{variable_name}_{n}", step=new_step)
        return

    def callbcak_add_dragpoint(self, sender, app_data):
        # New ordinal number bigger then others, create new trajectory
        n_new = max(self.dragpoint_trajectories.keys())+1
        trajectory_new = Trajectory()
        self.dragpoint_trajectories[n_new] = trajectory_new

        # New row in the dragpoint table
        self.add_row_to_dragpoint_table(n_new)
        
        # Add new dragpoint and plot
        dpg.add_drag_point(label=f"Init. State {n_new}",
                        tag=f"dragpoint_{n_new}", 
                        parent="phase_space_plot",
                        callback=self.callback_change_dragpoint_position, 
                        user_data={"n":n_new},
                        color=[255, 0, 0, 150])
        dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag=f"dragpoint_plot_{n_new}")

        # Refresh this trajectory
        self.update_from_dragpoint_to_dragpoint_table(n_new)
        self.update_from_dragpoint_table_to_dragpoint(n_new)
        self.update_from_dragpoint_table_to_trajectory(n_new)
        self.update_from_dragpoint_trajectory_to_plot(n_new)
        return

    def callback_dragpoint_table_toggle_visibility(self, sender, app_data, user_data):
        n = user_data["n"]
        show = dpg.get_value(sender) 
        if show:
            dpg.show_item(f"dragpoint_{n}")
            dpg.show_item(f"dragpoint_plot_{n}")
        else:
            dpg.hide_item(f"dragpoint_{n}")
            dpg.hide_item(f"dragpoint_plot_{n}")
        return
    
    def callback_dragpoint_table_copy_variable(self, sender, app_data, user_name):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Get variable_name and n from the layout of the context menu
        n = user_name["n"]
        variable_name = user_name["variable"]
        include_name = user_name["name"]
        tag = f"dragpoint_table_{variable_name}_{n}"
        
        if include_name:
            clip.copy(f"{variable_name}={dpg.get_value(tag)}")
        else:
            clip.copy(f"{dpg.get_value(tag)}")
        return

    def callback_dragpoint_table_copy_init_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Create a strings of "var_n=val_n"
        n = user_data["n"]
        init_state = self.get_dragpoint_table_init_state(n)
        result = [f"{variable_name}={init_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = self.separator_default
        if self.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return

    def callback_dragpoint_table_paste_init_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]

        # Read the clipboard
        variable_values_str = clip.paste().replace(" ", "")

        for sep in self.separators_supported:
            if sep not in variable_values_str:
                continue
            variable_values_split = variable_values_str.split(sep)
            for split in variable_values_split:
                variable_name = split[:split.find("=")]
                variable_value = split[split.find("=")+1:]
                dpg.set_value(f"dragpoint_table_{variable_name}_{n}", float(variable_value))
        self.update_from_dragpoint_table_to_dragpoint(n)
        self.update_from_dragpoint_table_to_trajectory(n)
        self.update_from_dragpoint_trajectory_to_plot(n)
        return
    
    def callback_dragpoint_table_copy_last_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]
        last_state = self.get_dragpoint_last_state(n)
        result = [f"{variable_name}={last_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = self.separator_default
        if self.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_dragpoint_table_copy_trajectory(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]
        trajectory = self.dragpoint_trajectories[n]

        copy_type = user_data["type"]
        if copy_type == "python":
            lines = [f"{variable_name} = {trajectory.sol[i].tolist()}" for (i,variable_name) in enumerate(self.app.variable_names)]
            lines.append(f"t = {trajectory.t_sol.tolist()}")
        elif copy_type == "numpy":
            lines = [f"{variable_name} = np.array({trajectory.sol[i].tolist()})" for (i,variable_name) in enumerate(self.app.variable_names)]
            lines.append(f"t = np.array({trajectory.t_sol.tolist()})")

        result = "\n".join(lines)
        clip.copy(result)
        return