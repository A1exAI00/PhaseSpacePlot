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

class WindowNearSoE:
    def __init__(self, app:App, parent:"WorkbenchPhaseSpace", event_manager:EventManager):
        self._app:App = app
        self._parent:"WorkbenchPhaseSpace" = parent
        self._event_manager:EventManager = event_manager

        # Defaults
        self._default_variable_value = 0.0
        self._default_autocorrect_value = False
        self._default_eps = 1e-6
        self._default_t_start = 0.0
        self._default_t_end = 10.0
        self._default_t_steps = 1000

        # GUI
        self._window_label = "Near SoE Initial States"
        self._variable_format = "%f"
        self._eps_input_format = "%.1E"
        self._variable_input_width = 85
        self._option_input_width = 55

        self._event_added_init_state = "added_init_state"
        self._event_corrected_SoE = "corrected_SoE"
        self._event_changed_table_option = "changed_init_state_table_option"
        self._event_toggled_show = "changed_toggled_show"
        self._event_toggled_autocorrect = "changed_toggled_autocorrect"

        return
    
    def get_SoE_coordinates(self, n:int):
        variable_tags = [self.get_variable_tag(variable_name, n) for (i, variable_name) in enumerate(self._app.variable_names)]
        return np.array(dpg.get_values(variable_tags))
    
    def get_variable_tag(self, variable_name, n):
        return f"near_SoE_table_{variable_name}_{n}"
    
    def get_variable(self, variable_name, n):
        return dpg.get_value(self.get_variable_tag(variable_name, n))
    
    def set_variable(self, variable_name, n, value):
        dpg.set_value(self.get_variable_tag(variable_name, n), value)
        return
    
    def get_last_state(self, n):
        last_state = self._parent.get_trajectory(n).get_last_state()
        return last_state
    
    def setup_window(self):
        with dpg.window(label=self._window_label, tag="near_SoE_init_state_window", pos=(0, 300), height=400):

            # Button to create new init state
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Initial State", callback=self.callbcak_add_init_state)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Correct All", callback=self.callback_correct_SoE, user_data={"n":-1})
            
            # Create a list of headers for near SoE table
            header_texts = ["n", "show", "autocor", "correct", "dt", "eps", *self._app.variable_names, "eig. N", "eig. dir.", "t start", "t end", "t steps"]
        
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            # Create a table for near SoE init states
            with dpg.table(header_row=True, row_background=True, tag="near_SoE_init_state_table",
                           borders_innerH=True, borders_outerH=True, borders_innerV=True,
                           borders_outerV=True, policy=dpg.mvTable_SizingFixedFit):
                
                # Add a colomn for each header item
                for header_text in header_texts:
                    dpg.add_table_column(label=header_text)
        return
    
    def delete_near_SoE_init_state_window(self):
        dpg.delete_item("near_SoE_init_state_window")
        return

    def add_row_to_table(self, n):
        with dpg.table_row(parent="near_SoE_init_state_table"):
            
            # Ordinal number of init state 
            dpg.add_text(str(n))

            # Chechbox show/hide trajectory
            dpg.add_checkbox(label="", 
                             tag=f"show_{n}",
                             default_value=True, 
                             callback=self.callback_table_toggle_show,
                             user_data={"n":n})
            
            # Chechbox for autocorrection
            dpg.add_checkbox(label="", 
                             tag=f"autocorrect_{n}",
                             default_value=self._default_autocorrect_value, 
                             callback=self.callback_table_toggle_autocorrect,
                             user_data={"n":n})
            
            # Button to correct coordinates of SoE
            dpg.add_button(label="Correct",
                           callback=self.callback_correct_SoE,
                           user_data={"n":n}) 

            # Combo box for directions of integration
            dpg.add_combo(label="", 
                          tag=f"near_SoE_table_dt_{n}", 
                          width=20,
                          items=self._parent._integrate_directions, 
                          default_value=self._parent._integrate_direction_default, 
                          callback=self.callback_table_change_option,
                          user_data={"n":n},
                          no_arrow_button=True)

            # Input for eps
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_eps_{n}", 
                                default_value=self._default_eps, 
                                callback=self.callback_table_change_option, 
                                user_data={"n":n},
                                width=self._option_input_width, 
                                format=self._eps_input_format,
                                step=0.0)

            # Variable input and variable step input for every variable_name
            for (i, variable_name) in enumerate(self._app.variable_names):
                dpg.add_input_float(label="", 
                                    tag=self.get_variable_tag(variable_name, n), 
                                    default_value=self._default_variable_value, 
                                    callback=self.callback_table_change_option, 
                                    user_data={"n":n},
                                    width=self._variable_input_width, 
                                    format=self._variable_format,
                                    step=0.0)
        
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

            # Combo box for eigenvalues
            dpg.add_input_int(label="", 
                              tag=f"near_SoE_table_eig_N_{n}",
                              callback=self.callback_table_change_option,
                              user_data={"n":n},
                              default_value=0, 
                              width=self._option_input_width,
                              step=0.0)
            
            with dpg.popup(parent=dpg.last_item()):
                dpg.add_text("", tag=f"near_SoE_eigenvalue_popup_text_{n}")
                dpg.add_button(label="Copy eigenvalues", callback=self.callback_table_copy_eigen, user_data={"n":n, "type":"python"})
                dpg.add_text("", tag=f"near_SoE_eigenvector_popup_text_{n}")
                dpg.add_button(label="Copy eigenvectors", callback=self.callback_table_copy_eigen, user_data={"n":n, "type":"python"})
            
            # Combo box for eigenvectors
            dpg.add_combo(label="", 
                          tag=f"near_SoE_table_eig_dir_{n}", 
                          width=20,
                          items=["+", "-"], 
                          default_value="+", 
                          callback=self.callback_table_change_option,
                          user_data={"n":n},
                          no_arrow_button=True)

            # Integration start, end and steps inputs
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_t_start_{n}",
                                callback=self.callback_table_change_option,
                                user_data={"n":n},
                                default_value=self._default_t_start, 
                                width=self._option_input_width,
                                step=0.0)
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_t_end_{n}",
                                callback=self.callback_table_change_option,
                                user_data={"n":n},
                                default_value=self._default_t_end, 
                                width=self._option_input_width,
                                step=0.0)
            dpg.add_input_int(label="", 
                              tag=f"near_SoE_table_t_steps_{n}",
                              callback=self.callback_table_change_option,
                              user_data={"n":n},
                              default_value=self._default_t_steps, 
                              width=self._option_input_width,
                              step=0.0)
        return
    
    def update_variable(self, variable_name, n, value):
        dpg.set_value(self.get_variable_tag(variable_name, n), value)
        return
    
    def callbcak_add_init_state(self, sender, app_data, user_data):
        keys = self._parent._trajectories.keys()
        n_new = 0 if (len(keys) == 0) else max(keys)+1

        self.add_row_to_table(n_new)

        self._event_manager.publish(self._event_added_init_state, data={"n":n_new, "draginit":False})

        self._event_manager.publish(self._event_changed_table_option, data={"n":n_new})
        return
    
    def callback_table_toggle_show(self, sender, app_data, user_data):
        n = user_data["n"]
        draginit = False
        show = dpg.get_value(sender)
        _data = {"n":n, "draginit":draginit, "show":show}
        self._event_manager.publish(self._event_toggled_show, data=_data)
        return
    
    def callback_table_toggle_autocorrect(self, sender, app_data, user_data):
        n = user_data["n"]
        autocorrect = dpg.get_value(sender)
        _data = {"n":n, "autocorrect":autocorrect}
        self._event_manager.publish(self._event_toggled_autocorrect, data=_data)
        return
    
    def callback_correct_SoE(self, sender, app_data, user_data):
        self._event_manager.publish(self._event_corrected_SoE, data=user_data)
        return
    
    def callback_table_change_option(self, sender, app_data, user_data):
        self._event_manager.publish(self._event_changed_table_option, data=user_data)
        return
    
    def callback_table_copy_variable(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Get variable_name and n from the layout of the context menu
        n = user_data["n"]
        variable_name = user_data["variable"]
        include_name = user_data["name"]
        value = self.get_variable(variable_name, n)
        
        if include_name:
            clip.copy(f"{variable_name}={value}")
        else:
            clip.copy(f"{value}")
        return
    
    def callback_table_copy_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]
        state_type = user_data["state_type"]

        if (state_type == "init_state"):
            state = self.get_SoE_coordinates(n)
        elif (state_type == "last_state"):
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

        _data = {"n":n}
        self._event_manager.publish(self._event_changed_table_option, data=_data)
        return
    
    def callback_table_copy_trajectory(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]
        trajectory = self._parent.get_trajectory(n)

        copy_type = user_data["type"]
        if copy_type == "python":
            lines = [f"{variable_name} = {trajectory.sol[i].tolist()}" for (i,variable_name) in enumerate(self._app.variable_names)]
            lines.append(f"t = {trajectory.t_sol.tolist()}")
        elif copy_type == "numpy":
            lines = [f"{variable_name} = np.array({trajectory.sol[i].tolist()})" for (i,variable_name) in enumerate(self._app.variable_names)]
            lines.append(f"t = np.array({trajectory.t_sol.tolist()})")

        result = "\n".join(lines)
        clip.copy(result)
        return
    
    def callback_table_copy_eigen(self, sender, app_data, user_data): # TODO finish
        # Hide context menu
        # dpg.hide_item(dpg.get_item_parent(sender))

        # n = user_data["n"]
        # format_type = user_data["format_type"]
        # eigen_type = user_data["eigen_type"]

        # if format_type == "python":
        #     if eigen_type == "eigenvalue":

        #     texts = [f"{eigen_type}_{i} = {self.near_SoE_eigenvalues[n][i]}" for i in range(len(self.app.variable_names))]
        #     text = "\n".join(texts)
        # else:
        #     return
        # clip.copy(eigenvalues_text)
        return