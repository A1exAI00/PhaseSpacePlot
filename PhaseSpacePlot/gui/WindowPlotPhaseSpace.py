import dearpygui.dearpygui as dpg

from utils.Trajectory import Trajectory

from App import App
from utils.EventManager import EventManager

from .WindowPlot import WindowPlot

# For VSCode autocomplete, to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gui.WorkbenchPhaseSpace import WorkbenchPhaseSpace

#########################################################################################

class WindowPlotPhaseSpace(WindowPlot):
    def __init__(self, m:int, app:App, parent:"WorkbenchPhaseSpace", event_manager:EventManager) -> None:
        super().__init__(m, app, parent, event_manager)

        # GUI
        self._window_title:str = "Phase Space Plot"

        # Event Manager
        self._event_manager.subscribe("added_init_state", self.handler_added_init_state)
        self._event_manager.subscribe("integrated_trajectory", self.handler_integrated_trajectory)
        self._event_manager.subscribe("changed_toggled_show", self.handle_toggled_show)

        return None
    
    def handler_added_init_state(self, data:dict):
        n = data["n"]
        draginit = data["draginit"]

        if draginit: self.add_dragpoint(n)
        self.add_lineseries(n)
        return
    
    def handler_integrated_trajectory(self, data:dict):
        n = data["n"]
        trajectory:Trajectory = data["trajectory"]
        draginit = data["draginit"]

        x_axis_label, y_axis_label, x_axis_i, y_axis_i = self.get_axis_labels()
        x_data = trajectory.t_sol if x_axis_i == len(self._app.variable_names) else trajectory.sol[x_axis_i]
        y_data = trajectory.t_sol if y_axis_i == len(self._app.variable_names) else trajectory.sol[y_axis_i]

        if draginit: self.update_dragpoint(n, x_data[0], y_data[0])
        self.update_lineseries(n, x_data, y_data)
        return

    def handle_toggled_show(self, data:dict):
        n = data["n"]
        show = data["show"]
        draginit = data["draginit"]

        toggle_show = dpg.show_item if show else dpg.hide_item

        if draginit: toggle_show(self.get_dragpoint_tag(n))
        toggle_show(self.get_lineseries_tag(n))
        return