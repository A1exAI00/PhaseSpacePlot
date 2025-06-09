import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from App import App
from utils.EventManager import EventManager

# For VSCode autocomplete, to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.WorkbenchPhaseSpace import WorkbenchPhaseSpace

#########################################################################################

class WindowParameters:
    def __init__(self, app:App, parent:"WorkbenchPhaseSpace", event_manager:EventManager) -> None:
        self._app:App = app
        self._parent:"WorkbenchPhaseSpace" = parent
        self._event_manager:EventManager = event_manager

        # Defaults
        self._parameter_default = 0.1
        self._parameter_step_default = 1e-2

        # GUI
        self._window_label = "Dynamical System Parameters"
        self._parameter_format = "%f"
        self._parameter_step_format = "%.2E"
        self._parameter_input_width = 130
        self._parameter_step_input_window = 65

        self._event_changed_parameter = "changed_dynamical_system_parameter"

        return None
    
    def get_parameters(self):
        return [dpg.get_value(parameter_name) for parameter_name in self._app.parameter_names]
    
    def setup_window(self):
        with dpg.window(label=self._window_label, tag="dynamical_system_parameters_window", pos=(0,0)):
            for (i, parameter_name) in enumerate(self._app.parameter_names):

                # Create a row of parameter input and a parameter step input for every parameter_name
                with dpg.group(horizontal=True) as group:
                    dpg.add_input_float(label=parameter_name, tag=parameter_name, 
                                        default_value=self._parameter_default, 
                                        callback=self.callback_change_parameter, 
                                        width=self._parameter_input_width, 
                                        format=self._parameter_format, 
                                        step=self._parameter_step_default)
                    dpg.add_input_float(label=parameter_name+" step", tag=parameter_name+"_step", 
                                        default_value=self._parameter_step_default, 
                                        callback=self.callback_change_parameter_step,
                                        width=self._parameter_step_input_window, step=0.0, 
                                        format=self._parameter_step_format)
                    
                    # Create a contect menu for the parameter
                with dpg.popup(parent=group, no_move=True):
                    dpg.add_button(label="Copy parameter name=value", callback=self.callback_copy_parameter_value, user_data={"parameter_name":parameter_name, "name":True})
                    dpg.add_button(label="Copy all parameter values", callback=self.callback_copy_all_parameter_values)
                    dpg.add_button(label="Paste all parameter values", callback=self.callback_paste_all_parameter_values)
        return

    def delete_dynamical_system_parameters_window(self):
        dpg.delete_item("dynamical_system_parameters_window")
        return
    
    def callback_change_parameter(self, sender, app_data, user_data):
        self._event_manager.publish(self._event_changed_parameter, data={})
        return
    
    def callback_change_parameter_step(self, sender, app_data, user_data):
        for (i, parameter_name) in enumerate(self._app.parameter_names):
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
    
    def callback_copy_all_parameter_values(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Create a strings of "par_n=val_n"
        result = [f"{parameter_name}={dpg.get_value(parameter_name)}" for parameter_name in self._app.parameter_names]

        sep = self._parent.separator_default
        if self._parent.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_paste_all_parameter_values(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Read clipboard
        parameter_values_str = clip.paste().replace(" ", "")

        # For every separator, check if it is used, split with ir, split with "=" and set parameter
        for sep in self._parent.separators_supported:
            if sep not in parameter_values_str:
                continue
            parameter_values_split = parameter_values_str.split(sep)
            for split in parameter_values_split:
                parameter_name = split[:split.find("=")]
                if parameter_name not in self._app.parameter_names:
                    continue
                parameter_value = split[split.find("=")+1:]
                dpg.set_value(parameter_name, float(parameter_value))

        # Refresh all trajectories
        self.callback_change_parameter(None, None)
        return