"""Event management system"""
from typing import Callable, Dict, List
import logging

class EventManager:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)

    def register_handler(self, event: str, handler: Callable) -> None:
        """Register an event handler.
        
        Args:
            event: Event name to handle
            handler: Callback function for the event
        """
        if event not in self.handlers:
            self.handlers[event] = []
        self.handlers[event].append(handler)
        self.logger.debug(f"Registered handler for event: {event}")

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Name of event to emit
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        if event in self.handlers:
            for handler in self.handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event}: {e}")
