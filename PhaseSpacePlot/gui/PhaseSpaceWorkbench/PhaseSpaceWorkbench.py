import numpy as np
import dearpygui.dearpygui as dpg
import clipboard as clip

from utils.integration import Trajectory

from .PhaseSpaceWorkbenchParameters import PhaseSpaceWorkbenchParameters as pswp
from .PhaseSpaceWorkbenchPlotOptions import PhaseSpaceWorkbenchPlotOptions as pswpo
from .PhaseSpaceWorkbenchPlot import PhaseSpaceWorkbenchPlot as pswpl
from .PhaseSpaceWorkbenchDragpoint import PhaseSpaceWorkbenchDragpoint as pswd

#########################################################################################

class PhaseSpaceWorkbench(pswp, pswpo, pswpl, pswd):
    def __init__(self, app):
        self.app = app

        ######################
        ##### PARAMETERS #####
        ######################

        # Defaults
        self.parameter_default = 0.1
        self.parameter_step_default = 1e-2

        # GUI
        self.parameter_format = "%f"
        self.parameter_step_format = "%.2E"
        self.parameter_input_width = 130
        self.parameter_step_input_window = 65
        

        ########################
        ##### PLOT OPTIONS #####
        ########################

        # Defaults
        self.axis_posible_labels = self.app.variable_names + ["t",]
        self.x_axis_label_default = self.axis_posible_labels[0]
        self.y_axis_label_default = self.axis_posible_labels[1]

        # GUI
        self.plot_options_option_width = 140


        #############################
        ##### DRAGPOINT OPTIONS #####
        #############################

        # Defaults
        self.dragpoint_table_default_t_start = 0.0
        self.dragpoint_table_default_t_end = 10.0
        self.dragpoint_table_default_t_steps = 1000
        self.integrate_directions = ["+", "-"]
        self.integrate_direction_default = self.integrate_directions[0]

        # GUI
        self.dragpoint_table_variable_format = "%f"
        self.dragpoint_table_variable_step_format = "%.2E"
        self.dragpoint_table_variable_input_width = 110
        self.dragpoint_table_variable_step_input_width = 65
        self.dragpoint_table_option_input_width = 55
        self.dragpoint_table_default_variable_value = 0.0
        self.dragpoint_table_default_variable_step_value = 1e-2

        # Objects
        self.dragpoint_trajectories = {0:Trajectory()}


        ################
        ##### MISC #####
        ################

        self.separators_supported = [",", ";", ":"]
        self.separator_default = self.separators_supported[0]
        self.separator_add_whitespace = True

        return
    
    def setup_all(self):
        self.setup_dynamical_system_parameters_window()
        self.setup_plot_options_window()
        self.setup_dragpoint_init_state_window()
        self.setup_phase_space_plot_window()
    
    def delete_all(self):
        self.delete_dynamical_system_parameters_window()
        self.delete_plot_options_window()
        self.delete_dragpoint_init_state_window()
        self.delete_phase_space_plot_window()
