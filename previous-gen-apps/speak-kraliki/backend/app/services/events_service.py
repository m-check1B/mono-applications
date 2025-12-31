"""Events Service for Speak by Kraliki.

Provides event publishing for employee voice intelligence using platform-2026 events-core.

Event Types:
- survey.created - When a new survey is created
- survey.sent - When survey invites are sent
- survey.closed - When a survey closes
- conversation.started - When an employee starts a voice conversation
- conversation.completed - When a conversation ends
- response.received - When a survey response is submitted
- action.created - When a follow-up action is created
- action.resolved - When an action is marked as resolved
- alert.triggered - When an automated alert fires
- insight.generated - When new insights are computed

Usage:
    from app.services.events_service import events_service

    # Publish conversation event
    await events_service.publish_conversation_completed(
        conversation_id="conv-123",
        survey_id="survey-456",
        sentiment_score=0.75,
    )
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try importing events-core
_events_available = False
try:
    from events_core import Event, EventPriority, create_event_bus, BaseEventBus
    _events_available = True
except ImportError:
    logger.warning("events-core not installed. Event publishing disabled.")
    Event = None
    EventPriority = None
    BaseEventBus = None


class EventsService:
    """Service for publishing Speak by Kraliki events.

    Wraps events-core with speak-specific event types.
    Falls back to logging if events-core not available.
    """

    def __init__(self):
        self._bus: Optional[BaseEventBus] = None
        self._connected = False

    async def connect(self, amqp_url: Optional[str] = None) -> None:
        """Connect to event bus.

        Args:
            amqp_url: RabbitMQ URL. Uses RABBITMQ_URL env var if not provided.
                     Falls back to in-memory if neither available.
        """
        if not _events_available:
            logger.info("Events disabled: events-core not installed")
            return

        url = amqp_url or os.getenv("RABBITMQ_URL")
        self._bus = create_event_bus(amqp_url=url, exchange="vop_events")
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
        data: Dict[str, Any],
        priority: str = "normal",
        correlation_id: Optional[str] = None,
    ) -> None:
        """Publish an event."""
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
            source="speak-kraliki",
            priority=priority_map.get(priority, EventPriority.NORMAL),
            correlation_id=correlation_id,
        )

        await self._bus.publish_event(event)
        logger.debug(f"Published event: {event_type}")

    # Survey Events

    async def publish_survey_created(
        self,
        survey_id: str,
        company_id: str,
        title: str,
        target_employees: int,
        **extra,
    ) -> None:
        """Publish survey.created event."""
        await self._publish(
            "survey.created",
            {
                "survey_id": survey_id,
                "company_id": company_id,
                "title": title,
                "target_employees": target_employees,
                **extra,
            },
            correlation_id=survey_id,
        )

    async def publish_survey_sent(
        self,
        survey_id: str,
        invites_sent: int,
        **extra,
    ) -> None:
        """Publish survey.sent event."""
        await self._publish(
            "survey.sent",
            {
                "survey_id": survey_id,
                "invites_sent": invites_sent,
                **extra,
            },
            correlation_id=survey_id,
        )

    async def publish_survey_closed(
        self,
        survey_id: str,
        total_responses: int,
        response_rate: float,
        avg_sentiment: Optional[float] = None,
        **extra,
    ) -> None:
        """Publish survey.closed event."""
        await self._publish(
            "survey.closed",
            {
                "survey_id": survey_id,
                "total_responses": total_responses,
                "response_rate": response_rate,
                "avg_sentiment": avg_sentiment,
                **extra,
            },
            correlation_id=survey_id,
        )

    # Conversation Events

    async def publish_conversation_started(
        self,
        conversation_id: str,
        survey_id: str,
        anonymous_id: str,
        **extra,
    ) -> None:
        """Publish conversation.started event."""
        await self._publish(
            "conversation.started",
            {
                "conversation_id": conversation_id,
                "survey_id": survey_id,
                "anonymous_id": anonymous_id,
                **extra,
            },
            correlation_id=conversation_id,
        )

    async def publish_conversation_completed(
        self,
        conversation_id: str,
        survey_id: str,
        duration_seconds: int,
        sentiment_score: Optional[float] = None,
        topics: Optional[List[str]] = None,
        **extra,
    ) -> None:
        """Publish conversation.completed event."""
        await self._publish(
            "conversation.completed",
            {
                "conversation_id": conversation_id,
                "survey_id": survey_id,
                "duration_seconds": duration_seconds,
                "sentiment_score": sentiment_score,
                "topics": topics or [],
                **extra,
            },
            correlation_id=conversation_id,
        )

    # Response Events

    async def publish_response_received(
        self,
        response_id: str,
        survey_id: str,
        sentiment_score: Optional[float] = None,
        **extra,
    ) -> None:
        """Publish response.received event."""
        await self._publish(
            "response.received",
            {
                "response_id": response_id,
                "survey_id": survey_id,
                "sentiment_score": sentiment_score,
                **extra,
            },
            correlation_id=survey_id,
        )

    # Action Events

    async def publish_action_created(
        self,
        action_id: str,
        survey_id: str,
        action_type: str,
        priority: str = "normal",
        **extra,
    ) -> None:
        """Publish action.created event."""
        await self._publish(
            "action.created",
            {
                "action_id": action_id,
                "survey_id": survey_id,
                "action_type": action_type,
                "priority": priority,
                **extra,
            },
            priority=priority,
            correlation_id=action_id,
        )

    async def publish_action_resolved(
        self,
        action_id: str,
        resolution: str,
        resolved_by: str,
        **extra,
    ) -> None:
        """Publish action.resolved event."""
        await self._publish(
            "action.resolved",
            {
                "action_id": action_id,
                "resolution": resolution,
                "resolved_by": resolved_by,
                **extra,
            },
            correlation_id=action_id,
        )

    # Alert Events

    async def publish_alert_triggered(
        self,
        alert_id: str,
        survey_id: str,
        alert_type: str,
        severity: str,
        message: str,
        **extra,
    ) -> None:
        """Publish alert.triggered event."""
        await self._publish(
            "alert.triggered",
            {
                "alert_id": alert_id,
                "survey_id": survey_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                **extra,
            },
            priority="high" if severity in ["high", "critical"] else "normal",
            correlation_id=alert_id,
        )

    # Insight Events

    async def publish_insight_generated(
        self,
        insight_id: str,
        survey_id: str,
        insight_type: str,
        summary: str,
        **extra,
    ) -> None:
        """Publish insight.generated event."""
        await self._publish(
            "insight.generated",
            {
                "insight_id": insight_id,
                "survey_id": survey_id,
                "insight_type": insight_type,
                "summary": summary,
                **extra,
            },
            correlation_id=survey_id,
        )


# Global instance
events_service = EventsService()
