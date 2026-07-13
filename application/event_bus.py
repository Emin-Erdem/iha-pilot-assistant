from collections import defaultdict
from typing import Callable, Any


class EventBus:
    """
    A simple event bus that allows components to communicate
    without directly depending on each other.
    """

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        """
        Registers a callback for an event.
        """
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, data: Any = None) -> None:
        """
        Publishes an event to all subscribers.
        """
        for callback in self._subscribers[event_name]:
            callback(data)