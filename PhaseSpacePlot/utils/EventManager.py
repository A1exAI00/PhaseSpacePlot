class EventManager:
    def __init__(self) -> None:
        self._subscribers:dict = {}
        return None
    
    def subscribe(self, event_type:str, handler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        return None
    
    def publish(self, event_type:str, data:dict={}) -> None:
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                handler(data)
        return None