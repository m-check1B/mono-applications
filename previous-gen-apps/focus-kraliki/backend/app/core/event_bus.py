"""
Event Bus for Backend Services
Part of Gap #7: Event bus notifications from agent-tools to frontend
Enables decoupled event publishing/subscription pattern
"""

from typing import Dict, List, Callable, Any
from datetime import datetime
import asyncio

class EventBus:
    """Simple in-memory event bus for backend services"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)
    
    async def publish(self, event_type: str, data: Any, user_id: str = None):
        """Publish an event to all subscribers"""
        if event_type not in self._subscribers:
            return
        
        event = {
            "type": event_type,
            "data": data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Call all subscribers
        tasks = []
        for handler in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # Sync handler - run in executor
                tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

import threading

# Global event bus instance with thread-safe singleton pattern
_event_bus = None
_instance_lock = threading.Lock()

def get_event_bus() -> EventBus:
    """Get the global event bus instance with thread-safe initialization"""
    global _event_bus
    if _event_bus is None:
        with _instance_lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus
