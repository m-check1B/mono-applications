"""
Context sharing service for browser and voice channel integration
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ChannelType(str, Enum):
    BROWSER = "browser"
    VOICE = "voice"

class ContextEventType(str, Enum):
    SESSION_STARTED = "session_started"
    MESSAGE_SENT = "message_sent"
    INTENT_DETECTED = "intent_detected"
    SENTIMENT_ANALYZED = "sentiment_analyzed"
    PROVIDER_SWITCHED = "provider_switched"
    CUSTOMER_INFO_UPDATED = "customer_info_updated"
    WORKFLOW_TRIGGERED = "workflow_triggered"
    SESSION_ENDED = "session_ended"

class ContextEvent:
    def __init__(
        self,
        event_type: ContextEventType,
        channel: ChannelType,
        session_id: str,
        data: dict[str, Any],
        timestamp: datetime | None = None
    ):
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.channel = channel
        self.session_id = session_id
        self.data = data
        self.timestamp = timestamp or datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "channel": self.channel,
            "session_id": self.session_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

class SharedContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.browser_session_id: str | None = None
        self.voice_session_id: str | None = None
        self.customer_info: dict[str, Any] = {}
        self.conversation_summary: list[dict[str, Any]] = []
        self.intents: list[dict[str, Any]] = []
        self.sentiments: list[dict[str, Any]] = []
        self.provider_history: list[dict[str, Any]] = []
        self.workflows: list[dict[str, Any]] = []
        self.events: list[ContextEvent] = []
        self.created_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)

    def add_event(self, event: ContextEvent):
        """Add an event to the context"""
        self.events.append(event)
        self.last_activity = datetime.now(UTC)

        # Update specific context based on event type
        if event.event_type == ContextEventType.MESSAGE_SENT:
            self.conversation_summary.append({
                "channel": event.channel,
                "role": event.data.get("role", "user"),
                "content": event.data.get("content", ""),
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.data.get("metadata", {})
            })

        elif event.event_type == ContextEventType.INTENT_DETECTED:
            self.intents.append({
                "intent": event.data.get("intent"),
                "confidence": event.data.get("confidence"),
                "provider": event.data.get("provider"),
                "timestamp": event.timestamp.isoformat()
            })

        elif event.event_type == ContextEventType.SENTIMENT_ANALYZED:
            self.sentiments.append({
                "sentiment": event.data.get("sentiment"),
                "confidence": event.data.get("confidence"),
                "emotion": event.data.get("emotion"),
                "provider": event.data.get("provider"),
                "timestamp": event.timestamp.isoformat()
            })

        elif event.event_type == ContextEventType.PROVIDER_SWITCHED:
            self.provider_history.append({
                "from_provider": event.data.get("from_provider"),
                "to_provider": event.data.get("to_provider"),
                "reason": event.data.get("reason"),
                "timestamp": event.timestamp.isoformat()
            })

        elif event.event_type == ContextEventType.WORKFLOW_TRIGGERED:
            self.workflows.append({
                "workflow_id": event.data.get("workflow_id"),
                "action": event.data.get("action"),
                "status": event.data.get("status"),
                "timestamp": event.timestamp.isoformat()
            })

        elif event.event_type == ContextEventType.CUSTOMER_INFO_UPDATED:
            self.customer_info.update(event.data.get("customer_info", {}))

    def get_recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent events"""
        return [event.to_dict() for event in sorted(self.events, key=lambda x: x.timestamp, reverse=True)[:limit]]

    def get_conversation_history(self, channel: ChannelType | None = None) -> list[dict[str, Any]]:
        """Get conversation history, optionally filtered by channel"""
        if channel:
            return [msg for msg in self.conversation_summary if msg["channel"] == channel]
        return self.conversation_summary

    def get_current_intent(self) -> dict[str, Any] | None:
        """Get the most recent intent"""
        if self.intents:
            return max(self.intents, key=lambda x: x["timestamp"])
        return None

    def get_current_sentiment(self) -> dict[str, Any] | None:
        """Get the most recent sentiment"""
        if self.sentiments:
            return max(self.sentiments, key=lambda x: x["timestamp"])
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "session_id": self.session_id,
            "browser_session_id": self.browser_session_id,
            "voice_session_id": self.voice_session_id,
            "customer_info": self.customer_info,
            "conversation_summary": self.conversation_summary,
            "intents": self.intents,
            "sentiments": self.sentiments,
            "provider_history": self.provider_history,
            "workflows": self.workflows,
            "events": [event.to_dict() for event in self.events],
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

class ContextSharingService:
    def __init__(self):
        self.contexts: dict[str, SharedContext] = {}  # session_id -> SharedContext
        self.channel_mappings: dict[str, str] = {}  # channel_session_id -> shared_session_id

    def create_shared_context(
        self,
        session_id: str,
        channel: ChannelType,
        channel_session_id: str,
        customer_info: dict[str, Any] | None = None
    ) -> SharedContext:
        """Create a new shared context"""
        context = SharedContext(session_id)

        if channel == ChannelType.BROWSER:
            context.browser_session_id = channel_session_id
        else:
            context.voice_session_id = channel_session_id

        if customer_info:
            context.customer_info = customer_info

        self.contexts[session_id] = context
        self.channel_mappings[channel_session_id] = session_id

        # Add session started event
        context.add_event(ContextEvent(
            event_type=ContextEventType.SESSION_STARTED,
            channel=channel,
            session_id=session_id,
            data={"channel_session_id": channel_session_id}
        ))

        return context

    def link_channels(
        self,
        shared_session_id: str,
        channel: ChannelType,
        channel_session_id: str
    ) -> SharedContext | None:
        """Link a channel session to an existing shared context"""
        if shared_session_id not in self.contexts:
            return None

        context = self.contexts[shared_session_id]

        if channel == ChannelType.BROWSER:
            context.browser_session_id = channel_session_id
        else:
            context.voice_session_id = channel_session_id

        self.channel_mappings[channel_session_id] = shared_session_id

        return context

    def get_context_by_channel(self, channel_session_id: str) -> SharedContext | None:
        """Get shared context by channel session ID"""
        shared_session_id = self.channel_mappings.get(channel_session_id)
        if shared_session_id:
            return self.contexts.get(shared_session_id)
        return None

    def get_context(self, session_id: str) -> SharedContext | None:
        """Get shared context by session ID"""
        return self.contexts.get(session_id)

    def add_event(self, channel_session_id: str, event: ContextEvent) -> bool:
        """Add an event to the shared context"""
        context = self.get_context_by_channel(channel_session_id)
        if context:
            context.add_event(event)
            return True
        return False

    def update_customer_info(
        self,
        channel_session_id: str,
        customer_info: dict[str, Any]
    ) -> bool:
        """Update customer information in the shared context"""
        context = self.get_context_by_channel(channel_session_id)
        if context:
            context.customer_info.update(customer_info)
            context.add_event(ContextEvent(
                event_type=ContextEventType.CUSTOMER_INFO_UPDATED,
                channel=ChannelType.BROWSER,  # Default to browser, can be overridden
                session_id=context.session_id,
                data={"customer_info": customer_info}
            ))
            return True
        return False

    def get_hydration_data(self, channel_session_id: str) -> dict[str, Any] | None:
        """Get data for hydrating a reconnected channel"""
        context = self.get_context_by_channel(channel_session_id)
        if not context:
            return None

        return {
            "shared_session_id": context.session_id,
            "customer_info": context.customer_info,
            "conversation_summary": context.get_conversation_history(),
            "current_intent": context.get_current_intent(),
            "current_sentiment": context.get_current_sentiment(),
            "provider_history": context.provider_history,
            "workflows": context.workflows,
            "last_activity": context.last_activity.isoformat()
        }

    def switch_provider(
        self,
        channel_session_id: str,
        from_provider: str,
        to_provider: str,
        reason: str = "manual"
    ) -> bool:
        """Record a provider switch in the shared context"""
        context = self.get_context_by_channel(channel_session_id)
        if context:
            context.add_event(ContextEvent(
                event_type=ContextEventType.PROVIDER_SWITCHED,
                channel=ChannelType.VOICE,  # Provider switches typically happen in voice
                session_id=context.session_id,
                data={
                    "from_provider": from_provider,
                    "to_provider": to_provider,
                    "reason": reason
                }
            ))
            return True
        return False

    def trigger_workflow(
        self,
        channel_session_id: str,
        workflow_id: str,
        action: str,
        status: str = "triggered"
    ) -> bool:
        """Record a workflow trigger in the shared context"""
        context = self.get_context_by_channel(channel_session_id)
        if context:
            context.add_event(ContextEvent(
                event_type=ContextEventType.WORKFLOW_TRIGGERED,
                channel=ChannelType.BROWSER,  # Workflows typically triggered from browser
                session_id=context.session_id,
                data={
                    "workflow_id": workflow_id,
                    "action": action,
                    "status": status
                }
            ))
            return True
        return False

    def end_session(self, channel_session_id: str) -> bool:
        """End a session in the shared context"""
        context = self.get_context_by_channel(channel_session_id)
        if context:
            context.add_event(ContextEvent(
                event_type=ContextEventType.SESSION_ENDED,
                channel=ChannelType.BROWSER,  # Can be either channel
                session_id=context.session_id,
                data={"channel_session_id": channel_session_id}
            ))
            return True
        return False

    def cleanup_old_contexts(self, max_age_hours: int = 24) -> int:
        """Clean up old contexts"""
        cutoff_time = datetime.now(UTC).timestamp() - (max_age_hours * 3600)
        old_contexts = [
            session_id for session_id, context in self.contexts.items()
            if context.last_activity.timestamp() < cutoff_time
        ]

        for session_id in old_contexts:
            context = self.contexts[session_id]
            # Clean up channel mappings
            if context.browser_session_id:
                self.channel_mappings.pop(context.browser_session_id, None)
            if context.voice_session_id:
                self.channel_mappings.pop(context.voice_session_id, None)
            # Remove context
            del self.contexts[session_id]

        return len(old_contexts)

    async def share_context(
        self,
        context_data: dict[str, Any],
        target_users: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Share context with target users.
        This is a higher-level method for AI-powered context sharing.
        """
        session_id = context_data.get("session_id", str(uuid.uuid4()))

        # If it doesn't exist, create it
        if session_id not in self.contexts:
            context = SharedContext(session_id)
            self.contexts[session_id] = context
        else:
            context = self.contexts[session_id]

        # Update context with data
        if "customer_info" in context_data:
            context.customer_info.update(context_data["customer_info"])

        # Add event
        context.add_event(ContextEvent(
            event_type=ContextEventType.CUSTOMER_INFO_UPDATED,
            channel=ChannelType.BROWSER,
            session_id=session_id,
            data={"shared_with": target_users, "context_data": context_data}
        ))

        return {
            "session_id": session_id,
            "shared_with": target_users,
            "status": "success",
            "timestamp": datetime.now(UTC).isoformat()
        }

# Global instance
context_sharing_service = ContextSharingService()
