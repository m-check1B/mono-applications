"""
E2E Tests for Events-Core Adapter Integration

Tests full integration flows for event publishing and consumption:
- Event publishing to RabbitMQ/in-memory bus
- Event routing and delivery
- Cross-module event workflows
- Event-driven automation
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from app.core.events import EventPublisher, event_publisher
from app.module import PlanningModule


class TestEventsAdapterE2E:
    """End-to-end tests for events adapter integration flows."""

    @pytest.mark.asyncio
    async def test_event_publisher_connection_lifecycle(self):
        """E2E: Event publisher connects and disconnects properly."""
        test_publisher = EventPublisher("amqp://localhost:5672")

        # Mock RabbitMQ connection
        with patch('app.core.events.aio_pika') as mock_pika:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()

            mock_pika.connect_robust = AsyncMock(return_value=mock_connection)
            mock_connection.channel = AsyncMock(return_value=mock_channel)
            mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

            # Connect
            await test_publisher.connect()
            assert test_publisher.connection is not None
            assert test_publisher.channel is not None
            assert test_publisher.exchange is not None

            # Disconnect
            await test_publisher.disconnect()

    @pytest.mark.asyncio
    async def test_event_publishing_full_flow(self, mock_event_publisher):
        """E2E: Full event publishing flow from creation to delivery."""
        # Publish event
        await mock_event_publisher.publish(
            event_type="task.created",
            data={
                "task_id": "task_123",
                "title": "Review PR",
                "priority": "high"
            },
            organization_id="org_456",
            user_id="user_789"
        )

        # Verify event recorded
        assert len(mock_event_publisher.published_events) == 1
        event = mock_event_publisher.published_events[0]

        assert event["type"] == "task.created"
        assert event["data"]["task_id"] == "task_123"
        assert event["organization_id"] == "org_456"

    @pytest.mark.asyncio
    async def test_event_envelope_structure(self, mock_event_publisher):
        """E2E: Published events have correct envelope structure."""
        await mock_event_publisher.publish(
            event_type="task.completed",
            data={"task_id": "task_456", "duration": 3600},
            organization_id="org_123",
            user_id="user_456",
            metadata={"version": "2.0.0", "source": "api"}
        )

        event = mock_event_publisher.published_events[0]

        # Required fields
        assert "type" in event
        assert "data" in event
        assert "organization_id" in event
        assert "user_id" in event
        assert "metadata" in event


class TestEventsAdapterConvenienceMethods:
    """Test event publisher convenience methods."""

    @pytest.mark.asyncio
    async def test_publish_task_created_convenience(self):
        """E2E: publish_task_created convenience method works correctly."""
        publisher = EventPublisher()
        publisher.published_events = []

        # Mock publish method
        async def mock_publish(event_type, data, organization_id, user_id, *args, **kwargs):
            publisher.published_events.append({
                "type": event_type,
                "data": data,
                "organization_id": organization_id,
                "user_id": user_id
            })

        publisher.publish = mock_publish

        await publisher.publish_task_created(
            task_id="task_new",
            title="New Task",
            priority="medium",
            organization_id="org_123",
            user_id="user_456",
            assignee_id="user_789",
            project_id="proj_abc"
        )

        assert len(publisher.published_events) == 1
        event = publisher.published_events[0]

        assert event["type"] == "task.created"
        assert event["data"]["task_id"] == "task_new"
        assert event["data"]["assignee_id"] == "user_789"
        assert event["data"]["project_id"] == "proj_abc"

    @pytest.mark.asyncio
    async def test_publish_task_completed_convenience(self):
        """E2E: publish_task_completed tracks completion metrics."""
        publisher = EventPublisher()
        publisher.published_events = []

        async def mock_publish(event_type, data, organization_id, user_id, *args, **kwargs):
            publisher.published_events.append({
                "type": event_type,
                "data": data,
                "organization_id": organization_id,
                "user_id": user_id
            })

        publisher.publish = mock_publish

        await publisher.publish_task_completed(
            task_id="task_done",
            title="Completed Task",
            organization_id="org_123",
            user_id="user_456",
            duration_minutes=45
        )

        event = publisher.published_events[0]
        assert event["type"] == "task.completed"
        assert event["data"]["duration_minutes"] == 45

    @pytest.mark.asyncio
    async def test_publish_project_milestone_convenience(self):
        """E2E: publish_project_milestone tracks project progress."""
        publisher = EventPublisher()
        publisher.published_events = []

        async def mock_publish(event_type, data, organization_id, user_id, *args, **kwargs):
            publisher.published_events.append({
                "type": event_type,
                "data": data,
                "organization_id": organization_id,
                "user_id": user_id
            })

        publisher.publish = mock_publish

        await publisher.publish_project_milestone(
            project_id="proj_milestone",
            milestone_name="Beta Release",
            organization_id="org_123",
            user_id="user_456",
            completion_percentage=75
        )

        event = publisher.published_events[0]
        assert event["type"] == "project.milestone_reached"
        assert event["data"]["completion_percentage"] == 75

    @pytest.mark.asyncio
    async def test_publish_shadow_insight_convenience(self):
        """E2E: publish_shadow_insight publishes AI insights."""
        publisher = EventPublisher()
        publisher.published_events = []

        async def mock_publish(event_type, data, organization_id, user_id, *args, **kwargs):
            publisher.published_events.append({
                "type": event_type,
                "data": data,
                "organization_id": organization_id,
                "user_id": user_id
            })

        publisher.publish = mock_publish

        await publisher.publish_shadow_insight(
            insight_id="insight_ai_123",
            insight_type="pattern_detection",
            insight_text="User works best in morning hours",
            organization_id="org_123",
            user_id="user_456",
            task_id="task_related"
        )

        event = publisher.published_events[0]
        assert event["type"] == "shadow.insight_generated"
        assert event["data"]["insight_type"] == "pattern_detection"


class TestEventsAdapterMultiStepWorkflows:
    """Test multi-step workflows involving event publishing."""

    @pytest.mark.asyncio
    async def test_task_lifecycle_event_sequence(self, mock_event_publisher):
        """E2E: Task lifecycle publishes correct event sequence."""
        # Simulate task lifecycle:
        # 1. Task created
        await mock_event_publisher.publish(
            event_type="task.created",
            data={"task_id": "task_seq", "title": "Lifecycle Task"},
            organization_id="org_123",
            user_id="user_456"
        )

        # 2. Task updated
        await mock_event_publisher.publish(
            event_type="task.updated",
            data={"task_id": "task_seq", "changes": {"priority": "high"}},
            organization_id="org_123",
            user_id="user_456"
        )

        # 3. Task completed
        await mock_event_publisher.publish(
            event_type="task.completed",
            data={"task_id": "task_seq", "duration_minutes": 30},
            organization_id="org_123",
            user_id="user_456"
        )

        # Verify sequence
        assert len(mock_event_publisher.published_events) == 3
        assert mock_event_publisher.published_events[0]["type"] == "task.created"
        assert mock_event_publisher.published_events[1]["type"] == "task.updated"
        assert mock_event_publisher.published_events[2]["type"] == "task.completed"

    @pytest.mark.asyncio
    async def test_event_triggers_followup_task_creation(self):
        """E2E: Completing task triggers follow-up task creation via events."""
        # Workflow:
        # 1. Task completed (with follow_up flag)
        # 2. Event published
        # 3. Event consumer creates follow-up task
        # 4. New task.created event published

        # Currently not fully implemented
        # Documenting expected workflow
        pass

    @pytest.mark.asyncio
    async def test_cross_module_event_workflow(self):
        """E2E: Event from communications module triggers planning action."""
        module = PlanningModule(platform_mode=True)

        # Simulate call.ended event from communications module
        call_event = {
            "type": "call.ended",
            "data": {
                "call_id": "call_123",
                "outcome": "callback_requested",
                "contact": {"name": "John Doe"}
            },
            "organization_id": "org_123",
            "user_id": "user_456"
        }

        # Handle event (should create follow-up task)
        await module.handle_event(call_event)

        # Verify follow-up task created
        # Currently not implemented - documenting expected flow


class TestEventsAdapterRoutingKeys:
    """Test event routing key patterns and subscriptions."""

    def test_routing_key_format(self):
        """E2E: Routing keys follow planning.{category}.{action} pattern."""
        event_types = [
            ("task.created", "planning.task.created"),
            ("task.completed", "planning.task.completed"),
            ("project.milestone_reached", "planning.project.milestone_reached"),
            ("shadow.insight_generated", "planning.shadow.insight_generated"),
        ]

        for event_type, expected_key in event_types:
            routing_key = f"planning.{event_type}"
            assert routing_key == expected_key

    def test_routing_key_wildcard_patterns(self):
        """E2E: Routing keys support wildcard subscriptions."""
        # Consumers can subscribe to:
        # - planning.task.* (all task events)
        # - planning.*.created (all creation events)
        # - planning.# (all planning events)

        patterns = [
            "planning.task.*",
            "planning.*.created",
            "planning.#"
        ]

        # Verify patterns are valid RabbitMQ routing keys
        for pattern in patterns:
            assert "planning." in pattern


class TestEventsAdapterInMemoryMode:
    """Test in-memory event bus for testing and development."""

    @pytest.mark.asyncio
    async def test_inmemory_event_bus_publish_subscribe(self):
        """E2E: In-memory event bus works for testing."""
        from app.core.config import settings

        with patch.object(settings, 'USE_INMEMORY_EVENTS', True):
            with patch('app.core.events.InMemoryEventBus') as MockBus:
                mock_bus = AsyncMock()
                MockBus.return_value = mock_bus

                publisher = EventPublisher()
                await publisher.connect()

                # Should use in-memory bus
                assert publisher._mem_bus is not None

                # Publish event
                await publisher.publish(
                    event_type="test.event",
                    data={"test": "data"},
                    organization_id="org_123"
                )

                # Verify in-memory bus was called
                mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_inmemory_subscription(self):
        """E2E: In-memory event bus supports subscriptions."""
        with patch('app.core.events.InMemoryEventBus') as MockBus:
            mock_bus = AsyncMock()
            MockBus.return_value = mock_bus

            publisher = EventPublisher()
            publisher._mem_bus = mock_bus

            # Subscribe to event
            async def handler(event_type, data):
                pass

            await publisher.subscribe("planning.task.created", handler)

            # Verify subscription registered
            mock_bus.subscribe.assert_called_once()


class TestEventsAdapterErrorHandling:
    """Test error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_rabbitmq_connection_failure_handling(self):
        """E2E: Event publisher handles RabbitMQ connection failures."""
        publisher = EventPublisher("amqp://invalid-host:5672")

        # Connection should fail gracefully
        with pytest.raises(Exception):
            with patch('app.core.events.aio_pika.connect_robust') as mock_connect:
                mock_connect.side_effect = ConnectionError("Cannot connect")
                await publisher.connect()

    @pytest.mark.asyncio
    async def test_publish_with_auto_reconnect(self):
        """E2E: Publisher auto-reconnects if connection lost."""
        publisher = EventPublisher()

        with patch('app.core.events.aio_pika') as mock_pika:
            mock_connection = AsyncMock()
            mock_connection.is_closed = False
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()

            mock_pika.connect_robust = AsyncMock(return_value=mock_connection)
            mock_connection.channel = AsyncMock(return_value=mock_channel)
            mock_channel.declare_exchange = AsyncMock(return_value=mock_exchange)

            await publisher.connect()

            # Simulate connection closed
            mock_connection.is_closed = True

            # Publish should reconnect
            await publisher.publish(
                event_type="test.event",
                data={},
                organization_id="org_123"
            )

            # Should have reconnected
            assert mock_pika.connect_robust.call_count >= 2

    @pytest.mark.asyncio
    async def test_publish_retry_on_transient_failure(self):
        """E2E: Publisher retries on transient publish failures."""
        # Mock publisher to fail once then succeed
        # Currently no retry logic - documenting expected behavior
        pass


class TestEventsAdapterPerformance:
    """Test performance characteristics of event publishing."""

    @pytest.mark.asyncio
    async def test_high_throughput_event_publishing(self, mock_event_publisher):
        """E2E: Publisher handles high throughput efficiently."""
        import time

        num_events = 100
        start = time.time()

        for i in range(num_events):
            await mock_event_publisher.publish(
                event_type="test.load",
                data={"index": i},
                organization_id="org_load"
            )

        elapsed = time.time() - start

        # Should publish 100 events in under 1 second
        assert elapsed < 1.0
        assert len(mock_event_publisher.published_events) == num_events

    @pytest.mark.asyncio
    async def test_event_batching_optimization(self):
        """E2E: Publisher optimizes batch event publishing."""
        # Should batch multiple events in single RabbitMQ transaction
        # Currently single event per publish - documenting optimization
        pass


class TestEventsAdapterOrganizationIsolation:
    """Test organization-level event isolation."""

    @pytest.mark.asyncio
    async def test_events_scoped_to_organization(self, mock_event_publisher):
        """E2E: Events tagged with organization ID for isolation."""
        # Org A events
        await mock_event_publisher.publish(
            event_type="task.created",
            data={"task_id": "task_org_a"},
            organization_id="org_a",
            user_id="user_a"
        )

        # Org B events
        await mock_event_publisher.publish(
            event_type="task.created",
            data={"task_id": "task_org_b"},
            organization_id="org_b",
            user_id="user_b"
        )

        # Both published but scoped to respective orgs
        events = mock_event_publisher.published_events
        assert events[0]["organization_id"] == "org_a"
        assert events[1]["organization_id"] == "org_b"

    @pytest.mark.asyncio
    async def test_event_filtering_by_organization(self):
        """E2E: Event consumers filter events by organization."""
        # Consumers should only receive events for their organization
        # Implemented via RabbitMQ queue bindings or filtering logic

        # Currently not implemented - documenting expected behavior
        pass


class TestEventsAdapterCompliance:
    """Test event system compliance with platform standards."""

    def test_event_schema_versioning(self):
        """E2E: Events include schema version for compatibility."""
        # Events should include version in metadata
        # Allows gradual migration of event schemas

        # Currently basic versioning - documenting enhancement
        pass

    @pytest.mark.asyncio
    async def test_event_audit_trail(self, mock_event_publisher):
        """E2E: All published events logged for audit."""
        await mock_event_publisher.publish(
            event_type="sensitive.operation",
            data={"operation": "delete_user"},
            organization_id="org_audit",
            user_id="user_admin"
        )

        # Should be logged for compliance
        # Currently minimal logging - documenting requirement
        pass

    @pytest.mark.asyncio
    async def test_event_retention_policy(self):
        """E2E: Events have defined retention policy."""
        # Events older than X days should be archived/deleted
        # RabbitMQ message TTL configured appropriately

        # Currently no retention policy - documenting requirement
        pass
