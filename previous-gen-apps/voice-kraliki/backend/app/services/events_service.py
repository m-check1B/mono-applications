"""Events Service for Voice by Kraliki.

Provides event publishing for call center events using the local events-core package.

Event Types:
- call.started - When a call begins
- call.completed - When a call ends successfully
- call.failed - When a call fails
- call.transferred - When a call is transferred
- campaign.started - When a campaign begins
- campaign.completed - When a campaign ends
- agent.status_changed - When agent availability changes
- queue.threshold_exceeded - When queue metrics exceed thresholds

Usage:
    from app.services.events_service import events_service

    # Publish call event
    await events_service.publish_call_started(
        call_id="call-123",
        campaign_id="campaign-456",
        agent_id="agent-789",
    )
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Try importing events-core
_events_available = False
try:
    from events_core import BaseEventBus, Event, EventPriority, create_event_bus
    _events_available = True
except ImportError:
    logger.warning("events-core not installed. Event publishing disabled.")
    Event = None
    EventPriority = None
    BaseEventBus = None


class EventsService:
    """Service for publishing call center events.

    Wraps events-core with Voice by Kraliki specific event types.
    Falls back to logging if events-core not available.
    """

    def __init__(self):
        self._bus: BaseEventBus | None = None
        self._connected = False

    async def connect(self, amqp_url: str | None = None) -> None:
        """Connect to event bus.

        Args:
            amqp_url: RabbitMQ URL. Uses RABBITMQ_URL env var if not provided.
                     Falls back to in-memory if neither available.
        """
        if not _events_available:
            logger.info("Events disabled: events-core not installed")
            return

        url = amqp_url or os.getenv("RABBITMQ_URL")
        self._bus = create_event_bus(amqp_url=url, exchange="cc_lite_events")
        await self._bus.connect()
        self._connected = True
        logger.info(f"Events service connected (backend: {'rabbitmq' if url else 'in-memory'})")

    async def close(self) -> None:
        """Close event bus connection."""
        if self._bus:
            await self._bus.close()
            self._connected = False
            logger.info("Events service disconnected")

    async def _publish(
        self,
        event_type: str,
        data: dict[str, Any],
        priority: str = "normal",
        correlation_id: str | None = None,
    ) -> None:
        """Publish an event.

        Args:
            event_type: Event type string
            data: Event payload
            priority: Event priority (low, normal, high, critical)
            correlation_id: Optional correlation ID for tracing
        """
        if not _events_available:
            logger.debug(f"Event (disabled): {event_type} - {data}")
            return

        if not self._connected:
            logger.warning(f"Events not connected, logging only: {event_type}")
            return

        priority_map = {
            "low": EventPriority.LOW,
            "normal": EventPriority.NORMAL,
            "high": EventPriority.HIGH,
            "critical": EventPriority.CRITICAL,
        }

        event = Event(
            type=event_type,
            data=data,
            source="voice-kraliki",
            priority=priority_map.get(priority, EventPriority.NORMAL),
            correlation_id=correlation_id,
        )

        await self._bus.publish_event(event)
        logger.debug(f"Published event: {event_type}")

    # Call Events

    async def publish_call_started(
        self,
        call_id: str,
        campaign_id: str | None = None,
        agent_id: str | None = None,
        phone_number: str | None = None,
        direction: str = "outbound",
        **extra,
    ) -> None:
        """Publish call.started event."""
        await self._publish(
            "call.started",
            {
                "call_id": call_id,
                "campaign_id": campaign_id,
                "agent_id": agent_id,
                "phone_number": phone_number,
                "direction": direction,
                **extra,
            },
            correlation_id=call_id,
        )

    async def publish_call_completed(
        self,
        call_id: str,
        duration_seconds: int,
        outcome: str = "completed",
        sentiment_score: float | None = None,
        **extra,
    ) -> None:
        """Publish call.completed event."""
        await self._publish(
            "call.completed",
            {
                "call_id": call_id,
                "duration_seconds": duration_seconds,
                "outcome": outcome,
                "sentiment_score": sentiment_score,
                **extra,
            },
            correlation_id=call_id,
        )

    async def publish_call_failed(
        self,
        call_id: str,
        error_code: str,
        error_message: str,
        **extra,
    ) -> None:
        """Publish call.failed event."""
        await self._publish(
            "call.failed",
            {
                "call_id": call_id,
                "error_code": error_code,
                "error_message": error_message,
                **extra,
            },
            priority="high",
            correlation_id=call_id,
        )

    async def publish_call_transferred(
        self,
        call_id: str,
        from_agent_id: str,
        to_agent_id: str,
        reason: str | None = None,
        **extra,
    ) -> None:
        """Publish call.transferred event."""
        await self._publish(
            "call.transferred",
            {
                "call_id": call_id,
                "from_agent_id": from_agent_id,
                "to_agent_id": to_agent_id,
                "reason": reason,
                **extra,
            },
            correlation_id=call_id,
        )

    # Campaign Events

    async def publish_campaign_started(
        self,
        campaign_id: str,
        name: str,
        total_contacts: int,
        **extra,
    ) -> None:
        """Publish campaign.started event."""
        await self._publish(
            "campaign.started",
            {
                "campaign_id": campaign_id,
                "name": name,
                "total_contacts": total_contacts,
                **extra,
            },
            correlation_id=campaign_id,
        )

    async def publish_campaign_completed(
        self,
        campaign_id: str,
        total_calls: int,
        successful_calls: int,
        failed_calls: int,
        **extra,
    ) -> None:
        """Publish campaign.completed event."""
        await self._publish(
            "campaign.completed",
            {
                "campaign_id": campaign_id,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                **extra,
            },
            correlation_id=campaign_id,
        )

    # Agent Events

    async def publish_agent_status_changed(
        self,
        agent_id: str,
        old_status: str,
        new_status: str,
        **extra,
    ) -> None:
        """Publish agent.status_changed event."""
        await self._publish(
            "agent.status_changed",
            {
                "agent_id": agent_id,
                "old_status": old_status,
                "new_status": new_status,
                **extra,
            },
        )

    # Queue Events

    async def publish_queue_threshold_exceeded(
        self,
        queue_id: str,
        metric: str,
        threshold: float,
        current_value: float,
        **extra,
    ) -> None:
        """Publish queue.threshold_exceeded event."""
        await self._publish(
            "queue.threshold_exceeded",
            {
                "queue_id": queue_id,
                "metric": metric,
                "threshold": threshold,
                "current_value": current_value,
                **extra,
            },
            priority="high",
        )


# Global instance
events_service = EventsService()
