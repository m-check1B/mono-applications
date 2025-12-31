"""
Event Publisher Tests for Focus by Kraliki

Tests the RabbitMQ event publishing functionality without requiring
a running RabbitMQ instance (uses mocks).
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json


# Import after path is set
from app.core.events import EventPublisher


@pytest.mark.asyncio
async def test_event_publisher_connect():
    """Test that EventPublisher can connect to RabbitMQ."""
    publisher = EventPublisher()

    with patch('aio_pika.connect_robust', new_callable=AsyncMock) as mock_connect:
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_exchange.return_value = mock_exchange
        mock_connect.return_value = mock_connection

        await publisher.connect()

        assert publisher.connection is not None
        assert publisher.channel is not None
        assert publisher.exchange is not None
        mock_connect.assert_called_once()


@pytest.mark.asyncio
async def test_publish_task_created_event():
    """Test publishing task.created event."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish(
            event_type="task.created",
            data={"task_id": "123", "title": "Test task"},
            organization_id="org-1",
            user_id="user-1"
        )

        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == "planning.task.created"


@pytest.mark.asyncio
async def test_publish_milestone_event():
    """Test publishing project.milestone_reached event."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish(
            event_type="project.milestone_reached",
            data={"project_id": "p-1", "milestone": "Phase 1"},
            organization_id="org-1"
        )

        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == "planning.project.milestone_reached"


@pytest.mark.asyncio
async def test_event_structure():
    """Test that published events have correct structure."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish(
            event_type="task.completed",
            data={"task_id": "456"},
            organization_id="org-1",
            user_id="user-1"
        )

        message = mock_exchange.publish.call_args[0][0]
        event = json.loads(message.body.decode())

        assert event["type"] == "task.completed"
        assert event["source"] == "planning"
        assert event["organizationId"] == "org-1"
        assert event["userId"] == "user-1"
        assert "id" in event
        assert "timestamp" in event
        assert "metadata" in event


@pytest.mark.asyncio
async def test_publish_task_created_helper():
    """Test the publish_task_created helper method."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish_task_created(
            task_id="task-123",
            title="Fix bug",
            priority="high",
            organization_id="org-xyz",
            user_id="user-456",
            assignee_id="user-789"
        )

        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == "planning.task.created"

        message = call_args[0][0]
        event = json.loads(message.body.decode())
        assert event["data"]["task_id"] == "task-123"
        assert event["data"]["priority"] == "high"


@pytest.mark.asyncio
async def test_publish_task_completed_helper():
    """Test the publish_task_completed helper method."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish_task_completed(
            task_id="task-123",
            title="Bug fixed",
            organization_id="org-xyz",
            user_id="user-456",
            duration_minutes=45
        )

        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == "planning.task.completed"

        message = call_args[0][0]
        event = json.loads(message.body.decode())
        assert event["data"]["task_id"] == "task-123"
        assert event["data"]["duration_minutes"] == 45


@pytest.mark.asyncio
async def test_publish_shadow_insight_helper():
    """Test the publish_shadow_insight helper method."""
    publisher = EventPublisher()

    # Mock the connection check
    publisher.connection = MagicMock()
    publisher.connection.is_closed = False

    with patch.object(publisher, 'exchange', AsyncMock()) as mock_exchange:
        await publisher.publish_shadow_insight(
            insight_id="insight-123",
            insight_type="workflow_optimization",
            insight_text="Consider batching similar tasks",
            organization_id="org-xyz",
            user_id="user-456",
            task_id="task-789"
        )

        mock_exchange.publish.assert_called_once()
        call_args = mock_exchange.publish.call_args
        assert call_args[1]['routing_key'] == "planning.shadow.insight_generated"

        message = call_args[0][0]
        event = json.loads(message.body.decode())
        assert event["data"]["insight_type"] == "workflow_optimization"
        assert event["data"]["task_id"] == "task-789"
