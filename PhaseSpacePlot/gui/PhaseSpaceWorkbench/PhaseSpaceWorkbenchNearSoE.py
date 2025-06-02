import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from utils.integration import Trajectory
from utils.nonlinear_solve import solve, eigenvalues_and_eigenvectors

#########################################################################################

class PhaseSpaceWorkbenchNearSoE:
    def get_near_SoE_table_init_state(self,n):
        variable_tags = [f"near_SoE_table_{variable_name}_{n}" for (i, variable_name) in enumerate(self.app.variable_names)]
        return np.array(dpg.get_values(variable_tags))
    
    def get_near_SoE_last_state(self, n):
        return np.array([self.near_SoE_trajectories[n].sol[i][-1] for (i, variable_name) in enumerate(self.app.variable_names)])
    
    def setup_near_SoE_init_state_window(self):
        with dpg.window(label='Near SoE Initial States', tag="near_SoE_init_state_window", pos=(0, 300), height=400):

            # Button to create new init state
            with dpg.group(horizontal=True):
                dpg.add_button(label="Add Initial State", callback=self.callbcak_add_near_SoE)
                dpg.add_spacer(width=10)
                dpg.add_button(label="Correct All", callback=self.callbcak_near_SoE_correct_all)
            
            # Create a list of headers for near SoE table
            header_texts = ["n", "show", "autocor", "correct", "dt", "eps", *self.app.variable_names, "eig. N", "eig. dir.", "t start", "t end", "t steps"]
        
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
                
                # Add a row for each trajectory
                for (n, trajectory) in self.near_SoE_trajectories.items():
                    self.add_row_to_near_SoE_table(n)
        return
    
    def delete_near_SoE_init_state_window(self):
        dpg.delete_item("near_SoE_init_state_window")
        return
    
    def delete_near_SoE_plot(self, n):
        dpg.set_value(f"near_SoE_plot_{n}", [[], []])
        return
    
    def add_row_to_near_SoE_table(self, n):
        with dpg.table_row(parent="near_SoE_init_state_table"):
            
            # Ordinal number of init state 
            dpg.add_text(str(n))

            # Chechbox show/hide trajectory
            dpg.add_checkbox(label="", 
                             default_value=True, 
                             callback=self.callback_near_SoE_table_toggle_visibility,
                             user_data={"n":n})
            
            # Chechbox for autocorrection
            dpg.add_checkbox(label="", 
                             default_value=self.near_SoE_default_autocorrect_value, 
                             callback=self.callback_near_SoE_table_toggle_autocorrect,
                             user_data={"n":n})
            
            # Button to correct coordinates of SoE
            dpg.add_button(label="Correct",
                           callback=self.callback_near_SoE_table_correct,
                           user_data={"n":n}) 

            # Combo box for directions of integration
            dpg.add_combo(label="", 
                          tag=f"near_SoE_table_dt_{n}", 
                          width=20,
                          items=self.integrate_directions, 
                          default_value=self.integrate_direction_default, 
                          callback=self.callback_near_SoE_table_change_option,
                          user_data={"n":n},
                          no_arrow_button=True)

            # Input for eps
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_eps_{n}", 
                                default_value=self.near_SoE_default_eps, 
                                callback=self.callback_near_SoE_table_change_option, 
                                user_data={"n":n},
                                width=self.near_SoE_option_input_width, 
                                format=self.near_SoE_eps_input_format,
                                step=0.0)

            # Variable input and variable step input for every variable_name
            for (i, variable_name) in enumerate(self.app.variable_names):
                dpg.add_input_float(label="", 
                                    tag=f"near_SoE_table_{variable_name}_{n}", 
                                    default_value=self.near_SoE_default_variable_value, 
                                    callback=self.callback_near_SoE_table_change_option, 
                                    user_data={"n":n},
                                    width=self.near_SoE_variable_input_width, 
                                    format=self.near_SoE_variable_format,
                                    step=0.0)
        
                # Context menu for variable input
                with dpg.popup(parent=dpg.last_item()):
                    dpg.add_button(label="Copy name=value", callback=self.callback_near_SoE_table_copy_variable, user_data={"n":n, "variable":variable_name, "name":True})
                    dpg.add_button(label="Copy init state", callback=self.callback_near_SoE_table_copy_init_state, user_data={"n":n})
                    dpg.add_button(label="Copy last state", callback=self.callback_near_SoE_table_copy_last_state, user_data={"n":n})
                    dpg.add_separator()
                    dpg.add_button(label="Paste init state", callback=self.callback_near_SoE_table_paste_init_state, user_data={"n":n})
                    dpg.add_separator()
                    dpg.add_button(label="Copy trajectory as python lists", callback=self.callback_near_SoE_table_copy_trajectory, user_data={"n":n, "type":"python"})
                    dpg.add_button(label="Copy trajectory as numpy array", callback=self.callback_near_SoE_table_copy_trajectory, user_data={"n":n, "type":"numpy"})

            # Combo box for eigenvalues
            dpg.add_input_int(label="", 
                              tag=f"near_SoE_table_eig_N_{n}",
                              callback=self.callback_near_SoE_table_change_option,
                              user_data={"n":n},
                              default_value=0, 
                              width=self.near_SoE_option_input_width,
                              step=0.0)
            
            with dpg.popup(parent=dpg.last_item()):
                dpg.add_text("", tag=f"near_SoE_eigenvalue_popup_text_{n}")
                dpg.add_button(label="Copy eigenvalues", callback=self.callback_near_SoE_table_copy_eigenvalues, user_data={"n":n, "type":"python"})
                dpg.add_text("", tag=f"near_SoE_eigenvector_popup_text_{n}")
                dpg.add_button(label="Copy eigenvectors", callback=self.callback_near_SoE_table_copy_eigenvectors, user_data={"n":n, "type":"python"})
            
            # Combo box for eigenvectors
            dpg.add_combo(label="", 
                          tag=f"near_SoE_table_eig_dir_{n}", 
                          width=20,
                          items=["+", "-"], 
                          default_value="+", 
                          callback=self.callback_near_SoE_table_change_option,
                          user_data={"n":n},
                          no_arrow_button=True)

            # Integration start, end and steps inputs
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_t_start_{n}",
                                callback=self.callback_near_SoE_table_change_option,
                                user_data={"n":n},
                                default_value=self.near_SoE_default_t_start, 
                                width=self.near_SoE_option_input_width,
                                step=0.0)
            dpg.add_input_float(label="", 
                                tag=f"near_SoE_table_t_end_{n}",
                                callback=self.callback_near_SoE_table_change_option,
                                user_data={"n":n},
                                default_value=self.near_SoE_default_t_end, 
                                width=self.near_SoE_option_input_width,
                                step=0.0)
            dpg.add_input_int(label="", 
                              tag=f"near_SoE_table_t_steps_{n}",
                              callback=self.callback_near_SoE_table_change_option,
                              user_data={"n":n},
                              default_value=self.near_SoE_default_t_steps, 
                              width=self.near_SoE_option_input_width,
                              step=0.0)
        return
    
    def update_from_near_SoE_table_to_trajectory(self, n):
        # Get parameters and options from GUI
        pars = [dpg.get_value(parameter_name) for parameter_name in self.app.parameter_names]
        integration_t_start = dpg.get_value(f"near_SoE_table_t_start_{n}")
        integration_t_end = dpg.get_value(f"near_SoE_table_t_end_{n}")
        integration_t_steps = dpg.get_value(f"near_SoE_table_t_steps_{n}")
        dt = dpg.get_value(f"near_SoE_table_dt_{n}")
        if dt == "-":
            integration_t_start, integration_t_end = integration_t_end, integration_t_start

        eig_N = dpg.get_value(f"near_SoE_table_eig_N_{n}")
        eigenvector = self.near_SoE_eigenvectors[n][eig_N]
        eps = dpg.get_value(f"near_SoE_table_eps_{n}")
        eig_dir = dpg.get_value(f"near_SoE_table_eig_dir_{n}")
        eig_dir_numerical = 1
        if eig_dir == "-":
            eig_dir_numerical = -1

        # Get init state from table
        try:
            init_state = self.get_near_SoE_table_init_state(n) + eps * eig_dir_numerical * eigenvector
        except:
            return

        # Reintegrate with new parameters and options
        trajectory = self.near_SoE_trajectories[n]
        trajectory.integrate_scipy(self.app.ODEs, init_state, pars, integration_t_start, integration_t_end, integration_t_steps)
        return
    
    def update_from_near_SoE_trajectory_to_plot(self, n):
        _, _, x_axis_i, y_axis_i = self.get_axis_labels()

        sol, t_sol = self.near_SoE_trajectories[n].sol, self.near_SoE_trajectories[n].t_sol
        if (sol is None) or (t_sol is None):
            return
        if x_axis_i == len(self.app.variable_names):
            x_axis_data = t_sol
        else:
            x_axis_data = sol[x_axis_i]

        if y_axis_i == len(self.app.variable_names):
            y_axis_data = t_sol
        else:
            y_axis_data = sol[y_axis_i]
        dpg.set_value(f"near_SoE_plot_{n}", [x_axis_data, y_axis_data])
        return
    
    def callbcak_add_near_SoE(self, sender, app_data, user_data):
        n_max = max(self.near_SoE_trajectories.keys())
        n_new = n_max + 1

        trajectory_new = Trajectory()
        self.near_SoE_trajectories[n_new] = trajectory_new
        self.near_SoE_autocorrect[n_new] = self.near_SoE_default_autocorrect_value
        self.near_SoE_eigenvalues[n_new] = []
        self.near_SoE_eigenvectors[n_new] = []

        self.add_row_to_near_SoE_table(n_new)
        dpg.add_line_series([], [], label='PhaseSpacePlot', parent='y_axis', tag=f"near_SoE_plot_{n_new}")

        if not self.near_SoE_autocorrect[n_new]:
            return

        self.update_from_near_SoE_table_to_trajectory(n_new)
        self.update_from_near_SoE_trajectory_to_plot(n_new)
        return
    
    def callback_near_SoE_table_toggle_visibility(self, sender, app_data, user_data):
        n = user_data["n"]
        show = dpg.get_value(sender) 
        if show:
            dpg.show_item(f"near_SoE_plot_{n}")
        else:
            dpg.hide_item(f"near_SoE_plot_{n}")
        return
    
    def callback_near_SoE_table_toggle_autocorrect(self, sender, app_data, user_data):
        n = user_data["n"]
        self.near_SoE_autocorrect[n] = dpg.get_value(sender)

        if self.near_SoE_autocorrect[n]:
            self.callback_near_SoE_table_correct(None, None, {"n":n})
        return
    
    def callback_near_SoE_table_correct(self, sender, app_data, user_data):
        n = user_data["n"]

        current_eig_N = dpg.get_value(f"near_SoE_table_eig_N_{n}")

        # if incorrect current_eig_N
        if (current_eig_N < 0) or (current_eig_N > len(self.app.variable_names)):
            return
        
        # Get init state from table
        init_state = self.get_near_SoE_table_init_state(n)

        # Get DS parameters
        parameter_values = [dpg.get_value(parameter_name) for parameter_name in self.app.parameter_names]

        # Solve for SoE
        new_init_state, success = solve(self.app.ODEs, init_state, parameter_values)

        # If calculation is not successful
        if not success:
            return

        # Set SoE coordinates
        for (i, variable_name) in enumerate(self.app.variable_names):
            dpg.set_value(f"near_SoE_table_{variable_name}_{n}", new_init_state[i])

        # Calc ad save eigenvalues and eigenvectors
        _eigenvalues, _eigenvectors = eigenvalues_and_eigenvectors(self.app.ODEs, new_init_state, parameter_values)
        self.near_SoE_eigenvalues[n] = [eigenvalue for eigenvalue in _eigenvalues]
        self.near_SoE_eigenvectors[n] = [eigenvector for eigenvector in _eigenvectors.T]

        # Change text in "eig. N" popup
        eigenvalues_texts = [f"{i} : {self.near_SoE_eigenvalues[n][i]}" for i in range(len(self.app.variable_names))]
        eigenvalues_text = "\n".join(eigenvalues_texts)
        dpg.set_value(f"near_SoE_eigenvalue_popup_text_{n}", eigenvalues_text)
        eigenvectors_texts = [f"{i} : {self.near_SoE_eigenvectors[n][i].tolist()}" for i in range(len(self.app.variable_names))]
        eigenvectors_text = "\n".join(eigenvectors_texts)
        dpg.set_value(f"near_SoE_eigenvector_popup_text_{n}", eigenvectors_text)

        if len(self.near_SoE_eigenvalues[n]) != len(self.app.variable_names):
            self.delete_near_SoE_plot(n)
            return
        if np.iscomplexobj(self.near_SoE_eigenvectors[n]):
            self.delete_near_SoE_plot(n)
            return
        
        # Change integration direction
        if np.real(self.near_SoE_eigenvalues[n][current_eig_N]) < 0.0:
            dpg.set_value(f"near_SoE_table_dt_{n}", "-")
        else:
            dpg.set_value(f"near_SoE_table_dt_{n}", "+")
        
        # Reintegrate and redraw
        self.update_from_near_SoE_table_to_trajectory(n)
        self.update_from_near_SoE_trajectory_to_plot(n)
        return
    
    def callbcak_near_SoE_correct_all(self, sender, app_data, user_data):
        for (n, trajectory) in self.near_SoE_trajectories.items():
            self.callback_near_SoE_table_correct(None, None, {"n":n})
        return
    
    def callback_near_SoE_table_change_option(self, sender, app_data, user_data):
        n = user_data["n"]

        if not self.near_SoE_autocorrect[n]:
            return

        current_eig_N = dpg.get_value(f"near_SoE_table_eig_N_{n}")
        if np.real(self.near_SoE_eigenvalues[n][current_eig_N]) < 0.0:
            dpg.set_value(f"near_SoE_table_dt_{n}", "-")
        else:
            dpg.set_value(f"near_SoE_table_dt_{n}", "+")

        self.update_from_near_SoE_table_to_trajectory(n)
        self.update_from_near_SoE_trajectory_to_plot(n)
        return
    
    def callback_near_SoE_table_copy_variable(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]
        variable_name = user_data["variable"]
        include_name = user_data["name"]
        tag = f"near_SoE_table_{variable_name}_{n}"
        
        if include_name:
            clip.copy(f"{variable_name}={dpg.get_value(tag)}")
        else:
            clip.copy(f"{dpg.get_value(tag)}")
        return
    
    def callback_near_SoE_table_copy_init_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]

        # Create strings of "var_n=val_n"
        init_state = self.get_near_SoE_table_init_state(n)
        result = [f"{variable_name}={init_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = self.separator_default
        if self.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_near_SoE_table_copy_last_state(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]

        # Create strings of "var_n=val_n"
        last_state = self.get_near_SoE_last_state(n)
        result = [f"{variable_name}={last_state[i]}" for (i,variable_name) in enumerate(self.app.variable_names)]
        sep = self.separator_default
        if self.separator_add_whitespace:
            sep = sep + " "
        clip.copy(sep.join(result))
        return
    
    def callback_near_SoE_table_paste_init_state(self, sender, app_data, user_data):
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
                dpg.set_value(f"near_SoE_table_{variable_name}_{n}", float(variable_value))

        if not self.near_SoE_autocorrect[n]:
            return
        
        self.callback_near_SoE_table_correct(None, None, {"n":n})
        return
    
    def callback_near_SoE_table_copy_trajectory(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        # Which n trajectory has been clicked
        n = user_data["n"]
        trajectory = self.near_SoE_trajectories[n]

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
    
    def callback_near_SoE_table_copy_eigenvalues(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]
        copy_type = user_data["type"]

        if copy_type == "python":
            eigenvalues_texts = [f"eigenvalue_{i} = {self.near_SoE_eigenvalues[n][i]}" for i in range(len(self.app.variable_names))]
            eigenvalues_text = "\n".join(eigenvalues_texts)
        else:
            return
        clip.copy(eigenvalues_text)
        return
    
    def callback_near_SoE_table_copy_eigenvectors(self, sender, app_data, user_data):
        # Hide context menu
        dpg.hide_item(dpg.get_item_parent(sender))

        n = user_data["n"]
        copy_type = user_data["type"]

        if copy_type == "python":
            eigenvectors_texts = [f"eigenvector_{i} = {self.near_SoE_eigenvectors[n][i].tolist()}" for i in range(len(self.app.variable_names))]
            eigenvectors_text = "\n".join(eigenvectors_texts)
        else:
            return
        clip.copy(eigenvectors_text)
        return