import asyncio
import logging
from typing import Callable, Dict, List, Awaitable, Type, Any
from app.events.events import BaseEvent, DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[BaseEvent, Any], Awaitable[None]]

class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type[BaseEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed to {event_type.__name__}")

    async def publish(self, event: BaseEvent, **kwargs):
        event_type = type(event)
        handlers = list(self._subscribers.get(event_type, []))
        # Also trigger handlers subscribed to base classes
        for base in event_type.__bases__:
            if issubclass(base, BaseEvent) and base in self._subscribers:
                handlers.extend(self._subscribers[base])
        
        if not handlers:
            return
            
        tasks = [handler(event, **kwargs) for handler in set(handlers)]
        
        # Execute tasks sequentially to ensure DB session is valid in synchronous context
        for task in tasks:
            await self._safe_execute(task)
                
    async def _safe_execute(self, awaitable: Awaitable):
        try:
            await awaitable
        except Exception as e:
            logger.error(f"Error executing event handler: {e}", exc_info=True)

# Global event bus instance
event_bus = EventBus()
