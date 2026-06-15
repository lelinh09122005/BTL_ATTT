from collections import defaultdict
from typing import Callable, Any, Dict, List
from loguru import logger

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: str, listener: Callable[[Any], None]):
        """Registers a listener function for a specific event type."""
        self._listeners[event_type].append(listener)
        logger.debug(f"Subscribed listener to event: {event_type}")

    def publish(self, event_type: str, data: Any = None):
        """Publishes an event to all registered listeners."""
        logger.debug(f"Publishing event: {event_type} with data: {data}")
        listeners = self._listeners.get(event_type, [])
        for listener in listeners:
            try:
                listener(data)
            except Exception as e:
                logger.error(f"Error executing listener for event {event_type}: {e}")
                
# Global event bus instance
event_bus = EventBus()
