"""Tests for event bus implementations."""

import asyncio
import pytest
from events_core import (
    Event,
    EventPriority,
    InMemoryEventBus,
    create_event_bus,
    is_rabbitmq_available,
)


@pytest.fixture
async def event_bus():
    """Create and connect an in-memory event bus."""
    bus = create_event_bus()
    await bus.connect()
    yield bus
    await bus.close()


class TestInMemoryEventBus:
    """Tests for InMemoryEventBus."""

    async def test_publish_subscribe_raw(self, event_bus):
        """Test basic publish/subscribe with raw handlers."""
        received = []

        async def handler(event_type: str, data: dict):
            received.append((event_type, data))

        await event_bus.subscribe("test.event", handler)
        result = await event_bus.publish("test.event", {"key": "value"})

        await asyncio.sleep(0.1)

        assert result.published
        assert len(received) == 1
        assert received[0][0] == "test.event"
        assert received[0][1]["key"] == "value"

    async def test_publish_subscribe_typed(self, event_bus):
        """Test typed Event publish/subscribe."""
        received = []

        async def handler(event: Event):
            received.append(event)

        await event_bus.subscribe_typed("user.created", handler)

        event = Event(
            type="user.created",
            data={"user_id": "123"},
            source="test",
        )
        await event_bus.publish_event(event)

        await asyncio.sleep(0.1)

        assert len(received) == 1
        assert received[0].type == "user.created"
        assert received[0].data["user_id"] == "123"

    async def test_pattern_matching_star(self, event_bus):
        """Test single-word wildcard pattern matching."""
        received = []

        async def handler(event_type: str, data: dict):
            received.append(event_type)

        await event_bus.subscribe("user.*", handler)

        await event_bus.publish("user.created", {})
        await event_bus.publish("user.deleted", {})
        await event_bus.publish("order.created", {})  # Should not match

        await asyncio.sleep(0.1)

        assert len(received) == 2
        assert "user.created" in received
        assert "user.deleted" in received

    async def test_pattern_matching_hash(self, event_bus):
        """Test multi-word wildcard pattern matching."""
        received = []

        async def handler(event_type: str, data: dict):
            received.append(event_type)

        await event_bus.subscribe("user.#", handler)

        await event_bus.publish("user.created", {})
        await event_bus.publish("user.profile.updated", {})
        await event_bus.publish("order.created", {})  # Should not match

        await asyncio.sleep(0.1)

        assert len(received) == 2
        assert "user.created" in received
        assert "user.profile.updated" in received

    async def test_multiple_handlers(self, event_bus):
        """Test multiple handlers for same pattern."""
        results1 = []
        results2 = []

        async def handler1(event_type: str, data: dict):
            results1.append(event_type)

        async def handler2(event_type: str, data: dict):
            results2.append(event_type)

        await event_bus.subscribe("test.*", handler1)
        await event_bus.subscribe("test.*", handler2)

        await event_bus.publish("test.event", {})

        await asyncio.sleep(0.1)

        assert len(results1) == 1
        assert len(results2) == 1


class TestEvent:
    """Tests for Event model."""

    def test_event_defaults(self):
        """Test Event with default values."""
        event = Event(type="test.event")

        assert event.type == "test.event"
        assert event.data == {}
        assert event.id is not None
        assert event.timestamp is not None
        assert event.priority == EventPriority.NORMAL

    def test_event_with_data(self):
        """Test Event with custom data."""
        event = Event(
            type="user.created",
            data={"user_id": "123"},
            source="auth-service",
            priority=EventPriority.HIGH,
            correlation_id="req-456",
        )

        assert event.type == "user.created"
        assert event.data["user_id"] == "123"
        assert event.source == "auth-service"
        assert event.priority == EventPriority.HIGH
        assert event.correlation_id == "req-456"


class TestFactoryFunction:
    """Tests for create_event_bus factory."""

    def test_create_inmemory_bus(self):
        """Test creating in-memory bus."""
        bus = create_event_bus()
        assert isinstance(bus, InMemoryEventBus)

    def test_create_inmemory_without_url(self):
        """Test that None URL creates in-memory bus."""
        bus = create_event_bus(amqp_url=None)
        assert isinstance(bus, InMemoryEventBus)


class TestRabbitMQAvailability:
    """Tests for RabbitMQ availability check."""

    def test_is_rabbitmq_available(self):
        """Test that availability check works."""
        result = is_rabbitmq_available()
        assert isinstance(result, bool)
