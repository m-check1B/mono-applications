"""Event bus implementations for publish/subscribe patterns.

Provides two backends:
- InMemoryEventBus: For testing and single-process apps
- RabbitMQEventBus: For distributed systems with RabbitMQ

Usage:
    from events_core import create_event_bus, Event

    # Create bus (auto-selects RabbitMQ if URL provided, else in-memory)
    bus = create_event_bus(amqp_url="amqp://localhost")

    # Connect
    await bus.connect()

    # Subscribe to events
    async def handler(event: Event):
        print(f"Received: {event.type} - {event.data}")

    await bus.subscribe("user.*", handler)

    # Publish events
    await bus.publish_event(Event(type="user.created", data={"user_id": "123"}))

    # Cleanup
    await bus.close()
"""

import asyncio
import contextlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from events_core.types import Event, EventHandler, EventResult, RawEventHandler

logger = logging.getLogger(__name__)

# Try importing RabbitMQ library
_rabbitmq_available = False
try:
    import aio_pika
    _rabbitmq_available = True
except ImportError:
    aio_pika = None


class BaseEventBus(ABC):
    """Abstract base class for event bus implementations."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the event bus."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""
        ...

    @abstractmethod
    async def publish(self, event_type: str, data: Dict[str, Any]) -> EventResult:
        """Publish a raw event.

        Args:
            event_type: Event type string (e.g., "user.created")
            data: Event payload

        Returns:
            EventResult with publication status
        """
        ...

    @abstractmethod
    async def subscribe(
        self,
        event_pattern: str,
        handler: RawEventHandler,
    ) -> None:
        """Subscribe to events matching a pattern.

        Args:
            event_pattern: Pattern to match (e.g., "user.*", "order.#")
            handler: Async function to handle events
        """
        ...

    async def publish_event(self, event: Event) -> EventResult:
        """Publish a typed Event object.

        Args:
            event: Event instance to publish

        Returns:
            EventResult with publication status
        """
        return await self.publish(event.type, event.model_dump())

    async def subscribe_typed(
        self,
        event_pattern: str,
        handler: EventHandler,
    ) -> None:
        """Subscribe with typed Event handler.

        Args:
            event_pattern: Pattern to match
            handler: Async function receiving Event objects
        """
        async def wrapper(event_type: str, data: Dict[str, Any]) -> None:
            event = Event(**data) if "type" in data else Event(type=event_type, data=data)
            await handler(event)

        await self.subscribe(event_pattern, wrapper)


class InMemoryEventBus(BaseEventBus):
    """In-memory event bus for testing and single-process applications.

    Events are dispatched asynchronously via an asyncio queue.
    Pattern matching supports "*" (single word) and "#" (multiple words).

    Example:
        bus = InMemoryEventBus()
        await bus.connect()

        async def handler(event_type, data):
            print(f"Got {event_type}: {data}")

        await bus.subscribe("user.*", handler)
        await bus.publish("user.created", {"id": 1})
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[tuple[str, Dict[str, Any]]] = asyncio.Queue()
        self._handlers: Dict[str, List[RawEventHandler]] = {}
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def connect(self) -> None:
        """Start the event dispatch loop."""
        if self._running:
            return

        self._running = True

        async def _dispatcher():
            while self._running:
                try:
                    event_type, data = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0
                    )
                    await self._dispatch(event_type, data)
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Event dispatch error: {e}")

        self._task = asyncio.create_task(_dispatcher())
        logger.info("InMemoryEventBus connected")

    async def close(self) -> None:
        """Stop the dispatch loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        logger.info("InMemoryEventBus closed")

    async def publish(self, event_type: str, data: Dict[str, Any]) -> EventResult:
        """Publish an event to the queue."""
        event_id = data.get("id", "")
        await self._queue.put((event_type, data))
        return EventResult(
            event_id=event_id,
            published=True,
            routing_key=event_type
        )

    async def subscribe(
        self,
        event_pattern: str,
        handler: RawEventHandler,
    ) -> None:
        """Subscribe to events matching a pattern."""
        if event_pattern not in self._handlers:
            self._handlers[event_pattern] = []
        self._handlers[event_pattern].append(handler)
        logger.debug(f"Subscribed to pattern: {event_pattern}")

    async def _dispatch(self, event_type: str, data: Dict[str, Any]) -> None:
        """Dispatch event to matching handlers."""
        for pattern, handlers in self._handlers.items():
            if self._matches_pattern(event_type, pattern):
                for handler in handlers:
                    try:
                        await handler(event_type, data)
                    except Exception as e:
                        logger.error(f"Handler error for {event_type}: {e}")

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches subscription pattern.

        Supports:
        - Exact match: "user.created" matches "user.created"
        - Single word wildcard: "user.*" matches "user.created", "user.deleted"
        - Multi word wildcard: "user.#" matches "user.created", "user.profile.updated"
        """
        if pattern == "#":
            return True

        event_parts = event_type.split(".")
        pattern_parts = pattern.split(".")

        i = 0
        j = 0

        while i < len(event_parts) and j < len(pattern_parts):
            if pattern_parts[j] == "#":
                return True
            elif pattern_parts[j] == "*":
                i += 1
                j += 1
            elif pattern_parts[j] == event_parts[i]:
                i += 1
                j += 1
            else:
                return False

        return i == len(event_parts) and j == len(pattern_parts)


class RabbitMQEventBus(BaseEventBus):
    """RabbitMQ-based event bus for distributed systems.

    Uses topic exchange for flexible routing patterns.
    Supports durable queues and persistent messages.

    Example:
        bus = RabbitMQEventBus("amqp://guest:guest@localhost:5672/")
        await bus.connect()

        async def handler(event_type, data):
            print(f"Got {event_type}: {data}")

        await bus.subscribe("user.*", handler)
        await bus.publish("user.created", {"id": 1})
    """

    def __init__(
        self,
        amqp_url: str,
        exchange: str = "events",
        exchange_type: str = "topic",
        prefetch_count: int = 10,
    ) -> None:
        if not _rabbitmq_available:
            raise ImportError(
                "aio-pika is required for RabbitMQEventBus. "
                "Install with: pip install events-core[rabbitmq]"
            )

        self._amqp_url = amqp_url
        self._exchange_name = exchange
        self._exchange_type = exchange_type
        self._prefetch_count = prefetch_count

        self._connection = None
        self._channel = None
        self._exchange = None
        self._queues: Dict[str, aio_pika.Queue] = {}

    async def connect(self) -> None:
        """Connect to RabbitMQ and declare exchange."""
        self._connection = await aio_pika.connect_robust(self._amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._prefetch_count)

        self._exchange = await self._channel.declare_exchange(
            self._exchange_name,
            getattr(aio_pika.ExchangeType, self._exchange_type.upper()),
            durable=True,
        )
        logger.info(f"RabbitMQEventBus connected to {self._amqp_url}")

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self._connection:
            await self._connection.close()
        logger.info("RabbitMQEventBus closed")

    async def publish(self, event_type: str, data: Dict[str, Any]) -> EventResult:
        """Publish event to RabbitMQ exchange."""
        if not self._exchange:
            raise RuntimeError("Not connected. Call connect() first.")

        event_id = data.get("id", "")

        body = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }).encode()

        message = aio_pika.Message(
            body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )

        await self._exchange.publish(message, routing_key=event_type)

        return EventResult(
            event_id=event_id,
            published=True,
            routing_key=event_type
        )

    async def subscribe(
        self,
        event_pattern: str,
        handler: RawEventHandler,
    ) -> None:
        """Subscribe to events matching pattern via RabbitMQ queue."""
        if not self._channel:
            raise RuntimeError("Not connected. Call connect() first.")

        # Create unique queue for this subscription
        queue = await self._channel.declare_queue(
            "",  # Auto-generated name
            durable=True,
            auto_delete=True,
        )

        await queue.bind(self._exchange, routing_key=event_pattern)
        self._queues[event_pattern] = queue

        async def _consumer(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    event_type = payload.get("type", message.routing_key)
                    data = payload.get("data", payload)
                    await handler(event_type, data)
                except Exception as e:
                    logger.error(f"Handler error: {e}")

        await queue.consume(_consumer)
        logger.debug(f"Subscribed to RabbitMQ pattern: {event_pattern}")


def create_event_bus(
    amqp_url: Optional[str] = None,
    exchange: str = "events",
    exchange_type: str = "topic",
) -> BaseEventBus:
    """Factory function to create appropriate event bus.

    Args:
        amqp_url: RabbitMQ URL. If None, uses in-memory bus.
        exchange: RabbitMQ exchange name (ignored for in-memory)
        exchange_type: Exchange type (topic, direct, fanout)

    Returns:
        Configured event bus instance

    Example:
        # In-memory for testing
        bus = create_event_bus()

        # RabbitMQ for production
        bus = create_event_bus(amqp_url="amqp://localhost")
    """
    if amqp_url:
        return RabbitMQEventBus(
            amqp_url=amqp_url,
            exchange=exchange,
            exchange_type=exchange_type,
        )
    return InMemoryEventBus()


def is_rabbitmq_available() -> bool:
    """Check if RabbitMQ support is available."""
    return _rabbitmq_available
