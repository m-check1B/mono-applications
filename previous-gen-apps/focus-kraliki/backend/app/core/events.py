"""
Event Publishing System
Event-driven architecture for Ocelot Platform integration (RabbitMQ or In-Memory)
Includes n8n trigger integration for external orchestration (VD-239)
"""

import json
import logging
import importlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import aio_pika

logger = logging.getLogger(__name__)
from aio_pika import ExchangeType
try:
    InMemoryEventBus = importlib.import_module("events_core").InMemoryEventBus
except Exception as e:
    logger.debug(f"events_core not available, using built-in event bus: {e}")

    class _BuiltInInMemoryEventBus:
        """Lightweight in-memory bus used when events_core isn't available."""

        def __init__(self):
            self._subscribers: Dict[str, list] = {}
            self.events = []

        async def connect(self):
            return None

        async def publish(self, routing_key: str, event: Dict[str, Any]):
            self.events.append((routing_key, event))
            for pattern, handlers in self._subscribers.items():
                if self._matches(pattern, routing_key):
                    for handler in handlers:
                        await handler(routing_key, event)

        async def subscribe(self, routing_key: str, handler):
            self._subscribers.setdefault(routing_key, []).append(handler)

        @staticmethod
        def _matches(pattern: str, routing_key: str) -> bool:
            if pattern == routing_key:
                return True
            if pattern.endswith("#"):
                prefix = pattern[:-1]
                return routing_key.startswith(prefix)
            return False

    InMemoryEventBus = _BuiltInInMemoryEventBus


class EventPublisher:
    """
    Event publisher for cross-module communication in Ocelot Platform.

    Events are published to RabbitMQ topic exchange with routing keys:
    - planning.task.created
    - planning.task.completed
    - planning.project.milestone_reached
    - planning.shadow.insight_generated

    Other modules can subscribe to these events for automation and integration.
    """

    def __init__(self, amqp_url: str = "amqp://localhost:5672"):
        """
        Initialize RabbitMQ event publisher.

        Args:
            amqp_url: RabbitMQ connection URL
        """
        self.amqp_url = amqp_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self._mem_bus = None

    async def connect(self):
        """Establish connection to RabbitMQ or In-Memory bus."""
        from app.core.config import settings
        if getattr(settings, "USE_INMEMORY_EVENTS", False) and InMemoryEventBus is not None:
            self._mem_bus = InMemoryEventBus()
            await self._mem_bus.connect()
            return
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()

            # Declare topic exchange for planning module events
            self.exchange = await self.channel.declare_exchange(
                "ocelot.planning",
                ExchangeType.TOPIC,
                durable=True
            )

    async def disconnect(self):
        """Close RabbitMQ connection."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        workspace_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Publish event to platform event bus.

        Args:
            event_type: Event type (e.g., 'task.created', 'task.completed')
            data: Event payload data
            organization_id: Organization ID for multi-tenancy
            user_id: Optional user ID who triggered the event
            metadata: Optional additional metadata

        Example:
            await event_publisher.publish(
                event_type="task.created",
                data={
                    "task_id": "abc123",
                    "title": "Fix bug",
                    "priority": "high"
                },
                organization_id="org_xyz",
                user_id="user_123"
            )
        """
        # Ensure connection
        if self._mem_bus is None and (not self.connection or self.connection.is_closed):
            await self.connect()

        # Build event envelope
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "source": "planning",  # Module identifier
            "timestamp": datetime.utcnow().isoformat(),
            "organizationId": organization_id,
            "userId": user_id,
            "data": data,
            "metadata": metadata or {
                "version": "1.0.0",
                "module": "focus-kraliki"
            }
        }

        # Publish to RabbitMQ/In-Memory
        if self._mem_bus is not None:
            await self._mem_bus.publish(f"planning.{event_type}", event)
        else:
            routing_key = f"planning.{event_type}"
            message = aio_pika.Message(
                body=json.dumps(event).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            if self.exchange:
                await self.exchange.publish(
                    message,
                    routing_key=routing_key
                )

        # Bridge to local EventBus for WebSockets (Gap #7)
        try:
            from app.core.event_bus import get_event_bus
            eb = get_event_bus()
            # Use event_type (e.g. 'task.created') directly or mapped
            # websocket.py subscribes to 'task_update', etc.
            # We'll map 'task.created' to 'task_update' for consistency if needed,
            # but let's just publish the raw type too.
            await eb.publish(event_type, data, user_id=user_id)
            if "." in event_type:
                # Also publish with underscore for websocket.py compatibility if needed
                await eb.publish(event_type.replace(".", "_"), data, user_id=user_id)
        except Exception as e:
            logger.warning(f"Failed to bridge event to local EventBus: {e}")

        # Dispatch to n8n if configured as global orchestration
        from app.services.n8n_client import get_n8n_client
        from app.core.config import settings
        
        if settings.N8N_URL or (workspace_settings and workspace_settings.get("n8n_url")):
            try:
                n8n = get_n8n_client(workspace_settings)
                await n8n.dispatch_event(event)
                logger.debug(f"Event {event_type} dispatched to n8n")
            except Exception as e:
                logger.warning(f"Failed to dispatch event to n8n: {e}")

    async def subscribe(self, routing_key: str, handler):
        """
        Subscribe to events (in-memory backend only).

        Args:
            routing_key: Event routing key (e.g., 'planning.task.created')
            handler: Async function (event_type: str, data: dict) -> None
        """
        if self._mem_bus is not None:
            await self._mem_bus.subscribe(routing_key, handler)
        else:
            # RabbitMQ subscription is handled by platform; module subscribes via platform bus
            pass

    async def publish_task_created(
        self,
        task_id: str,
        title: str,
        priority: str,
        organization_id: str,
        user_id: str,
        assignee_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Publish task.created event.

        Triggers:
        - Agents module: Suggest workflow automation
        - Notifications: Notify assignee
        - Analytics: Track task creation metrics
        """
        await self.publish(
            event_type="task.created",
            data={
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "assignee_id": assignee_id,
                "project_id": project_id
            },
            organization_id=organization_id,
            user_id=user_id,
            workspace_settings=workspace_settings
        )

    async def publish_task_completed(
        self,
        task_id: str,
        title: str,
        organization_id: str,
        user_id: str,
        duration_minutes: Optional[int] = None,
        workspace_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Publish task.completed event.

        Triggers:
        - Campaigns: Send follow-up campaign
        - Analytics: Track completion metrics
        - Achievements: Award badges/points
        """
        await self.publish(
            event_type="task.completed",
            data={
                "task_id": task_id,
                "title": title,
                "duration_minutes": duration_minutes
            },
            organization_id=organization_id,
            user_id=user_id,
            workspace_settings=workspace_settings
        )

    async def publish_task_updated(
        self,
        task_id: str,
        title: str,
        organization_id: str,
        user_id: str,
        updates: Dict[str, Any],
        workspace_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Publish task.updated event.
        """
        await self.publish(
            event_type="task.updated",
            data={
                "task_id": task_id,
                "title": title,
                "updates": updates
            },
            organization_id=organization_id,
            user_id=user_id,
            workspace_settings=workspace_settings
        )

    async def publish_project_milestone(
        self,
        project_id: str,
        milestone_name: str,
        organization_id: str,
        user_id: str,
        completion_percentage: int
    ):
        """
        Publish project.milestone_reached event.

        Triggers:
        - Notifications: Notify team members
        - Reports: Generate progress report
        """
        await self.publish(
            event_type="project.milestone_reached",
            data={
                "project_id": project_id,
                "milestone_name": milestone_name,
                "completion_percentage": completion_percentage
            },
            organization_id=organization_id,
            user_id=user_id
        )

    async def publish_shadow_insight(
        self,
        insight_id: str,
        insight_type: str,
        insight_text: str,
        organization_id: str,
        user_id: str,
        task_id: Optional[str] = None
    ):
        """
        Publish shadow.insight_generated event.

        Triggers:
        - Flow Memory: Store insight for cross-session context
        - Analytics: Track AI insights
        """
        await self.publish(
            event_type="shadow.insight_generated",
            data={
                "insight_id": insight_id,
                "insight_type": insight_type,
                "insight_text": insight_text,
                "task_id": task_id
            },
            organization_id=organization_id,
            user_id=user_id
        )


# Global instance (initialize in main.py startup)
event_publisher = EventPublisher()
