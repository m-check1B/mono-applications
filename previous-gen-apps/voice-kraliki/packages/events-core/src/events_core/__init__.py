"""Events Core - Event bus abstraction for Platform 2026.

Provides unified publish/subscribe patterns with multiple backends:

- InMemoryEventBus: For testing and single-process applications
- RabbitMQEventBus: For distributed systems with RabbitMQ

Basic usage:
    from events_core import create_event_bus, Event

    # Create bus (auto-selects based on URL)
    bus = create_event_bus(amqp_url="amqp://localhost")  # or None for in-memory
    await bus.connect()

    # Subscribe to events
    async def handler(event: Event):
        print(f"Received: {event.type}")

    await bus.subscribe_typed("user.*", handler)

    # Publish events
    await bus.publish_event(Event(type="user.created", data={"id": "123"}))

    # Cleanup
    await bus.close()
"""

from events_core.types import (
    Event,
    EventHandler,
    EventPriority,
    EventResult,
    RawEventHandler,
)
from events_core.event_bus import (
    BaseEventBus,
    InMemoryEventBus,
    RabbitMQEventBus,
    create_event_bus,
    is_rabbitmq_available,
)

__version__ = "0.1.0"

__all__ = [
    # Types
    "Event",
    "EventHandler",
    "EventPriority",
    "EventResult",
    "RawEventHandler",
    # Event Bus
    "BaseEventBus",
    "InMemoryEventBus",
    "RabbitMQEventBus",
    # Factory
    "create_event_bus",
    "is_rabbitmq_available",
]
