import dearpygui.dearpygui as dpg

from App import App
from utils.EventManager import EventManager

# For VSCode autocomplete, to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.WorkbenchPhaseSpace import WorkbenchPhaseSpace

#########################################################################################

class WindowPlot:
    def __init__(self, m:int, app:App, parent:"WorkbenchPhaseSpace", event_manager:EventManager) -> None:
        self._m:int = m
        self._app:App = app
        self._parent:"WorkbenchPhaseSpace" = parent
        self._event_manager:EventManager = event_manager

        # Defaults
        self._x_axis_label_combo_tag = f"x_axis_label_{self._m}"
        self._y_axis_label_combo_tag = f"y_axis_label_{self._m}"
        self._x_axis_tag = f"x_axis_{self._m}"
        self._y_axis_tag = f"y_axis_{self._m}"
        self._window_tag = f"plot_window_{self._m}"
        self._axis_posible_labels = self._app.variable_names + ["t",]
        self._x_axis_label_default = self._axis_posible_labels[0]
        self._y_axis_label_default = self._axis_posible_labels[1]

        # GUI
        self._window_title:str = "Plot"
        self._plot_options_option_width = 140

        # Event Manager
        self._event_changed_dragpoint_position = "changed_dragpoint_position"
        self._event_changed_axis_label = "changed_plot_axis_label"

        return None
    
    def get_axis_labels(self):
        x_axis_label, y_axis_label = dpg.get_value(self._x_axis_label_combo_tag), dpg.get_value(self._y_axis_label_combo_tag)
        x_axis_i, y_axis_i = self._axis_posible_labels.index(x_axis_label), self._axis_posible_labels.index(y_axis_label)
        return (x_axis_label, y_axis_label, x_axis_i, y_axis_i)
    
    def get_dragpoint_tag(self, n):
        return f"dragpoint_{self._m}_{n}"
    
    def get_lineseries_tag(self, n):
        return f"lineseries_{self._m}_{n}"
    
    def get_plot_tag(self):
        return f"phase_space_plot_{self._m}"
    
    def setup_window(self):
        with dpg.window(label=self._window_title, tag=self._window_tag, pos=(800, 0), width=720, height=800):

            # Create two combo boxes to choose axis labels
            dpg.add_combo(label="X Axis Label", tag=self._x_axis_label_combo_tag,
                        default_value=self._x_axis_label_default, 
                        items=self._axis_posible_labels, 
                        callback=self.callback_change_axis_label, 
                        width=self._plot_options_option_width)
            dpg.add_combo(label="Y Axis Label", tag=self._y_axis_label_combo_tag,
                        default_value=self._y_axis_label_default, 
                        items=self._axis_posible_labels, 
                        callback=self.callback_change_axis_label,
                        width=self._plot_options_option_width)
            
            # Add empty plot
            with dpg.plot(label='', tag=self.get_plot_tag(), width=700, height=700):
                dpg.add_plot_axis(dpg.mvXAxis, label=self._x_axis_label_default, tag=self._x_axis_tag)
                dpg.add_plot_axis(dpg.mvYAxis, label=self._y_axis_label_default, tag=self._y_axis_tag)
        return
    
    def delete_phase_space_plot_window(self):
        dpg.delete_item(self._window_tag)

    def add_lineseries(self, n):
        dpg.add_line_series([], [], label="", tag=self.get_lineseries_tag(n), parent=self._y_axis_tag)
        return
    
    def update_lineseries(self, n, x_data, y_data):
        dpg.set_value(self.get_lineseries_tag(n), [x_data, y_data])
        return
    
    def add_dragpoint(self, n):
        dpg.add_drag_point(label=f"Dragpoint No.{n}", tag=self.get_dragpoint_tag(n), 
                           parent=self.get_plot_tag(),
                           callback=self.callback_change_dragpoint_position,
                           user_data={"n":n},
                           color=[255, 0, 0, 150])
        return
    
    def update_dragpoint(self, n, x_data, y_data):
        dpg.set_value(self.get_dragpoint_tag(n), [x_data, y_data])

    def callback_change_dragpoint_position(self, sender, app_data, user_data):
        n = user_data["n"]
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()
        x_dragpoint, y_dragpoint = dpg.get_value(self.get_dragpoint_tag(n))
        _data = {"m":self._m, 
                 "n":n, 
                 "x_axis_label":x_axis_label, 
                 "y_axis_label":y_axis_label,
                 "x_axis_i":x_axis_i,
                 "y_axis_i":y_axis_i,
                 "x_dragpoint":x_dragpoint,
                 "y_dragpoint":y_dragpoint}
        self._event_manager.publish(self._event_changed_dragpoint_position, data=_data)
        return
    
    def callback_change_axis_label(self, sender, app_data, user_data):
        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()
        dpg.configure_item(self._x_axis_tag, label=x_axis_label)
        dpg.configure_item(self._y_axis_tag, label=y_axis_label)

        _data = {"m":self._m, 
                 "x_axis_label":x_axis_label, 
                 "y_axis_label":y_axis_label,
                 "x_axis_i":x_axis_i,
                 "y_axis_i":y_axis_i}
        self._event_manager.publish(self._event_changed_axis_label, data=_data)
        return 

