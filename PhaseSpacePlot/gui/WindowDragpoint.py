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

class WindowDragpoint:
    def __init__(self, app:App, parent:"WorkbenchPhaseSpace", event_manager:EventManager):
        self._app:App = app
        self._parent:"WorkbenchPhaseSpace" = parent
        self._event_manager:EventManager = event_manager

        # Defaults
        self._dragpoint_table_default_variable_value = 0.0
        self._dragpoint_table_default_variable_step_value = 1e-2
        self._dragpoint_table_default_t_start = 0.0
        self._dragpoint_table_default_t_end = 10.0
        self._dragpoint_table_default_t_steps = 1000

        # GUI
        self._window_label = "Dragpoint Initial States"
        self._window_tag = "dragpoint_init_state_window"
        self._dragpoint_table_variable_format = "%f"
        self._dragpoint_table_variable_step_format = "%.2E"
        self._dragpoint_table_variable_input_width = 110
        self._dragpoint_table_variable_step_input_width = 65
        self._dragpoint_table_option_input_width = 55

        # Events this class publishes in its methods
        self._event_added_init_state = "added_init_state"
        self._event_changed_table_option = "changed_init_state_table_option"
        self._event_toggled_show = "changed_toggled_show"

        self._event_manager.subscribe("changed_dragpoint_position", self.handler_changed_dragpoint_position)
        return
    
    def get_variable_tag(self, variable_name:str, n:int):
        return f"dragpoint_table_{variable_name}_{n}"

    def get_init_state(self, n):
        variable_tags = [self.get_variable_tag(variable_name, n) for (i, variable_name) in enumerate(self._app.variable_names)]
        return np.array(dpg.get_values(variable_tags))
    
    def get_last_state(self, n):
        last_state = self._parent.get_trajectory(n).get_last_state()
        return last_state
    
    def set_variable(self, variable_name:str, n:int, value:float):
        dpg.set_value(self.get_variable_tag(variable_name, n), value)
        return
    
    def setup_window(self):
        with dpg.window(label=self._window_label, tag=self._window_tag, pos=(0, 150), height=400):

            # Button to create new dragpoint
            dpg.add_button(label="Add Dragpoint Initial State", callback=self.callbcak_add_dragpoint)
            
            # Create a list of headers for dragpoint table
            header_for_variables = []
            for (i,variable_name) in enumerate(self._app.variable_names):
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
        return

    def delete_dragpoint_init_state_window(self):
        dpg.delete_item(self._window_tag)
        return

    def add_row_to_table(self, n):
        with dpg.table_row(parent="dragpoint_init_state_table"):
            
            # Ordinal number of dragpoint 
            dpg.add_text(str(n))

            # Chechbox show/hide dragpoint and trajectory
            dpg.add_checkbox(label="", 
                             tag=f"show_{n}",
                             default_value=True, 
                             callback=self.callback_table_toggle_show,
                             user_data={"n":n})

            # Direction of integration combo box
            dpg.add_combo(label="", 
                          tag=f"dragpoint_table_dt_{n}", 
                          width=20,
                          items=self._parent._integrate_directions, 
                          default_value=self._parent._integrate_direction_default, 
                          callback=self.callback_table_change_option,
                          user_data={"n":n},
                          no_arrow_button=True)
            
            # Variable input and variable step input for every variable_name
            for (i, variable_name) in enumerate(self._app.variable_names):
                dpg.add_input_float(label="", 
                                    tag=self.get_variable_tag(variable_name, n), 
                                    default_value=self._dragpoint_table_default_variable_value, 
                                    callback=self.callback_table_change_option, 
                                    user_data={"n":n},
                                    width=self._dragpoint_table_variable_input_width, 
                                    format=self._dragpoint_table_variable_format,
                                    step=self._dragpoint_table_default_variable_step_value)
        
                # Context menu for variable input
                with dpg.popup(parent=dpg.last_item()):
                    dpg.add_button(label="Copy name=value", callback=self.callback_table_copy_variable, user_data={"n":n, "variable":variable_name, "name":True})
                    dpg.add_button(label="Copy init state", callback=self.callback_table_copy_state, user_data={"n":n, "state_type":"init_state"})
                    dpg.add_button(label="Copy last state", callback=self.callback_table_copy_state, user_data={"n":n, "state_type":"last_state"})
                    dpg.add_separator()
                    dpg.add_button(label="Paste init state", callback=self.callback_table_paste_init_state, user_data={"n":n})
                    dpg.add_separator()
                    dpg.add_button(label="Copy trajectory as python lists", callback=self.callback_table_copy_trajectory, user_data={"n":n, "type":"python"})
                    dpg.add_button(label="Copy trajectory as numpy array", callback=self.callback_table_copy_trajectory, user_data={"n":n, "type":"numpy"})

                # Variable step input
                dpg.add_input_float(label="", 
                                    tag=f"dragpoint_table_{variable_name}_step_{n}", 
                                    default_value=self._dragpoint_table_default_variable_step_value, 
                                    callback=self.callback_table_change_variable_step, 
                                    width=self._dragpoint_table_variable_step_input_width, 
                                    format=self._dragpoint_table_variable_step_format,
                                    step=0.0)
            
            # Integration start, end and steps inputs
            dpg.add_input_float(label="", 
                                tag=f"dragpoint_table_t_start_{n}",
                                callback=self.callback_table_change_option,
                                user_data={"n":n},
                                default_value=self._dragpoint_table_default_t_start, 
                                width=self._dragpoint_table_option_input_width,
                                step=0.0)
            dpg.add_input_float(label="", 
                                tag=f"dragpoint_table_t_end_{n}",
                                callback=self.callback_table_change_option,
                                user_data={"n":n},
                                default_value=self._dragpoint_table_default_t_end, 
                                width=self._dragpoint_table_option_input_width,
                                step=0.0)
            dpg.add_input_int(label="", 
                              tag=f"dragpoint_table_t_steps_{n}",
                              callback=self.callback_table_change_option,
                              user_data={"n":n},
                              default_value=self._dragpoint_table_default_t_steps, 
                              width=self._dragpoint_table_option_input_width,
                              step=0.0)
        return
    
    def callbcak_add_dragpoint(self, sender, app_data, user_data):
        # Set new key to 0 or the the next integer above max
        keys = self._parent._trajectories.keys()
        n_new = 0 if (len(keys) == 0) else max(keys)+1

        self.add_row_to_table(n_new)
        self._event_manager.publish(self._event_added_init_state, data={"n":n_new, "draginit":True})
        self._event_manager.publish(self._event_changed_table_option, data={"n":n_new})
        return
    
    def callback_table_toggle_show(self, sender, app_data, user_data):
        n = user_data["n"]
        show = dpg.get_value(sender)
        _data = {"n":n, "show":show, "draginit":True}
        self._event_manager.publish(self._event_toggled_show, data=_data)
        return
    
    def callback_table_change_option(self, sender, app_data, user_data):
        self._event_manager.publish(self._event_changed_table_option, data=user_data)
        return
    
    def callback_table_change_variable_step(self, sender, app_data, user_data):
        for (n, trajectory) in self._parent._trajectories.items():
            for (i, variable_name) in enumerate(self._app.variable_names):
                new_step = dpg.get_value(f"dragpoint_table_{variable_name}_step_{n}")
                dpg.configure_item(self.get_variable_tag(variable_name, n), step=new_step)
        return
    
    def callback_table_copy_variable(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Get variable_name and n from the layout of the context menu
        n = user_data["n"]
        variable_name = user_data["variable"]
        include_name = user_data["name"]
        tag = f"dragpoint_table_{variable_name}_{n}"
        
        if include_name:
            clip.copy(f"{variable_name}={dpg.get_value(tag)}")
        else:
            clip.copy(f"{dpg.get_value(tag)}")
        return
    
    def callback_table_copy_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]
        state_type = user_data["state_type"]

        if state_type == "init_state":
            state = self.get_init_state(n)
        elif state_type == "last_state":
            state = self.get_last_state(n)
        else:
            return
        
        result = [f"{variable_name}={state[i]}" for (i,variable_name) in enumerate(self._app.variable_names)]
        sep = self._parent._separator_default
        if self._parent._separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_table_paste_init_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]

        # Read the clipboard
        variable_values_str = clip.paste().replace(" ", "")

        for sep in self._parent._separators_supported:
            if sep not in variable_values_str:
                continue
            variable_values_split = variable_values_str.split(sep)
            for split in variable_values_split:
                variable_name = split[:split.find("=")]
                variable_value = float(split[split.find("=")+1:])
                self.set_variable(variable_name, n, variable_value)
        
        self._event_manager.publish(self._event_changed_table_option, data={"n":n})
        return
    
    def callback_table_copy_trajectory(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]
        copy_type = user_data["type"]
        trajectory = self._parent.get_trajectory(n)
        
        if copy_type == "python":
            lines = [f"{variable_name} = {trajectory.sol[i].tolist()}" for (i,variable_name) in enumerate(self._app.variable_names)]
            lines.append(f"t = {trajectory.t_sol.tolist()}")
        elif copy_type == "numpy":
            lines = [f"{variable_name} = np.array({trajectory.sol[i].tolist()})" for (i,variable_name) in enumerate(self._app.variable_names)]
            lines.append(f"t = np.array({trajectory.t_sol.tolist()})")

        result = "\n".join(lines)
        clip.copy(result)
        return
    
    def handler_changed_dragpoint_position(self, data:dict):
        m = data["m"] 
        n = data["n"] 
        x_axis_label = data["x_axis_label"]
        y_axis_label = data["y_axis_label"]
        x_axis_i = data["x_axis_i"]
        y_axis_i = data["y_axis_i"]
        x_dragpoint = data["x_dragpoint"]
        y_dragpoint = data["y_dragpoint"]

        if (x_axis_i == len(self._app.variable_names)) and (y_axis_i == len(self._app.variable_names)):
            pass
        elif x_axis_i == len(self._app.variable_names):
            self.set_variable(y_axis_label, n, y_dragpoint)
        elif y_axis_i == len(self._app.variable_names):
            self.set_variable(x_axis_label, n, x_dragpoint)
        else:
            self.set_variable(x_axis_label, n, x_dragpoint)
            self.set_variable(y_axis_label, n, y_dragpoint)
        return