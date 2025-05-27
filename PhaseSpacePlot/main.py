import os
import dearpygui.dearpygui as dpg
import numpy as np

from App import App
from utils.DS_from_file import load_DS_from_file
from Equation import Expression
from gui.PhaseSpaceWorkbench.PhaseSpaceWorkbench import PhaseSpaceWorkbench as psw


#########################################################################################
#########################################################################################


def create_DS_folder_chooser(app):
    with dpg.file_dialog(label="Choose folder with Dynamical System",
                     tag="DS_folder_dialog",
                     directory_selector=True, 
                     show=True, 
                     callback=lambda sender, app_data: callback_DS_folder_chooser(app, sender, app_data), 
                     width=500, height=400):
        pass
    return

def callback_DS_folder_chooser(app, sender, app_data):
    # Get dynamical system folder
    app.DS_folder_path = app_data["file_path_name"]
    app.DS_file_path = os.path.join(app.DS_folder_path, app.DS_file_name)

    # Dynamical System setup
    variable_names, parameter_names, equations = load_DS_from_file(app.DS_file_path)
    app.variable_names = variable_names
    app.parameter_names = parameter_names
    equations_objs = [Expression(eq, app.variable_names+app.parameter_names) for (i,eq) in enumerate(equations)]
    app.ODEs = lambda U, p, t: [eq_obj(*np.concat((U,p))) for eq_obj in equations_objs]

    app.print_interesting()
    the_psw = psw(app)
    the_psw.setup_all()
    return


#########################################################################################
#########################################################################################


dpg.create_context()

app = App()

create_DS_folder_chooser(app)

dpg.create_viewport(title='PhaseSpacePlot', width=1500, height=750)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
