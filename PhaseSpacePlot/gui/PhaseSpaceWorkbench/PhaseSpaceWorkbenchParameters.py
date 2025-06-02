import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

#########################################################################################

class PhaseSpaceWorkbenchParameters:
    def setup_dynamical_system_parameters_window(self):
        with dpg.window(label='Dynamical System Parameters', tag="dynamical_system_parameters_window", pos=(0,0)):
            for (i, parameter_name) in enumerate(self.app.parameter_names):

                # Create a row of parameter input and a parameter step input for every parameter_name
                with dpg.group(horizontal=True) as group:
                    dpg.add_input_float(label=parameter_name, tag=parameter_name, 
                                        default_value=self.parameter_default, 
                                        callback=self.callback_change_parameter, 
                                        width=self.parameter_input_width, 
                                        format=self.parameter_format, 
                                        step=self.parameter_step_default)
                    dpg.add_input_float(label=parameter_name+" step", tag=parameter_name+"_step", 
                                        default_value=self.parameter_step_default, 
                                        callback=self.callback_change_parameter_step,
                                        width=self.parameter_step_input_window, step=0.0, 
                                        format=self.parameter_step_format)
                    
                    # Create a contect menu for the parameter
                with dpg.popup(parent=group, no_move=True):
                    dpg.add_button(label="Copy parameter name=value", callback=self.callback_copy_parameter_value, user_data={"parameter_name":parameter_name, "name":True})
                    dpg.add_button(label="Copy all parameter values", callback=self.callback_copy_all_parameter_values)
                    dpg.add_button(label="Paste all parameter values", callback=self.callback_paste_all_parameter_values)
        return

    def delete_dynamical_system_parameters_window(self):
        dpg.delete_item("dynamical_system_parameters_window")
        return
    
    def callback_change_parameter(self, sender, app_data):
        for (n, trajectory) in self.dragpoint_trajectories.items():
            self.update_from_dragpoint_table_to_trajectory(n)
            self.update_from_dragpoint_trajectory_to_plot(n)
        for (n, trajectory) in self.near_SoE_trajectories.items():
            if self.near_SoE_autocorrect[n]:
                self.callback_near_SoE_table_correct(None, None, {"n":n})
            self.update_from_near_SoE_table_to_trajectory(n)
            self.update_from_near_SoE_trajectory_to_plot(n)
        return
    
    def callback_change_parameter_step(self, sender, app_data):
        for (i, parameter_name) in enumerate(self.app.parameter_names):
            new_step = dpg.get_value(f"{parameter_name}_step")
            dpg.configure_item(parameter_name, step=new_step)
        return
    
    def callback_copy_parameter_value(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Get parameter_name from the layout of the context menu
        parameter_name = user_data["parameter_name"]
        include_name = user_data["name"]

        if include_name:
            clip.copy(f"{parameter_name}={dpg.get_value(parameter_name)}")
        else:
            clip.copy(f"{dpg.get_value(parameter_name)}")
        return

    def callback_copy_all_parameter_values(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Create a strings of "par_n=val_n"
        result = [f"{parameter_name}={dpg.get_value(parameter_name)}" for parameter_name in self.app.parameter_names]

        sep = self.separator_default
        if self.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_paste_all_parameter_values(self, sender, app_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Read clipboard
        parameter_values_str = clip.paste().replace(" ", "")

        # For every separator, check if it is used, split with ir, split with "=" and set parameter
        for sep in self.separators_supported:
            if sep not in parameter_values_str:
                continue
            parameter_values_split = parameter_values_str.split(sep)
            for split in parameter_values_split:
                parameter_name = split[:split.find("=")]
                if parameter_name not in self.app.parameter_names:
                    continue
                parameter_value = split[split.find("=")+1:]
                dpg.set_value(parameter_name, float(parameter_value))

        # Refresh all trajectories
        self.callback_change_parameter(None, None)
        return