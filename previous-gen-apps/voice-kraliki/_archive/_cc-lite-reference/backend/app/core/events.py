"""
Event Publisher - RabbitMQ Integration
Implements event-driven architecture for Ocelot Platform integration
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import aio_pika
from aio_pika import Connection, Channel, ExchangeType
try:
    from events_core import InMemoryEventBus  # type: ignore
except Exception:
    InMemoryEventBus = None  # Optional

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EventPublisher:
    """
    RabbitMQ Event Publisher for cross-module communication

    Publishes events to platform event bus:
    - call.started
    - call.ended
    - call.transcribed
    - campaign.completed
    - sentiment.analyzed
    """

    def __init__(self, amqp_url: Optional[str] = None):
        """
        Initialize event publisher

        Args:
            amqp_url: RabbitMQ connection URL (defaults to localhost)
        """
        self.amqp_url = amqp_url or "amqp://guest:guest@localhost:5672/"
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None
        self.exchange_name = "ocelot.events"
        self.is_connected = False
        self._mem_bus = None

    async def connect(self):
        """Establish connection to RabbitMQ or fallback to in-memory bus"""
        from app.core.config import settings
        if getattr(settings, "USE_INMEMORY_EVENTS", False) and InMemoryEventBus is not None:
            self._mem_bus = InMemoryEventBus()
            await self._mem_bus.connect()
            self.is_connected = True
            logger.info("Using InMemoryEventBus for events")
            return
        try:
            logger.info(f"Connecting to RabbitMQ: {self.amqp_url}")
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()

            # Declare exchange for events
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                ExchangeType.TOPIC,
                durable=True,
            )

            self.is_connected = True
            logger.info("✅ Connected to RabbitMQ event bus")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            logger.warning("Event publishing will be disabled")
            self.is_connected = False

    async def disconnect(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
        self.is_connected = False

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
    ):
        """
        Publish event to platform event bus

        Args:
            event_type: Event type (e.g., "call.started", "campaign.completed")
            data: Event payload data
            organization_id: Organization ID for data isolation
            user_id: Optional user ID who triggered the event

        Example:
            await event_publisher.publish(
                event_type="call.ended",
                data={
                    "call_id": "123",
                    "duration": 180,
                    "outcome": "completed"
                },
                organization_id="org_abc",
                user_id="user_xyz"
            )
        """
        if not self.is_connected:
            logger.warning(f"Event bus not connected, skipping event: {event_type}")
            return

        try:
            # Build event payload (Ocelot Platform standard format)
            event = {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "source": "communications",  # Module identifier
                "timestamp": datetime.utcnow().isoformat(),
                "organizationId": organization_id,
                "userId": user_id,
                "data": data,
                "metadata": {
                    "version": "1.0.0",
                    "module": "cc-lite",
                },
            }

            if self._mem_bus is not None:
                await self._mem_bus.publish(f"comms.{event_type}", event)
            else:
                # Publish to exchange with routing key
                routing_key = f"comms.{event_type}"
                message = aio_pika.Message(
                    body=json.dumps(event).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                )
                await self.exchange.publish(message, routing_key=routing_key)

            logger.info(f"📤 Published event: {event_type} (id: {event['id']})")

        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

    async def subscribe(self, routing_key: str, handler):
        """
        Subscribe to events (in-memory backend only).

        Args:
            routing_key: Event routing key (e.g., 'comms.call.started')
            handler: Async function (event_type: str, data: dict) -> None
        """
        if self._mem_bus is not None:
            await self._mem_bus.subscribe(routing_key, handler)
        else:
            logger.warning("Subscribe is only supported for in-memory event bus in this module")

    # Convenience methods for common events

    async def publish_call_started(
        self,
        call_id: str,
        from_number: str,
        to_number: str,
        campaign_id: Optional[str],
        organization_id: str,
        user_id: str,
    ):
        """Publish call.started event"""
        await self.publish(
            event_type="call.started",
            data={
                "call_id": call_id,
                "from_number": from_number,
                "to_number": to_number,
                "campaign_id": campaign_id,
            },
            organization_id=organization_id,
            user_id=user_id,
        )

    async def publish_call_ended(
        self,
        call_id: str,
        duration: int,
        outcome: str,
        transcript: Optional[str],
        organization_id: str,
        user_id: str,
    ):
        """Publish call.ended event"""
        await self.publish(
            event_type="call.ended",
            data={
                "call_id": call_id,
                "duration": duration,
                "outcome": outcome,
                "transcript": transcript,
            },
            organization_id=organization_id,
            user_id=user_id,
        )

    async def publish_call_transcribed(
        self,
        call_id: str,
        transcript: str,
        language: str,
        confidence: float,
        organization_id: str,
    ):
        """Publish call.transcribed event"""
        await self.publish(
            event_type="call.transcribed",
            data={
                "call_id": call_id,
                "transcript": transcript,
                "language": language,
                "confidence": confidence,
            },
            organization_id=organization_id,
        )

    async def publish_campaign_completed(
        self,
        campaign_id: str,
        total_calls: int,
        successful_calls: int,
        failed_calls: int,
        organization_id: str,
        user_id: str,
    ):
        """Publish campaign.completed event"""
        await self.publish(
            event_type="campaign.completed",
            data={
                "campaign_id": campaign_id,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": (
                    successful_calls / total_calls if total_calls > 0 else 0
                ),
            },
            organization_id=organization_id,
            user_id=user_id,
        )

    async def publish_sentiment_analyzed(
        self,
        call_id: str,
        sentiment: str,
        score: float,
        keywords: list,
        organization_id: str,
    ):
        """Publish sentiment.analyzed event (for alerts on negative sentiment)"""
        await self.publish(
            event_type="sentiment.analyzed",
            data={
                "call_id": call_id,
                "sentiment": sentiment,
                "score": score,
                "keywords": keywords,
            },
            organization_id=organization_id,
        )


# Global event publisher instance
event_publisher = EventPublisher()


@asynccontextmanager
async def get_event_publisher():
    """Dependency injection for event publisher"""
    yield event_publisher
