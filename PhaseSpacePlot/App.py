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

    def print_interesting(self):
        print("Path to DS folder:", self.DS_folder_path)
        print("Variable names:", self.variable_names)
        print("Parameter names:", self.parameter_names)
        print("ODEs:", self.ODEs)
        return