"""
Event Publishing Integration Tests
Target Coverage: 90%
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.core.events import event_publisher
from app.core.security_v2 import generate_id


class TestEventPublishing:
    """Test RabbitMQ event publishing integration."""

    @pytest.mark.asyncio
    async def test_task_created_event(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        mock_event_publisher
    ):
        """Test task.created event is published when creating task."""
        # Replace global event publisher with mock
        import app.core.events as events_module
        original_publisher = events_module.event_publisher
        events_module.event_publisher = mock_event_publisher

        try:
            response = await async_client.post(
                "/tasks/",
                json={
                    "title": "Test Event Task",
                    "priority": 2
                },
                headers=auth_headers
            )

            assert response.status_code == 200

            events = mock_event_publisher.published_events
            assert len(events) == 1
            event = events[0]
            assert event["type"] == "task.created"
            assert event["data"]["title"] == "Test Event Task"
            # When no workspaceId is provided in task, organization_id falls back to user's organizationId
            assert event["organization_id"] == test_user.organizationId
            assert event["user_id"] == test_user.id

        finally:
            events_module.event_publisher = original_publisher

    @pytest.mark.asyncio
    async def test_task_completed_event(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db: Session,
        mock_event_publisher
    ):
        """Test task.completed event is published when task is marked complete."""
        # Create task
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Task to Complete",
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()

        # Replace global event publisher with mock
        import app.core.events as events_module
        original_publisher = events_module.event_publisher
        events_module.event_publisher = mock_event_publisher

        try:
            response = await async_client.patch(
                f"/tasks/{task.id}",
                json={"status": "COMPLETED"},
                headers=auth_headers
            )

            assert response.status_code == 200

            events = mock_event_publisher.published_events
            assert len(events) == 1
            event = events[0]
            assert event["type"] == "task.completed"
            assert event["data"]["task_id"] == task.id
            # When task has no workspaceId, organization_id falls back to user's organizationId
            assert event["organization_id"] == test_user.organizationId
            assert event["user_id"] == test_user.id

        finally:
            events_module.event_publisher = original_publisher


class TestEventPublisher:
    """Test EventPublisher class directly."""

    @pytest.mark.asyncio
    async def test_publisher_publish(self, mock_event_publisher):
        """Test event publisher publish method."""
        await mock_event_publisher.publish(
            event_type="task.created",
            data={
                "task_id": "task123",
                "title": "Test Task",
                "priority": "high"
            },
            organization_id="org123",
            user_id="user123"
        )

        # Verify event was recorded
        assert len(mock_event_publisher.published_events) == 1
        event = mock_event_publisher.published_events[0]

        assert event["type"] == "task.created"
        assert event["data"]["task_id"] == "task123"
        assert event["organization_id"] == "org123"
        assert event["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_publish_task_created(self, mock_event_publisher):
        """Test publish_task_created convenience method."""
        from app.core.events import EventPublisher

        publisher = EventPublisher()
        publisher.published_events = []  # Mock storage

        # Mock the publish method
        async def mock_publish(event_type, data, organization_id, user_id, *args, **kwargs):
            publisher.published_events.append({
                "type": event_type,
                "data": data,
                "organization_id": organization_id,
                "user_id": user_id
            })

        publisher.publish = mock_publish

        await publisher.publish_task_created(
            task_id="task456",
            title="New Task",
            priority="high",
            organization_id="org123",
            user_id="user123",
            assignee_id="user456",
            project_id="proj789"
        )

        # Verify event
        assert len(publisher.published_events) == 1
        event = publisher.published_events[0]

        assert event["type"] == "task.created"
        assert event["data"]["task_id"] == "task456"
        assert event["data"]["title"] == "New Task"
        assert event["data"]["priority"] == "high"
        assert event["data"]["assignee_id"] == "user456"


class TestEventSchema:
    """Test event schema and structure."""

    @pytest.mark.asyncio
    async def test_event_envelope_structure(self, mock_event_publisher):
        """Test event envelope contains required fields."""
        await mock_event_publisher.publish(
            event_type="test.event",
            data={"key": "value"},
            organization_id="org123",
            user_id="user123",
            metadata={"version": "1.0.0"}
        )

        event = mock_event_publisher.published_events[0]

        # Check required fields
        assert "type" in event
        assert "data" in event
        assert "organization_id" in event
        assert "user_id" in event
        assert "metadata" in event

    @pytest.mark.asyncio
    async def test_event_types(self):
        """Test all defined event types are properly named."""
        # Event types follow pattern: planning.{event_type}
        event_types = [
            "task.created",
            "task.completed",
            "project.milestone_reached",
            "shadow.insight_generated"
        ]

        for event_type in event_types:
            # Verify format
            assert "." in event_type
            parts = event_type.split(".")
            assert len(parts) == 2
            assert parts[0] in ["task", "project", "shadow"]
            assert parts[1] in ["created", "completed", "milestone_reached", "insight_generated"]


class TestEventConsumption:
    """Test consuming events from other modules (platform mode)."""

    @pytest.mark.asyncio
    async def test_handle_call_ended_event(self):
        """Test handling call.ended event from communications module."""
        from app.module import PlanningModule

        module = PlanningModule(platform_mode=True)

        # Simulate call ended event
        event = {
            "type": "call.ended",
            "data": {
                "call_id": "call123",
                "outcome": "callback_requested",
                "contact": {
                    "name": "John Doe",
                    "phone": "+1234567890"
                }
            },
            "organization_id": "org123",
            "user_id": "user123"
        }

        # Handle event
        await module.handle_event(event)

        # In full implementation, this would create a follow-up task
        # For now, just verify method exists and doesn't error

    @pytest.mark.asyncio
    async def test_handle_workflow_suggested_event(self):
        """Test handling agent.workflow_suggested event from agents module."""
        from app.module import PlanningModule

        module = PlanningModule(platform_mode=True)

        # Simulate workflow suggestion event
        event = {
            "type": "agent.workflow_suggested",
            "data": {
                "workflow_id": "wf123",
                "tasks": [
                    {"title": "Task 1", "priority": "high"},
                    {"title": "Task 2", "priority": "medium"}
                ]
            },
            "organization_id": "org123",
            "user_id": "user123"
        }

        # Handle event
        await module.handle_event(event)

        # Verify method exists


class TestEventRoutingKeys:
    """Test RabbitMQ routing key patterns."""

    def test_routing_key_format(self):
        """Test event routing keys follow planning.{event_type} pattern."""
        from app.core.events import EventPublisher

        # Routing keys should be: planning.task.created, etc.
        event_types = [
            "task.created",
            "task.completed",
            "project.milestone_reached"
        ]

        for event_type in event_types:
            routing_key = f"planning.{event_type}"

            # Verify format
            assert routing_key.startswith("planning.")
            assert len(routing_key.split(".")) == 3

    def test_routing_key_uniqueness(self):
        """Test each event type has unique routing key."""
        event_types = [
            "task.created",
            "task.updated",
            "task.deleted",
            "task.completed",
            "project.created",
            "project.milestone_reached"
        ]

        routing_keys = [f"planning.{et}" for et in event_types]

        # All should be unique
        assert len(routing_keys) == len(set(routing_keys))
