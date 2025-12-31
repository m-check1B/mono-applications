"""Persistent call state manager with Redis caching and database persistence.

This module provides a robust call state management system that:
- Uses Redis for fast in-memory lookups of active calls
- Persists all call data to the database for durability
- Provides automatic recovery of active calls after server restarts
- Maintains backwards compatibility with the original in-memory API
"""

import logging
from datetime import UTC
from uuid import UUID

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.database import SessionLocal
from app.models.call_state import CallState, CallStatus

logger = logging.getLogger(__name__)


class PersistentCallStateManager:
    """Manages call state with Redis cache and database persistence.

    This manager provides a two-tier storage approach:
    1. Redis for fast lookups of active calls (optional, falls back to DB)
    2. PostgreSQL/SQLite for persistent storage and call history

    The Redis cache is used for performance but is not required. All data
    is always persisted to the database, ensuring durability even if Redis
    is unavailable or cleared.
    """

    def __init__(self):
        """Initialize the call state manager.

        Attempts to connect to Redis if configured, but continues without it
        if Redis is unavailable (graceful degradation).
        """
        self.settings = get_settings()
        self.redis_client = None
        self.redis_prefix = "call_state:"

        # Try to connect to Redis, but don't fail if it's unavailable
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                password=self.settings.redis_password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connected for call state caching")
        except Exception as exc:
            logger.warning("Redis not available for call state caching, using DB only: %s", exc)
            self.redis_client = None

    def _get_db(self) -> Session:
        """Get a database session."""
        return SessionLocal()

    def register_call(
        self,
        call_id: str,
        session_id: UUID,
        provider: str = "unknown",
        direction: str = "inbound",
        from_number: str | None = None,
        to_number: str | None = None,
        metadata: dict | None = None
    ) -> CallState:
        """Register a new call state in both Redis and database.

        Args:
            call_id: Telephony provider's call identifier (e.g., Twilio CallSid)
            session_id: Internal session UUID
            provider: Telephony provider name (twilio, telnyx)
            direction: Call direction (inbound/outbound)
            from_number: Calling party phone number
            to_number: Called party phone number
            metadata: Additional call metadata

        Returns:
            CallState: The created call state record
        """
        db = self._get_db()
        try:
            # Convert UUID to string for storage
            session_id_str = str(session_id)

            # Create database record
            call_state = CallState(
                call_id=call_id,
                session_id=session_id_str,
                provider=provider,
                direction=direction,
                status=CallStatus.INITIATED,
                from_number=from_number,
                to_number=to_number,
                call_metadata=metadata or {}
            )
            db.add(call_state)
            db.commit()
            db.refresh(call_state)

            # Cache in Redis for fast lookups (if available)
            if self.redis_client:
                try:
                    self.redis_client.hset(
                        f"{self.redis_prefix}call_to_session",
                        call_id,
                        session_id_str
                    )
                    self.redis_client.hset(
                        f"{self.redis_prefix}session_to_call",
                        session_id_str,
                        call_id
                    )
                except Exception as exc:
                    logger.warning("Failed to cache call state in Redis: %s", exc)

            logger.info(
                "Registered call %s for session %s (provider: %s, direction: %s)",
                call_id,
                session_id_str,
                provider,
                direction
            )
            return call_state

        except Exception as exc:
            db.rollback()
            logger.error("Failed to register call %s: %s", call_id, exc)
            raise
        finally:
            db.close()

    def update_call_status(
        self,
        call_id: str,
        status: CallStatus,
        metadata: dict | None = None
    ) -> bool:
        """Update call status in the database.

        Args:
            call_id: Telephony provider's call identifier
            status: New call status
            metadata: Additional metadata to merge with existing metadata

        Returns:
            bool: True if update was successful, False if call not found
        """
        db = self._get_db()
        try:
            call_state = db.query(CallState).filter_by(call_id=call_id).first()
            if not call_state:
                logger.warning("Cannot update status for unknown call %s", call_id)
                return False

            call_state.status = status
            if metadata:
                # Merge new metadata with existing
                call_state.call_metadata.update(metadata)

            # Set ended_at timestamp for terminal statuses
            if status in [CallStatus.COMPLETED, CallStatus.FAILED]:
                from datetime import datetime
                call_state.ended_at = datetime.now(UTC)

            db.commit()
            logger.info("Updated call %s status to %s", call_id, status.value)
            return True

        except Exception as exc:
            db.rollback()
            logger.error("Failed to update call %s status: %s", call_id, exc)
            return False
        finally:
            db.close()

    def get_call_by_id(self, call_id: str) -> CallState | None:
        """Get call state by call ID from database.

        Args:
            call_id: Telephony provider's call identifier

        Returns:
            CallState: The call state record, or None if not found
        """
        db = self._get_db()
        try:
            return db.query(CallState).filter_by(call_id=call_id).first()
        finally:
            db.close()

    def get_session_for_call(self, call_id: str) -> UUID | None:
        """Get session ID for a call (Redis first, DB fallback).

        Args:
            call_id: Telephony provider's call identifier

        Returns:
            UUID: The session UUID, or None if not found
        """
        # Try Redis cache first
        if self.redis_client:
            try:
                session_id_str = self.redis_client.hget(
                    f"{self.redis_prefix}call_to_session",
                    call_id
                )
                if session_id_str:
                    return UUID(session_id_str)
            except Exception as exc:
                logger.debug("Redis cache miss for call %s: %s", call_id, exc)

        # Fallback to database
        call_state = self.get_call_by_id(call_id)
        if call_state:
            return UUID(call_state.session_id)

        return None

    def get_call_for_session(self, session_id: UUID) -> str | None:
        """Get call ID for a session (Redis first, DB fallback).

        Args:
            session_id: Internal session UUID

        Returns:
            str: The call ID, or None if not found
        """
        session_id_str = str(session_id)

        # Try Redis cache first
        if self.redis_client:
            try:
                call_id = self.redis_client.hget(
                    f"{self.redis_prefix}session_to_call",
                    session_id_str
                )
                if call_id:
                    return call_id
            except Exception as exc:
                logger.debug("Redis cache miss for session %s: %s", session_id_str, exc)

        # Fallback to database
        db = self._get_db()
        try:
            call_state = db.query(CallState).filter_by(
                session_id=session_id_str
            ).order_by(CallState.created_at.desc()).first()
            return call_state.call_id if call_state else None
        finally:
            db.close()

    def get_active_calls(self) -> list[CallState]:
        """Get all active calls from the database.

        Active calls are those not in a terminal state (completed/failed).

        Returns:
            List[CallState]: List of active call state records
        """
        db = self._get_db()
        try:
            return db.query(CallState).filter(
                CallState.status.in_([
                    CallStatus.INITIATED,
                    CallStatus.RINGING,
                    CallStatus.ANSWERED,
                    CallStatus.ON_HOLD,
                    CallStatus.TRANSFERRING
                ])
            ).all()
        finally:
            db.close()

    def end_call(self, call_id: str) -> bool:
        """End a call and clean up caches.

        Updates the call status to COMPLETED and removes it from Redis cache.
        The database record is preserved for historical tracking.

        Args:
            call_id: Telephony provider's call identifier

        Returns:
            bool: True if successful, False if call not found
        """
        # Update status in database
        if not self.update_call_status(call_id, CallStatus.COMPLETED):
            return False

        # Get session_id before removing from cache
        call_state = self.get_call_by_id(call_id)
        if not call_state:
            return False

        # Remove from Redis cache (keep DB record for history)
        if self.redis_client:
            try:
                self.redis_client.hdel(
                    f"{self.redis_prefix}call_to_session",
                    call_id
                )
                self.redis_client.hdel(
                    f"{self.redis_prefix}session_to_call",
                    call_state.session_id
                )
            except Exception as exc:
                logger.warning("Failed to remove call %s from Redis cache: %s", call_id, exc)

        logger.info("Ended call %s", call_id)
        return True

    def unregister_call(self, call_id: str) -> bool:
        """Unregister a call (alias for end_call for backwards compatibility).

        Args:
            call_id: Telephony provider's call identifier

        Returns:
            bool: True if successful, False if call not found
        """
        return self.end_call(call_id)

    def recover_active_calls(self) -> list[CallState]:
        """Recover active calls from database to Redis cache.

        This method should be called on server startup to restore the
        Redis cache from persistent database state.

        Returns:
            List[CallState]: List of recovered active calls
        """
        active_calls = self.get_active_calls()

        if self.redis_client and active_calls:
            try:
                for call_state in active_calls:
                    self.redis_client.hset(
                        f"{self.redis_prefix}call_to_session",
                        call_state.call_id,
                        call_state.session_id
                    )
                    self.redis_client.hset(
                        f"{self.redis_prefix}session_to_call",
                        call_state.session_id,
                        call_state.call_id
                    )
                logger.info("Recovered %d active calls to Redis cache", len(active_calls))
            except Exception as exc:
                logger.warning("Failed to recover active calls to Redis: %s", exc)

        return active_calls


# Singleton instance
_call_state_manager: PersistentCallStateManager | None = None


def get_call_state_manager() -> PersistentCallStateManager:
    """Get the singleton call state manager instance.

    Returns:
        PersistentCallStateManager: The call state manager instance
    """
    global _call_state_manager
    if _call_state_manager is None:
        _call_state_manager = PersistentCallStateManager()
    return _call_state_manager
