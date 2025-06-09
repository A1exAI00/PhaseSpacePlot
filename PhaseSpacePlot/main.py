import dearpygui.dearpygui as dpg

from App import App
from gui.MenuBar import MenuBar

#########################################################################################

VIEWPORT_WINDOW_TITLE = "PhaseSpacePlot by Alex Akinin"
VIEWPORT_WINDOW_WIDTH = 1700
VIEWPORT_WINDOW_HEIGHT = 850

app = App()
menubar = MenuBar(app)

#########################################################################################

dpg.create_context()

menubar.setup()

dpg.create_viewport(title=VIEWPORT_WINDOW_TITLE, 
                    width=VIEWPORT_WINDOW_WIDTH, 
                    height=VIEWPORT_WINDOW_HEIGHT)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
