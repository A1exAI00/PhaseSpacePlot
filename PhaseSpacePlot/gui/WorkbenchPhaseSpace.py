import numpy as np
import dearpygui.dearpygui as dpg

from utils.Trajectory import Trajectory
from utils.nonlinear_solve import solve, eigenvalues_and_eigenvectors

from App import App
from gui.Workbench import Workbench

from .WindowParameters import WindowParameters
from .WindowDragpoint import WindowDragpoint
from .WindowNearSoE import WindowNearSoE
from .WindowPlotPhaseSpace import WindowPlotPhaseSpace

#########################################################################################

class WorkbenchPhaseSpace(Workbench):
    def __init__(self, app:App):
        super().__init__(app)

        # Necessery for Phase Space Workbench
        self._window_parameters:WindowParameters = WindowParameters(self._app, self, self._event_manager)
        self._window_dragpoint:WindowDragpoint = WindowDragpoint(self._app, self, self._event_manager)
        self._window_near_SoE:WindowNearSoE = WindowNearSoE(self._app, self, self._event_manager)

        # One plot window is necessery, others are optional
        self._windows_plot:dict[int, WindowPlotPhaseSpace] = {}
        self._windows_plot[0] = WindowPlotPhaseSpace(0, self._app, self, self._event_manager)

        # Mixed bag of dragpoint and near SoE trajectories
        self._trajectories:dict[int,Trajectory] = {}
        self._trajectory_types:dict[int, int] = {}
        self._trajectory_show:dict[int, bool] = {}
        self._trajectory_autocorrect:dict[int, bool] = {}
        self._SoE_eigenvalues:dict = {}
        self._SoE_eigenvectors:dict = {}

        # Events published by this class
        self._event_integrated_trajectory = "integrated_trajectory"

        # Events this class is subscribed to
        self._event_manager.subscribe("changed_init_state_table_option", self.handler_changed_init_state_table_option)
        self._event_manager.subscribe("changed_dynamical_system_parameter", self.handler_changed_dynamical_system_parameter)
        self._event_manager.subscribe("changed_plot_axis_label", self.handler_changed_plot_axis_label)
        self._event_manager.subscribe("changed_dragpoint_position", self.handler_changed_dragpoint_position)
        self._event_manager.subscribe("changed_toggled_show", self.handler_toggled_show)
        self._event_manager.subscribe("added_init_state", self.handler_added_init_state)
        self._event_manager.subscribe("corrected_SoE", self.handler_corrected_SoE)
        self._event_manager.subscribe("changed_toggled_autocorrect", self.handler_changed_toggled_autocorrect)
        return
    
    def get_last_state(self, n:int):
        trajectory:Trajectory = self._trajectories[n]
        return np.array([trajectory.sol[i][-1] for (i, variable_name) in enumerate(self._app.variable_names)])
    
    def get_trajectory(self, n:int):
        return self._trajectories[n]

    def setup_all(self):
        self._window_parameters.setup_window()
        self._window_dragpoint.setup_window()
        self._window_near_SoE.setup_window()
        for (m, window) in self._windows_plot.items():
            window.setup_window()
        return
    
    def integrate_trajectory(self, n:int):
        trajectory = self._trajectories[n]
        trajectory_type = self._trajectory_types[n]

        parameter_values:list[float] = self._window_parameters.get_parameters()

        if trajectory_type == 0: # Dragpoint init state
            # Get options from dragpoint table
            init_state:np.ndarray = self._window_dragpoint.get_init_state(n)
            t_start:float = dpg.get_value(f"dragpoint_table_t_start_{n}")
            t_end:float = dpg.get_value(f"dragpoint_table_t_end_{n}")
            t_steps:int = dpg.get_value(f"dragpoint_table_t_steps_{n}")
            dt:str = dpg.get_value(f"dragpoint_table_dt_{n}")

            if dt == "-": t_start, t_end = t_end, t_start

            trajectory.integrate_scipy(self._app.ODEs, init_state, parameter_values, t_start, t_end, t_steps)

        elif trajectory_type == 1: # Near SoE init state

            # If eigenvalues are empty
            # This can accure if there was an error when calculating eigenvalues
            # or eigenvalues hav not been calculated yet
            if len(self._SoE_eigenvalues[n]) != len(self._app.variable_names):
                return False
            
            # Get SoE current SoE coordinates from GUI
            SoE_coordinates = self._window_near_SoE.get_SoE_coordinates(n)

            # Get ordinary number of eigenvalue from GUI
            eigenvalue_N:int = dpg.get_value(f"near_SoE_table_eig_N_{n}")

            # If incorrect eigenvalue_N input
            if (eigenvalue_N < 0) or (eigenvalue_N > len(self._app.variable_names)):
                return False
            
            # Get eigenvalue and eigenvector that correspond to eigenvalue_N
            eigenvalue = self._SoE_eigenvalues[n][eigenvalue_N]
            eigenvector = self._SoE_eigenvectors[n][eigenvalue_N]

            # Get the sign corresponding to the direction along the eigenvector
            eigenvector_dir_sign = dpg.get_value(f"near_SoE_table_eig_dir_{n}")
            eigenvector_dir_numerical = 1 if (eigenvector_dir_sign=="+") else -1

            # DO NOT INTEGRATE IF EIGENVECTOR IS COMPLEX
            # This will result in segmentation fault            
            if np.iscomplexobj(eigenvector):
                return False
            
            # If the separatrix or direction is not stable, reverse the direction of integration 
            dpg.set_value(f"near_SoE_table_dt_{n}", "-" if (np.real(eigenvalue) < 0.0) else "+")

            # Get other options from GUI
            t_start:float = dpg.get_value(f"near_SoE_table_t_start_{n}")
            t_end:float = dpg.get_value(f"near_SoE_table_t_end_{n}")
            t_steps:int = dpg.get_value(f"near_SoE_table_t_steps_{n}")
            dt:str = dpg.get_value(f"near_SoE_table_dt_{n}")
            eps:float = dpg.get_value(f"near_SoE_table_eps_{n}")

            if dt == "-": t_start, t_end = t_end, t_start

            # Step of length eps from SoE in the direction of eigenvector 
            init_state = SoE_coordinates  + eps * eigenvector_dir_numerical * eigenvector

            trajectory.integrate_scipy(self._app.ODEs, init_state, parameter_values, t_start, t_end, t_steps)

        return True
    
    def correct_SoE(self, n:int):
        parameter_values:list[float] = self._window_parameters.get_parameters()

        SoE_coordinates = self._window_near_SoE.get_SoE_coordinates(n)
        new_SoE_coordinates, success = solve(self._app.ODEs, SoE_coordinates, parameter_values)

        # If new SoE is not found, return unsuccessful status
        if not success: 
            # Change text in "eig. N" popup to blank
            eigenvalues_texts = ["" for _ in range(len(self._app.variable_names))]
            eigenvalues_text = "\n".join(eigenvalues_texts)
            dpg.set_value(f"near_SoE_eigenvalue_popup_text_{n}", eigenvalues_text)
            eigenvectors_texts = ["" for _ in range(len(self._app.variable_names))]
            eigenvectors_text = "\n".join(eigenvectors_texts)
            dpg.set_value(f"near_SoE_eigenvector_popup_text_{n}", eigenvectors_text)
            return False

        # Update variables of SoE coordinates in GUI
        for (i, variable_name) in enumerate(self._app.variable_names): 
            self._window_near_SoE.update_variable(variable_name, n, new_SoE_coordinates[i])

        _eigenvalues, _eigenvectors = eigenvalues_and_eigenvectors(self._app.ODEs, SoE_coordinates, parameter_values)
        self._SoE_eigenvalues[n] = [eigenvalue for eigenvalue in _eigenvalues]
        self._SoE_eigenvectors[n] = [eigenvector for eigenvector in _eigenvectors.T]

        # Change text in "eig. N" popup
        eigenvalues_texts = [f"{i} : {self._SoE_eigenvalues[n][i]}" for i in range(len(self._app.variable_names))]
        eigenvalues_text = "\n".join(eigenvalues_texts)
        dpg.set_value(f"near_SoE_eigenvalue_popup_text_{n}", eigenvalues_text)
        eigenvectors_texts = [f"{i} : {self._SoE_eigenvectors[n][i].tolist()}" for i in range(len(self._app.variable_names))]
        eigenvectors_text = "\n".join(eigenvectors_texts)
        dpg.set_value(f"near_SoE_eigenvector_popup_text_{n}", eigenvectors_text)
        return True
    
    def handler_changed_init_state_table_option(self, data:dict):
        n:int = data["n"]

        # Do not integrate and do not publish any other events if "show" is False 
        if not self._trajectory_show[n]: return
        if not self._trajectory_autocorrect[n]: return

        # Try to correct SoE coordinates, return if unsuccessful
        if self._trajectory_types[n] == 1:
            success_correct = self.correct_SoE(n)
            if not success_correct: return

        success_integrate = self.integrate_trajectory(n)
        if not success_integrate: return

        _data = {"n":n, 
                "draginit":(self._trajectory_types[n]==0),
                "trajectory":self._trajectories[n]}
        self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return
    
    def handler_changed_dynamical_system_parameter(self, data:dict):
        for (n, trajectory) in self._trajectories.items():
            if not self._trajectory_show[n]: continue
            if not self._trajectory_autocorrect[n]: continue

            # Try to correct SoE coordinates, return if unsuccessful
            if self._trajectory_types[n] == 1:
                success_correct = self.correct_SoE(n)
                if not success_correct: continue

            success_integrate = self.integrate_trajectory(n)
            if not success_integrate: continue

            _data = {"n":n, 
                "draginit":(self._trajectory_types[n]==0),
                "trajectory":self._trajectories[n]}    
            self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return
    
    def handler_changed_plot_axis_label(self, data:dict):
        m:int = data["m"]
        window = self._windows_plot[m]
        # x_axis_label = data["x_axis_label"] 
        # y_axis_label = data["y_axis_label"] 
        x_axis_i:int = data["x_axis_i"] 
        y_axis_i:int = data["y_axis_i"]

        for (m, window) in self._windows_plot.items():
            for (n, trajectory) in self._trajectories.items():

                if not self._trajectory_show[n]: return

                # If X index corresponts to lamel of time "t"
                if x_axis_i == len(self._app.variable_names):
                    x_data = trajectory.t_sol
                else:
                    x_data = trajectory.sol[x_axis_i]
                
                # If Y index corresponts to lamel of time "t"
                if y_axis_i == len(self._app.variable_names):
                    y_data = trajectory.t_sol
                else:
                    y_data = trajectory.sol[y_axis_i]

                # Update projection in the plot
                if self._trajectory_types[n] == 0: 
                    window.update_dragpoint(n, x_data[0], y_data[0])
                window.update_lineseries(n, x_data, y_data)
        return
    
    def handler_changed_dragpoint_position(self, data:dict):
        m:int = data["m"] 
        n:int = data["n"] 
        # x_axis_label:str = data["x_axis_label"]
        # y_axis_label:str = data["y_axis_label"]
        x_axis_i:int = data["x_axis_i"]
        y_axis_i:int = data["y_axis_i"]
        x_dragpoint:float = data["x_dragpoint"]
        y_dragpoint:float = data["y_dragpoint"]

        if (x_axis_i == len(self._app.variable_names)) and (y_axis_i == len(self._app.variable_names)):
            self._windows_plot[m].update_dragpoint(n, 0.0, 0.0)
            return
        if x_axis_i == len(self._app.variable_names):
            self._windows_plot[m].update_dragpoint(n, 0.0, y_dragpoint)
        if y_axis_i == len(self._app.variable_names):
            self._windows_plot[m].update_dragpoint(n, x_dragpoint, 0.0)

        self.integrate_trajectory(n)

        _data = {"n":n, 
                "draginit":(self._trajectory_types[n]==0),
                "trajectory":self._trajectories[n]}
        self._event_manager.publish(self._event_integrated_trajectory, data=_data)

        return
    
    def handler_toggled_show(self, data:dict):
        n:int = data["n"]
        show:bool = data["show"]
        self._trajectory_show[n] = show

        if not self._trajectory_show[n]: return
        if not self._trajectory_autocorrect[n]: return

        # Try to correct SoE coordinates, return if unsuccessful
        if self._trajectory_types[n] == 1:
            success_correct = self.correct_SoE(n)
            if not success_correct: return

        success_integrate = self.integrate_trajectory(n)
        if not success_integrate: return

        _data = {"n":n, 
                "draginit":(self._trajectory_types[n]==0),
                "trajectory":self._trajectories[n]}
        self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return
    
    def handler_added_init_state(self, data:dict):
        n_new:int = data["n"]
        draginit:bool = data["draginit"]

        trajectory_new = Trajectory()
        self._trajectories[n_new] = trajectory_new
        self._trajectory_types[n_new] = 0 if draginit else 1
        self._trajectory_show[n_new] = True
        self._trajectory_autocorrect[n_new] = draginit
        if not draginit:
            self._SoE_eigenvalues[n_new] = []
            self._SoE_eigenvectors[n_new] = []

        if not self._trajectory_show[n_new]: return
        if not self._trajectory_autocorrect[n_new]: return

        # Try to correct SoE coordinates, return if unsuccessful
        if self._trajectory_types[n_new] == 1:
            success_correct = self.correct_SoE(n_new)
            if not success_correct: return

        success_integrate = self.integrate_trajectory(n_new)
        if not success_integrate: return

        _data = {"n":n_new, 
                "draginit":(self._trajectory_types[n_new]==0),
                "trajectory":self._trajectories[n_new]}
        self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return
    
    def handler_corrected_SoE(self, data:dict):
        n:int = data["n"]

        ns = [_n for (_n, trajectory) in self._trajectories.items()] if (n == -1) else [n,]

        for n in ns:
            if (self._trajectory_types[n] == 0): continue

            success_correct = self.correct_SoE(n)
            if not success_correct: continue

            success_integrate = self.integrate_trajectory(n)
            if not success_integrate: continue

            _data = {"n":n, 
                    "draginit":(self._trajectory_types[n]==0),
                    "trajectory":self._trajectories[n]}
            self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return
    
    def handler_changed_toggled_autocorrect(self, data:dict):
        n:int = data["n"]
        self._trajectory_autocorrect[n] = data["autocorrect"]

        if self._trajectory_autocorrect[n]:
            success_correct = self.correct_SoE(n)
            if not success_correct: return

            success_integrate = self.integrate_trajectory(n)
            if not success_integrate: return

            _data = {"n":n, 
                    "draginit":(self._trajectory_types[n]==0),
                    "trajectory":self._trajectories[n]}
            self._event_manager.publish(self._event_integrated_trajectory, data=_data)
        return