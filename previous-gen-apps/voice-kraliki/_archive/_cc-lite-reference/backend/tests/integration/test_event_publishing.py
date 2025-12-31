"""
Integration Tests for Event Publishing
Tests RabbitMQ event publishing functionality
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.events import EventPublisher, event_publisher


class TestEventPublisher:
    """Test suite for RabbitMQ event publisher"""

    @pytest.fixture
    async def mock_publisher(self):
        """Create event publisher with mocked RabbitMQ connection"""
        publisher = EventPublisher(amqp_url="amqp://guest:guest@localhost:5672/")

        # Mock RabbitMQ connection
        with patch("aio_pika.connect_robust") as mock_connect:
            mock_connection = AsyncMock()
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()

            mock_connect.return_value = mock_connection
            mock_connection.channel.return_value = mock_channel
            mock_channel.declare_exchange.return_value = mock_exchange

            await publisher.connect()

            # Store mocks for assertions
            publisher._mock_exchange = mock_exchange

            yield publisher

            await publisher.disconnect()

    @pytest.mark.asyncio
    async def test_connect_to_rabbitmq(self, mock_publisher):
        """Test successful connection to RabbitMQ"""
        assert mock_publisher.is_connected is True
        assert mock_publisher.exchange_name == "ocelot.events"

    @pytest.mark.asyncio
    async def test_publish_call_started_event(self, mock_publisher):
        """Test publishing call.started event"""
        await mock_publisher.publish_call_started(
            call_id="call_123",
            from_number="+1234567890",
            to_number="+0987654321",
            campaign_id="campaign_abc",
            organization_id="org_xyz",
            user_id="user_123",
        )

        # Verify publish was called
        assert mock_publisher._mock_exchange.publish.called

        # Get the published message
        call_args = mock_publisher._mock_exchange.publish.call_args
        message = call_args[0][0]

        # Verify message body
        event_data = json.loads(message.body.decode())
        assert event_data["type"] == "call.started"
        assert event_data["source"] == "communications"
        assert event_data["organizationId"] == "org_xyz"
        assert event_data["userId"] == "user_123"
        assert event_data["data"]["call_id"] == "call_123"
        assert event_data["data"]["from_number"] == "+1234567890"

    @pytest.mark.asyncio
    async def test_publish_call_ended_event(self, mock_publisher):
        """Test publishing call.ended event"""
        await mock_publisher.publish_call_ended(
            call_id="call_123",
            duration=180,
            outcome="completed",
            transcript="Sample transcript",
            organization_id="org_xyz",
            user_id="user_123",
        )

        # Verify publish was called
        assert mock_publisher._mock_exchange.publish.called

        # Get the published message
        call_args = mock_publisher._mock_exchange.publish.call_args
        message = call_args[0][0]

        # Verify message body
        event_data = json.loads(message.body.decode())
        assert event_data["type"] == "call.ended"
        assert event_data["data"]["duration"] == 180
        assert event_data["data"]["outcome"] == "completed"
        assert event_data["data"]["transcript"] == "Sample transcript"

    @pytest.mark.asyncio
    async def test_publish_campaign_completed_event(self, mock_publisher):
        """Test publishing campaign.completed event"""
        await mock_publisher.publish_campaign_completed(
            campaign_id="campaign_abc",
            total_calls=100,
            successful_calls=85,
            failed_calls=15,
            organization_id="org_xyz",
            user_id="user_123",
        )

        # Verify publish was called
        assert mock_publisher._mock_exchange.publish.called

        # Get the published message
        call_args = mock_publisher._mock_exchange.publish.call_args
        message = call_args[0][0]

        # Verify message body
        event_data = json.loads(message.body.decode())
        assert event_data["type"] == "campaign.completed"
        assert event_data["data"]["total_calls"] == 100
        assert event_data["data"]["successful_calls"] == 85
        assert event_data["data"]["success_rate"] == 0.85

    @pytest.mark.asyncio
    async def test_publish_sentiment_analyzed_event(self, mock_publisher):
        """Test publishing sentiment.analyzed event"""
        await mock_publisher.publish_sentiment_analyzed(
            call_id="call_123",
            sentiment="negative",
            score=-0.75,
            keywords=["frustrated", "angry", "disappointed"],
            organization_id="org_xyz",
        )

        # Verify publish was called
        assert mock_publisher._mock_exchange.publish.called

        # Get the published message
        call_args = mock_publisher._mock_exchange.publish.call_args
        message = call_args[0][0]

        # Verify message body
        event_data = json.loads(message.body.decode())
        assert event_data["type"] == "sentiment.analyzed"
        assert event_data["data"]["sentiment"] == "negative"
        assert event_data["data"]["score"] == -0.75
        assert "frustrated" in event_data["data"]["keywords"]

    @pytest.mark.asyncio
    async def test_event_has_standard_fields(self, mock_publisher):
        """Test that all events have standard Ocelot Platform fields"""
        await mock_publisher.publish(
            event_type="test.event",
            data={"test": "data"},
            organization_id="org_xyz",
            user_id="user_123",
        )

        # Get the published message
        call_args = mock_publisher._mock_exchange.publish.call_args
        message = call_args[0][0]
        event_data = json.loads(message.body.decode())

        # Verify standard fields
        assert "id" in event_data
        assert "type" in event_data
        assert "source" in event_data
        assert "timestamp" in event_data
        assert "organizationId" in event_data
        assert "userId" in event_data
        assert "data" in event_data
        assert "metadata" in event_data

        assert event_data["source"] == "communications"
        assert event_data["metadata"]["version"] == "1.0.0"

    @pytest.mark.asyncio
    async def test_publish_with_routing_key(self, mock_publisher):
        """Test that events are published with correct routing key"""
        await mock_publisher.publish(
            event_type="call.started",
            data={"test": "data"},
            organization_id="org_xyz",
        )

        # Verify routing key
        call_args = mock_publisher._mock_exchange.publish.call_args
        routing_key = call_args.kwargs["routing_key"]
        assert routing_key == "comms.call.started"

    @pytest.mark.asyncio
    async def test_publish_when_not_connected(self):
        """Test graceful handling when RabbitMQ is not connected"""
        publisher = EventPublisher()
        publisher.is_connected = False

        # Should not raise exception
        await publisher.publish(
            event_type="test.event",
            data={"test": "data"},
            organization_id="org_xyz",
        )

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_publisher):
        """Test disconnecting from RabbitMQ"""
        await mock_publisher.disconnect()
        assert mock_publisher.is_connected is False


class TestEventPublisherIntegration:
    """Integration tests with real RabbitMQ (requires running RabbitMQ)"""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires running RabbitMQ instance")
    @pytest.mark.asyncio
    async def test_real_rabbitmq_connection(self):
        """Test real connection to RabbitMQ (skip if not available)"""
        publisher = EventPublisher(amqp_url="amqp://guest:guest@localhost:5672/")

        try:
            await publisher.connect()
            assert publisher.is_connected is True

            # Publish test event
            await publisher.publish(
                event_type="test.integration",
                data={"message": "Integration test"},
                organization_id="test_org",
            )

        finally:
            await publisher.disconnect()


# Run tests with: pytest backend/tests/integration/test_event_publishing.py -v
# Run with real RabbitMQ: pytest backend/tests/integration/test_event_publishing.py -v -m integration
