"""Provider Failover Service

Manages mid-call provider switching with context preservation:
- Seamless provider switching during active calls
- Conversation context preservation
- Automatic failover on provider health issues
- Switch status tracking and monitoring
"""

import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProviderSwitchContext(BaseModel):
    """Context saved during provider switch."""
    messages: list = []
    sentiment: str | None = None
    insights: dict = {}
    metadata: dict = {}


class ProviderSwitchStatus(BaseModel):
    """Status of an in-progress provider switch."""
    session_id: UUID
    from_provider: str
    to_provider: str
    started_at: datetime
    reason: str
    status: str = "in_progress"  # in_progress, completed, failed


class ProviderSwitchResult(BaseModel):
    """Result of a provider switch operation."""
    success: bool
    session_id: UUID
    from_provider: str
    to_provider: str
    context_preserved: int
    switched_at: datetime
    error_message: str | None = None


class ProviderFailoverService:
    """Service for managing provider failover and switching.

    Handles seamless provider switching during active calls while
    preserving conversation context and state.
    """

    def __init__(self):
        """Initialize provider failover service."""
        self.switching_sessions: dict[UUID, ProviderSwitchStatus] = {}
        self._switch_history: dict[UUID, list[ProviderSwitchResult]] = {}

    async def switch_provider(
        self,
        session_id: UUID,
        from_provider: str,
        to_provider: str,
        reason: str = "manual"
    ) -> ProviderSwitchResult:
        """Execute provider switch for active session.

        Args:
            session_id: Session identifier
            from_provider: Current provider ID
            to_provider: Target provider ID
            reason: Reason for switch (manual, auto_failover, etc.)

        Returns:
            ProviderSwitchResult with switch details

        Raises:
            ValueError: If session not found
            RuntimeError: If switch fails
        """
        try:
            # Mark switch in progress
            self.switching_sessions[session_id] = ProviderSwitchStatus(
                session_id=session_id,
                from_provider=from_provider,
                to_provider=to_provider,
                started_at=datetime.now(UTC),
                reason=reason,
                status="in_progress"
            )

            # Get current session
            from app.sessions.manager import get_session_manager
            session_manager = get_session_manager()
            session = await session_manager.get_session(session_id)

            if not session:
                raise ValueError(f"Session {session_id} not found")

            logger.info(
                f"Starting provider switch for session {session_id}: "
                f"{from_provider} -> {to_provider} (reason: {reason})"
            )

            # Save conversation context
            context = await self._save_context(session)

            # Pause current provider (gracefully)
            await self._pause_provider(session, from_provider)

            # Initialize new provider
            await self._initialize_provider(session, to_provider)

            # Restore conversation context
            await self._restore_context(session, context)

            # Update session metadata
            if not hasattr(session, 'metadata') or session.metadata is None:
                session.metadata = {}

            if "provider_switches" not in session.metadata:
                session.metadata["provider_switches"] = []

            session.metadata["provider_switches"].append({
                "from": from_provider,
                "to": to_provider,
                "timestamp": datetime.now(UTC).isoformat(),
                "reason": reason
            })

            # Update session provider
            session.provider_type = to_provider
            session.updated_at = datetime.now(UTC)

            # Mark switch complete
            if session_id in self.switching_sessions:
                self.switching_sessions[session_id].status = "completed"

            result = ProviderSwitchResult(
                success=True,
                session_id=session_id,
                from_provider=from_provider,
                to_provider=to_provider,
                context_preserved=len(context.messages),
                switched_at=datetime.now(UTC)
            )

            # Store in history
            if session_id not in self._switch_history:
                self._switch_history[session_id] = []
            self._switch_history[session_id].append(result)

            logger.info(
                f"Provider switch completed for session {session_id}: "
                f"{from_provider} -> {to_provider}"
            )

            # Remove from switching list after short delay
            await asyncio.sleep(1.0)
            if session_id in self.switching_sessions:
                del self.switching_sessions[session_id]

            return result

        except Exception as e:
            logger.error(f"Provider switch failed for session {session_id}: {e}")

            # Mark switch failed
            if session_id in self.switching_sessions:
                self.switching_sessions[session_id].status = "failed"

            # Create failure result
            result = ProviderSwitchResult(
                success=False,
                session_id=session_id,
                from_provider=from_provider,
                to_provider=to_provider,
                context_preserved=0,
                switched_at=datetime.now(UTC),
                error_message=str(e)
            )

            # Store in history
            if session_id not in self._switch_history:
                self._switch_history[session_id] = []
            self._switch_history[session_id].append(result)

            # Cleanup
            if session_id in self.switching_sessions:
                del self.switching_sessions[session_id]

            raise RuntimeError(f"Provider switch failed: {e}") from e

    async def _save_context(self, session) -> ProviderSwitchContext:
        """Save conversation context before switch.

        Args:
            session: Session object

        Returns:
            ProviderSwitchContext with saved state
        """
        context = ProviderSwitchContext(
            messages=getattr(session, "messages", []),
            sentiment=getattr(session, "sentiment", None),
            insights=getattr(session, "ai_insights", {}),
            metadata=dict(session.metadata) if hasattr(session, "metadata") else {}
        )

        logger.debug(
            f"Saved context for session {session.id}: "
            f"{len(context.messages)} messages"
        )

        return context

    async def _restore_context(self, session, context: ProviderSwitchContext):
        """Restore conversation context after switch.

        Args:
            session: Session object
            context: ProviderSwitchContext to restore
        """
        if context.messages:
            session.messages = context.messages
        if context.sentiment:
            session.sentiment = context.sentiment
        if context.insights:
            session.ai_insights = context.insights

        logger.debug(
            f"Restored context for session {session.id}: "
            f"{len(context.messages)} messages"
        )

    async def _pause_provider(self, session, provider: str):
        """Gracefully pause current provider.

        Args:
            session: Session object
            provider: Provider ID to pause
        """
        try:
            # Get provider instance from session manager
            from app.sessions.manager import get_session_manager
            session_manager = get_session_manager()
            provider_instance = session_manager.get_provider(session.id)

            if provider_instance:
                # Send pause/disconnect signal
                # In production, this would gracefully close connections
                logger.debug(f"Pausing provider {provider} for session {session.id}")

            # Brief pause for cleanup
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.warning(f"Error pausing provider {provider}: {e}")

    async def _initialize_provider(self, session, provider: str):
        """Initialize new provider.

        Args:
            session: Session object
            provider: Provider ID to initialize
        """
        try:
            # In production, this would:
            # 1. Create new provider connection
            # 2. Warm up with minimal context
            # 3. Prepare for audio/message streaming

            logger.debug(f"Initializing provider {provider} for session {session.id}")

            # Brief initialization delay
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.warning(f"Error initializing provider {provider}: {e}")

    def get_switch_status(self, session_id: UUID) -> ProviderSwitchStatus | None:
        """Check if switch is in progress for session.

        Args:
            session_id: Session identifier

        Returns:
            ProviderSwitchStatus if switch in progress, None otherwise
        """
        return self.switching_sessions.get(session_id)

    def get_switch_history(self, session_id: UUID) -> list[ProviderSwitchResult]:
        """Get provider switch history for session.

        Args:
            session_id: Session identifier

        Returns:
            List of ProviderSwitchResult
        """
        return self._switch_history.get(session_id, [])

    async def auto_failover_if_needed(self, session_id: UUID) -> ProviderSwitchResult | None:
        """Automatically switch if current provider is unhealthy.

        Args:
            session_id: Session identifier

        Returns:
            ProviderSwitchResult if failover occurred, None otherwise
        """
        try:
            from app.services.provider_health_monitor import get_health_monitor
            from app.sessions.manager import get_session_manager

            session_manager = get_session_manager()
            session = await session_manager.get_session(session_id)

            if not session:
                logger.warning(f"Session {session_id} not found for auto-failover")
                return None

            current_provider = session.provider_type
            health_monitor = get_health_monitor()
            health = health_monitor.get_provider_health(current_provider)

            # Check if failover needed
            if health and health.status in ["unhealthy", "offline"]:
                logger.warning(
                    f"Provider {current_provider} is {health.status}, "
                    f"triggering auto-failover for session {session_id}"
                )

                # Find healthy alternative
                healthy_providers = health_monitor.get_healthy_providers()

                # Exclude current provider
                alternatives = [p for p in healthy_providers if p != current_provider]

                if alternatives:
                    best_provider = alternatives[0]
                    logger.info(
                        f"Auto-failover switching to {best_provider} "
                        f"for session {session_id}"
                    )

                    result = await self.switch_provider(
                        session_id,
                        current_provider,
                        best_provider,
                        reason="auto_failover"
                    )

                    return result
                else:
                    logger.error(
                        f"No healthy providers available for auto-failover "
                        f"of session {session_id}"
                    )

            return None

        except Exception as e:
            logger.error(f"Auto-failover failed for session {session_id}: {e}")
            return None


# Singleton instance
_failover_service: ProviderFailoverService | None = None


def get_failover_service() -> ProviderFailoverService:
    """Get singleton failover service instance.

    Returns:
        ProviderFailoverService instance
    """
    global _failover_service
    if _failover_service is None:
        _failover_service = ProviderFailoverService()
    return _failover_service
