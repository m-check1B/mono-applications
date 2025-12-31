"""Session manager for orchestrating AI provider sessions.

Handles session lifecycle, provider instantiation, and coordination.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.config.settings import get_settings
from app.database import SessionLocal
from app.providers.base import SessionConfig
from app.providers.registry import (
    ProviderType,
    TelephonyType,
    get_provider_registry,
)
from app.services.usage_service import usage_service
from app.sessions.models import Session, SessionCreateRequest, SessionStatus

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages active sessions and provider instances.

    This is a singleton that coordinates between FastAPI endpoints,
    WebSocket connections, and AI provider instances.
    """

    def __init__(self):
        """Initialize session manager."""
        self._sessions: dict[UUID, Session] = {}  # Memory cache
        self._providers: dict[UUID, Any] = {}  # UUID -> Provider instance
        self.settings = get_settings()
        self.registry = get_provider_registry()
        self._persistent_storage = None

    async def _get_persistent_storage(self):
        """Get persistent storage instance."""
        if self._persistent_storage is None:
            try:
                # Import here to avoid circular imports
                import os
                import sys

                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from app.sessions.storage import get_persistent_storage

                self._persistent_storage = await get_persistent_storage()
            except Exception as e:
                logger.warning(f"Persistent storage not available: {e}")
                self._persistent_storage = None
        return self._persistent_storage

    async def create_session(self, request: SessionCreateRequest) -> Session:
        """Create a new session and initialize provider.

        Args:
            request: Session creation request

        Returns:
            Session: Created session entity

        Raises:
            ValueError: If provider type is not supported
        """
        # Create session entity
        provider_type_value = request.resolved_provider_type()

        try:
            provider_enum = ProviderType(provider_type_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported provider '{provider_type_value}'") from exc

        # Determine model to use
        provider_model = self._resolve_model(provider_enum, request)

        # Determine execution strategy
        strategy = request.strategy or (
            "segmented" if provider_enum == ProviderType.DEEPGRAM else "realtime"
        )

        # Determine telephony provider if requested
        telephony_value = request.resolved_telephony()
        telephony_provider = None
        if telephony_value:
            try:
                telephony_enum = TelephonyType(telephony_value)
            except ValueError as exc:
                raise ValueError(f"Unsupported telephony provider '{telephony_value}'") from exc

            telephony_info = self.registry.get_telephony_info(telephony_enum)
            if not telephony_info or not telephony_info.is_configured:
                raise ValueError(f"Telephony provider '{telephony_enum.value}' is not configured")
            telephony_provider = telephony_enum.value
        else:
            primary_adapter = next(
                (
                    info
                    for info in self.registry.list_telephony_adapters()
                    if info.is_primary and info.is_configured
                ),
                None,
            )
            if primary_adapter:
                telephony_provider = primary_adapter.id

        metadata = dict(request.metadata or {})
        metadata["strategy"] = strategy
        if telephony_provider:
            metadata["telephony_provider"] = telephony_provider
        if request.phone_number:
            metadata.setdefault("phone_number", request.phone_number)
        if request.campaign:
            metadata.setdefault("campaign", request.campaign)
        if request.persona:
            metadata.setdefault("persona", request.persona)

        session = Session(
            provider_type=provider_enum.value,
            provider_model=provider_model,
            strategy=strategy,
            telephony_provider=telephony_provider,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            metadata=metadata,
            status=SessionStatus.PENDING,
        )

        now = datetime.now(UTC)
        session.created_at = now
        session.updated_at = now

        # Store session in persistent storage (if available)
        try:
            persistent_storage = await self._get_persistent_storage()
            if persistent_storage:
                await persistent_storage.create_session(session)
        except Exception as e:
            logger.warning(f"Failed to store session {session.id} persistently: {e}")

        # Always cache in memory for fast access
        self._sessions[session.id] = session

        logger.info(
            "Created session %s with provider %s",
            session.id,
            provider_enum.value,
        )

        return session

    async def start_session(self, session_id: UUID) -> None:
        """Start a session by connecting to the provider.

        Args:
            session_id: Session identifier

        Raises:
            ValueError: If session not found
            ConnectionError: If provider connection fails
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            # Instantiate provider
            provider = self._create_provider(session)

            # Create provider config
            config = SessionConfig(
                model_id=session.provider_model,
                system_prompt=session.system_prompt,
                temperature=session.temperature,
                metadata=session.metadata,
            )

            # Connect provider
            await provider.connect(config)

            # Store provider instance
            self._providers[session_id] = provider

            # Update session status
            session.status = SessionStatus.ACTIVE
            session.started_at = datetime.now(UTC)
            session.updated_at = session.started_at

            logger.info(f"Started session {session_id}")

        except Exception as e:
            session.status = SessionStatus.ERROR
            session.updated_at = datetime.now(UTC)
            logger.error(f"Failed to start session {session_id}: {e}")
            raise

    async def end_session(self, session_id: UUID) -> None:
        """End a session and cleanup resources.

        Args:
            session_id: Session identifier
        """
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"Attempted to end non-existent session {session_id}")
            return

        if session.status in (SessionStatus.COMPLETED, SessionStatus.TERMINATED):
            logger.debug(f"Session {session_id} already ended")
            return

        # Disconnect provider
        provider = self._providers.get(session_id)
        if provider:
            try:
                await provider.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting provider for session {session_id}: {e}")
            finally:
                del self._providers[session_id]

        # Update session status
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.now(UTC)
        session.updated_at = session.ended_at

        # Record usage if duration is available
        if session.started_at and session.ended_at:
            duration = int((session.ended_at - session.started_at).total_seconds())

            # Find user_id/company_id from metadata
            user_id = session.metadata.get("user_id") or session.metadata.get("company_id")

            if user_id:
                try:
                    # Sync DB session
                    with SessionLocal() as db:
                        # Record standard voice minutes (aggregated for all providers)
                        usage_service.record_usage(
                            db=db,
                            user_id=str(user_id),
                            quantity=duration,
                            service_type="voice_minutes",
                            reference_id=str(session.id),
                        )

                        # Record provider-specific usage for granular tracking
                        if session.provider_type == "gemini":
                            usage_service.record_usage(
                                db=db,
                                user_id=str(user_id),
                                quantity=duration,
                                service_type="voice_gemini",
                                reference_id=str(session.id),
                            )
                        elif session.provider_type == "openai":
                            usage_service.record_usage(
                                db=db,
                                user_id=str(user_id),
                                quantity=duration,
                                service_type="voice_openai",
                                reference_id=str(session.id),
                            )

                        logger.info(f"Recorded usage for session {session.id}: {duration}s (provider: {session.provider_type})")
                except Exception as e:
                    logger.error(f"Failed to record usage for session {session.id}: {e}")

        # Update in persistent storage
        try:
            persistent_storage = await self._get_persistent_storage()
            if persistent_storage:
                await persistent_storage.update_session(session)
        except Exception as e:
            logger.warning(f"Failed to update session {session_id} in persistent storage: {e}")

        logger.info(f"Ended session {session_id}")

    async def get_session(self, session_id: UUID) -> Session | None:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session or None if not found
        """
        # Check memory cache first
        session = self._sessions.get(session_id)
        if session:
            return session

        # Try persistent storage
        try:
            persistent_storage = await self._get_persistent_storage()
            if persistent_storage:
                session = await persistent_storage.get_session(session_id)
                if session:
                    # Cache in memory for faster access
                    self._sessions[session_id] = session
                    return session
        except Exception as e:
            logger.warning(f"Failed to get session {session_id} from persistent storage: {e}")

        return None

    def get_provider(self, session_id: UUID) -> Any | None:
        """Get provider instance for session.

        Args:
            session_id: Session identifier

        Returns:
            Provider instance or None
        """
        return self._providers.get(session_id)

    async def list_sessions(self, status: SessionStatus | None = None) -> list[Session]:
        """List all sessions, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of sessions
        """
        all_sessions = []

        # Get sessions from persistent storage
        try:
            persistent_storage = await self._get_persistent_storage()
            if persistent_storage:
                persistent_sessions = await persistent_storage.list_sessions(status)
                all_sessions.extend(persistent_sessions)
        except Exception as e:
            logger.warning(f"Failed to list sessions from persistent storage: {e}")

        # Add memory-only sessions
        memory_sessions = list(self._sessions.values())
        if status:
            memory_sessions = [s for s in memory_sessions if s.status == status]

        # Combine without duplicates
        for session in memory_sessions:
            if not any(s.id == session.id for s in all_sessions):
                all_sessions.append(session)

        return all_sessions

    def _create_provider(self, session: Session) -> Any:
        """Create provider instance based on session configuration.

        Args:
            session: Session entity

        Returns:
            Provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        try:
            provider_enum = ProviderType(session.provider_type)
        except ValueError as exc:
            raise ValueError(f"Unsupported provider type: {session.provider_type}") from exc

        return self.registry.create_provider(
            provider_enum,
            model=session.provider_model,
        )

    def _get_default_model(self, provider_type: str) -> str:
        """Get default model for provider type.

        Args:
            provider_type: Provider type

        Returns:
            Default model ID
        """
        defaults = {
            "openai": "gpt-4o-mini-realtime-preview",
            "gemini": "gemini-2.5-flash",
            "deepgram": "nova-2",
        }
        return defaults.get(provider_type.lower(), "unknown")

    def _resolve_model(self, provider: ProviderType, request: SessionCreateRequest) -> str:
        """Resolve model identifier from request with registry defaults."""

        preferred_model = request.provider_model
        use_premium = request.wants_premium()

        provider_info = self.registry.get_provider_info(provider)
        if not provider_info or not provider_info.available_models:
            raise ValueError(f"Provider '{provider.value}' has no configured models")

        if preferred_model and preferred_model in provider_info.available_models:
            return preferred_model

        if use_premium:
            # Choose the last (assumed premium) model with non-mini naming
            for model_id in reversed(provider_info.available_models):
                if "mini" not in model_id and "lite" not in model_id:
                    return model_id

        # Default to first model in list
        return provider_info.available_models[0]


# Global singleton instance
_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance.

    Returns:
        SessionManager: Global session manager
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
