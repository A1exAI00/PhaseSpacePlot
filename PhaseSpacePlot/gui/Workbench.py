from App import App
from utils.EventManager import EventManager

#########################################################################################

class Workbench():
    def __init__(self, app:App):
        self._app:App = app
        self._event_manager:EventManager = EventManager()

        self._separators_supported = [",", ";", ":"]
        self._separator_default = self._separators_supported[0]
        self._separator_add_whitespace = True

        self._integrate_directions = ["+", "-"]
        self._integrate_direction_default = self._integrate_directions[0]