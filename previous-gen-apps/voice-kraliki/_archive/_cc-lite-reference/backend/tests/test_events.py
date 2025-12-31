import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.events import EventPublisher

@pytest.mark.asyncio
async def test_event_publisher_connect():
    """Test RabbitMQ connection"""
    publisher = EventPublisher("amqp://guest:guest@localhost:5672/")

    with patch('aio_pika.connect_robust', new_callable=AsyncMock) as mock_connect:
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.channel.return_value = mock_channel
        mock_channel.declare_exchange.return_value = mock_exchange
        mock_connect.return_value = mock_connection

        await publisher.connect()

        assert publisher.connection is not None
        assert publisher.channel is not None
        assert publisher.is_connected is True
        mock_connect.assert_called_once()

@pytest.mark.asyncio
async def test_publish_call_ended_event():
    """Test publishing call.ended event"""
    publisher = EventPublisher()
    publisher.is_connected = True
    publisher.exchange = AsyncMock()

    await publisher.publish(
        event_type="call.ended",
        data={"call_id": "123", "duration": 300},
        organization_id="org-1",
        user_id="user-1"
    )

    publisher.exchange.publish.assert_called_once()
    call_args = publisher.exchange.publish.call_args
    assert call_args[1]['routing_key'] == "comms.call.ended"

@pytest.mark.asyncio
async def test_publish_campaign_completed_event():
    """Test publishing campaign.completed event"""
    publisher = EventPublisher()
    publisher.is_connected = True
    publisher.exchange = AsyncMock()

    await publisher.publish(
        event_type="campaign.completed",
        data={"campaign_id": "c-1", "total_calls": 100},
        organization_id="org-1"
    )

    publisher.exchange.publish.assert_called_once()
    call_args = publisher.exchange.publish.call_args
    assert call_args[1]['routing_key'] == "comms.campaign.completed"

@pytest.mark.asyncio
async def test_event_structure():
    """Test event JSON structure"""
    import json
    from unittest.mock import ANY

    publisher = EventPublisher()
    publisher.is_connected = True
    publisher.exchange = AsyncMock()

    await publisher.publish(
        event_type="call.started",
        data={"call_id": "456"},
        organization_id="org-1",
        user_id="user-1"
    )

    message = publisher.exchange.publish.call_args[0][0]
    event = json.loads(message.body.decode())

    assert event["type"] == "call.started"
    assert event["source"] == "communications"
    assert event["organizationId"] == "org-1"
    assert event["userId"] == "user-1"
    assert "id" in event
    assert "timestamp" in event
    assert event["metadata"]["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_publish_call_started_convenience_method():
    """Test convenience method for call.started event"""
    publisher = EventPublisher()
    publisher.is_connected = True

    with patch.object(publisher, 'publish', new_callable=AsyncMock) as mock_publish:
        await publisher.publish_call_started(
            call_id="call-123",
            from_number="+15551234567",
            to_number="+15559876543",
            campaign_id="campaign-1",
            organization_id="org-1",
            user_id="user-1"
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[1]["event_type"] == "call.started"
        assert call_args[1]["data"]["call_id"] == "call-123"

@pytest.mark.asyncio
async def test_publish_call_ended_convenience_method():
    """Test convenience method for call.ended event"""
    publisher = EventPublisher()
    publisher.is_connected = True

    with patch.object(publisher, 'publish', new_callable=AsyncMock) as mock_publish:
        await publisher.publish_call_ended(
            call_id="call-123",
            duration=180,
            outcome="completed",
            transcript="Test transcript",
            organization_id="org-1",
            user_id="user-1"
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[1]["event_type"] == "call.ended"
        assert call_args[1]["data"]["duration"] == 180

@pytest.mark.asyncio
async def test_publish_sentiment_analyzed_event():
    """Test publishing sentiment.analyzed event"""
    publisher = EventPublisher()
    publisher.is_connected = True

    with patch.object(publisher, 'publish', new_callable=AsyncMock) as mock_publish:
        await publisher.publish_sentiment_analyzed(
            call_id="call-123",
            sentiment="negative",
            score=-0.75,
            keywords=["frustrated", "angry"],
            organization_id="org-1"
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[1]["event_type"] == "sentiment.analyzed"
        assert call_args[1]["data"]["sentiment"] == "negative"
        assert call_args[1]["data"]["score"] == -0.75

@pytest.mark.asyncio
async def test_publish_when_not_connected():
    """Test that publish handles disconnected state gracefully"""
    publisher = EventPublisher()
    publisher.is_connected = False

    # Should not raise exception, just log warning
    await publisher.publish(
        event_type="test.event",
        data={"test": "data"},
        organization_id="org-1"
    )

@pytest.mark.asyncio
async def test_disconnect():
    """Test disconnecting from RabbitMQ"""
    publisher = EventPublisher()

    mock_connection = AsyncMock()
    mock_connection.is_closed = False
    publisher.connection = mock_connection
    publisher.is_connected = True

    await publisher.disconnect()

    mock_connection.close.assert_called_once()
    assert publisher.is_connected is False

@pytest.mark.asyncio
async def test_publish_call_transcribed_event():
    """Test publishing call.transcribed event"""
    publisher = EventPublisher()
    publisher.is_connected = True

    with patch.object(publisher, 'publish', new_callable=AsyncMock) as mock_publish:
        await publisher.publish_call_transcribed(
            call_id="call-123",
            transcript="Hello, how can I help you today?",
            language="en-US",
            confidence=0.95,
            organization_id="org-1"
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[1]["event_type"] == "call.transcribed"
        assert call_args[1]["data"]["confidence"] == 0.95

@pytest.mark.asyncio
async def test_publish_campaign_completed_convenience_method():
    """Test convenience method for campaign.completed event"""
    publisher = EventPublisher()
    publisher.is_connected = True

    with patch.object(publisher, 'publish', new_callable=AsyncMock) as mock_publish:
        await publisher.publish_campaign_completed(
            campaign_id="campaign-1",
            total_calls=150,
            successful_calls=120,
            failed_calls=30,
            organization_id="org-1",
            user_id="user-1"
        )

        mock_publish.assert_called_once()
        call_args = mock_publish.call_args
        assert call_args[1]["event_type"] == "campaign.completed"
        assert call_args[1]["data"]["total_calls"] == 150
        assert call_args[1]["data"]["success_rate"] == 0.8
