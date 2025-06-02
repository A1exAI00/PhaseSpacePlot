import os

from utils.DS_from_file import import_module_with_exec

class App:
    def __init__(self):
        self.DS_file_name = "dynamical_system.txt"
        self.DS_folder_path = None
        self.DS_file_path = None
        self.variable_names = None
        self.parameter_names = None
        self.ODEs = None

        self.active_workbench = None
        return
    
    def load_DS_info_exec(self, folder_path):
        self.DS_folder_path = folder_path
        self.DS_file_path = os.path.join(self.DS_folder_path, "dynamical_system.py")

        DS_module = import_module_with_exec(self.DS_file_path)
        self.variable_names = DS_module["variable_names"]
        self.parameter_names = DS_module["parameter_names"]
        self.ODEs = DS_module["ODEs"]
        return

    def print_interesting(self):
        print("Path to DS folder:", self.DS_folder_path)
        print("Variable names:", self.variable_names)
        print("Parameter names:", self.parameter_names)
        print("ODEs:", self.ODEs)
        return