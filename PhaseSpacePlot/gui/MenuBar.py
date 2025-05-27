import os
import numpy as np
import dearpygui.dearpygui as dpg
from Equation import Expression

from utils.DS_from_file import load_DS_from_file
from gui.PhaseSpaceWorkbench.PhaseSpaceWorkbench import PhaseSpaceWorkbench as psw

#########################################################################################

class MenuBar:
    def __init__(self, app):
        self.app = app
        return

    def setup(self):
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Create Dynamical System", callback=self.callback_create_DS)
                dpg.add_menu_item(label="Open Dynamical System", callback=self.callback_open_DS)

            with dpg.menu(label="Workbench"):
                dpg.add_menu_item(label="Phase Space Workbench", callback=self.callback_open_phasespace_workbench)

            with dpg.menu(label="Help"):
                dpg.add_menu_item(label="Manual", callback=self.callback_open_manual)
        return
    
    def callback_create_DS(self, sender, app_data):
        return
    
    def callback_open_DS(self, sender, app_data):
        if self.app.active_workbench is not None:
            self.app.active_workbench.delete_all()
            self.app.active_workbench = None
        
        with dpg.file_dialog(label="Choose folder with Dynamical System",
                            tag="DS_folder_dialog",
                            directory_selector=True, 
                            show=True, 
                            callback=self.callback_process_DS_folder, 
                            width=500, height=400):
            pass
        return
    
    def callback_process_DS_folder(self, sender, app_data):
        # Get dynamical system folder
        self.app.DS_folder_path = app_data["file_path_name"]
        self.app.DS_file_path = os.path.join(self.app.DS_folder_path, self.app.DS_file_name)

        # Dynamical System setup
        variable_names, parameter_names, equations = load_DS_from_file(self.app.DS_file_path)
        self.app.variable_names = variable_names
        self.app.parameter_names = parameter_names
        equations_objs = [Expression(eq, self.app.variable_names+self.app.parameter_names) for (i,eq) in enumerate(equations)]
        self.app.ODEs = lambda U, p, t: [eq_obj(*np.concat((U,p))) for eq_obj in equations_objs]

        self.app.print_interesting()
        return
    
    def callback_open_phasespace_workbench(self, sender, app_data):
        if self.app.active_workbench is not None:
            self.app.active_workbench.delete_all()
            self.app.active_workbench = None
            
        self.app.active_workbench = psw(self.app)
        self.app.active_workbench.setup_all()
        return
    
    def callback_open_manual(self, sender, app_data):
        return
