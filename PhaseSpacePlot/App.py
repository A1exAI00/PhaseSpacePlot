class App:
    def __init__(self):
        self.DS_file_name = "dynamical_system.txt"
        self.DS_folder_path = None
        self.DS_file_path = None
        self.variable_names = None
        self.parameter_names = None
        self.ODEs = None
        self.trajectories = None
        self.axis_posible_labels = None
        self.x_axis_label_default = None
        self.y_axis_label_default = None
        self.parameter_defaults = None 
        self.parameter_step_defaults = None
        self.integration_parameter_names = ["integration_t_start", "integration_t_end", "integration_t_steps"]
        self.integration_parameter_types = ["float", "float", "int"]
        self.integration_parameter_defaults = [0.0, 10.0, 1000] 
        return
    
    def init_other_variables(self):
        self.axis_posible_labels = self.variable_names + ["t",]
        self.x_axis_label_default = self.axis_posible_labels[0]
        self.y_axis_label_default = self.axis_posible_labels[1]
        self.parameter_defaults = [1e0 for _ in range(len(self.parameter_names))]
        self.parameter_step_defaults = [1e-1 for _ in range(len(self.parameter_names))]
        return

    def print_interesting(self):
        print("Path to DS folder:", self.DS_folder_path)
        print("Variable names:", self.variable_names)
        print("Parameter names:", self.parameter_names)
        print("ODEs:", self.ODEs)
        return