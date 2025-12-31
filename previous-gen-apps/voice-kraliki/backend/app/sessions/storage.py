"""Persistent storage adapters for session management.

This module provides Redis and PostgreSQL-based storage for sessions,
call maps, and transcripts with TTL support for Milestone 2.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel

from app.config.settings import get_settings
from app.sessions.models import Session, SessionStatus

if TYPE_CHECKING:
    import redis.asyncio as redis

logger = logging.getLogger(__name__)


class SessionStorage(BaseModel):
    """Session data model for storage."""

    id: str
    provider_type: str
    provider_model: str
    strategy: str
    telephony_provider: str | None = None
    system_prompt: str | None = None
    temperature: float = 0.7
    status: str
    metadata: dict[str, Any] = {}
    created_at: str
    updated_at: str
    ended_at: str | None = None


class CallMap(BaseModel):
    """Call mapping data model for storage."""

    call_sid: str
    session_id: str
    from_number: str
    to_number: str
    status: str
    direction: str
    provider: str
    created_at: str
    updated_at: str
    ended_at: str | None = None
    metadata: dict[str, Any] = {}


class Transcript(BaseModel):
    """Transcript data model for storage."""

    session_id: str
    sequence_number: int
    timestamp: str
    speaker: str  # 'user' | 'assistant' | 'system'
    content: str
    confidence: float | None = None
    metadata: dict[str, Any] = {}


class RedisStorage:
    """Redis-based storage with TTL support for fast access."""

    def __init__(self):
        """Initialize Redis storage."""
        self.settings = get_settings()
        self._redis: redis.Redis | None = None

    async def get_redis(self) -> "redis.Redis":
        """Get Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                redis_url = getattr(self.settings, "redis_url", "redis://localhost:6379/0")
                self._redis = redis.from_url(redis_url, decode_responses=True)
            except ImportError:
                logger.error("Redis not available - install redis package")
                raise
        return self._redis

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    # Session storage
    async def store_session(self, session: Session, ttl_seconds: int = 3600) -> bool:
        """Store session in Redis with TTL."""
        try:
            r = await self.get_redis()
            key = f"session:{session.id}"

            session_data = SessionStorage(
                id=str(session.id),
                provider_type=session.provider_type,
                provider_model=session.provider_model,
                strategy=session.strategy,
                telephony_provider=session.telephony_provider,
                system_prompt=session.system_prompt,
                temperature=session.temperature,
                status=session.status.value,
                metadata=session.metadata,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                ended_at=session.ended_at.isoformat() if session.ended_at else None,
            )

            await r.setex(key, ttl_seconds, session_data.model_dump_json())
            return True
        except Exception as e:
            logger.error(f"Failed to store session {session.id} in Redis: {e}")
            return False

    async def get_session(self, session_id: UUID) -> Session | None:
        """Get session from Redis."""
        try:
            r = await self.get_redis()
            key = f"session:{session_id}"
            data = await r.get(key)

            if not data:
                return None

            session_data = SessionStorage.model_validate_json(data)

            return Session(
                id=UUID(session_data.id),
                provider_type=session_data.provider_type,
                provider_model=session_data.provider_model,
                strategy=session_data.strategy,
                telephony_provider=session_data.telephony_provider,
                system_prompt=session_data.system_prompt,
                temperature=session_data.temperature,
                status=SessionStatus(session_data.status),
                metadata=session_data.metadata,
                created_at=datetime.fromisoformat(session_data.created_at),
                updated_at=datetime.fromisoformat(session_data.updated_at),
                ended_at=datetime.fromisoformat(session_data.ended_at)
                if session_data.ended_at
                else None,
            )
        except Exception as e:
            logger.error(f"Failed to get session {session_id} from Redis: {e}")
            return None

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session from Redis."""
        try:
            r = await self.get_redis()
            key = f"session:{session_id}"
            result = await r.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete session {session_id} from Redis: {e}")
            return False

    async def list_sessions(self, status: SessionStatus | None = None) -> list[Session]:
        """List sessions from Redis."""
        try:
            r = await self.get_redis()
            pattern = "session:*"
            keys = await r.keys(pattern)

            sessions = []
            for key in keys:
                data = await r.get(key)
                if data:
                    try:
                        session_data = SessionStorage.model_validate_json(data)
                        if status is None or session_data.status == status.value:
                            session = Session(
                                id=UUID(session_data.id),
                                provider_type=session_data.provider_type,
                                provider_model=session_data.provider_model,
                                strategy=session_data.strategy,
                                telephony_provider=session_data.telephony_provider,
                                system_prompt=session_data.system_prompt,
                                temperature=session_data.temperature,
                                status=SessionStatus(session_data.status),
                                metadata=session_data.metadata,
                                created_at=datetime.fromisoformat(session_data.created_at),
                                updated_at=datetime.fromisoformat(session_data.updated_at),
                                ended_at=datetime.fromisoformat(session_data.ended_at)
                                if session_data.ended_at
                                else None,
                            )
                            sessions.append(session)
                    except Exception as e:
                        logger.warning(f"Failed to parse session data from {key}: {e}")

            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions from Redis: {e}")
            return []

    # Call map storage
    async def store_call_map(
        self, call_sid: str, session_id: UUID, ttl_seconds: int = 7200
    ) -> bool:
        """Store call mapping in Redis with TTL."""
        try:
            r = await self.get_redis()
            key = f"call_map:{call_sid}"
            await r.setex(key, ttl_seconds, str(session_id))

            # Also store reverse mapping
            reverse_key = f"session_calls:{session_id}"
            await r.sadd(reverse_key, call_sid)
            await r.expire(reverse_key, ttl_seconds)

            return True
        except Exception as e:
            logger.error(f"Failed to store call map {call_sid} in Redis: {e}")
            return False

    async def get_session_by_call(self, call_sid: str) -> UUID | None:
        """Get session ID by call SID."""
        try:
            r = await self.get_redis()
            key = f"call_map:{call_sid}"
            session_id_str = await r.get(key)

            if session_id_str:
                return UUID(session_id_str)
            return None
        except Exception as e:
            logger.error(f"Failed to get session by call {call_sid}: {e}")
            return None

    async def delete_call_map(self, call_sid: str) -> bool:
        """Delete call mapping from Redis."""
        try:
            r = await self.get_redis()
            key = f"call_map:{call_sid}"

            # Get session ID for reverse mapping cleanup
            session_id_str = await r.get(key)
            if session_id_str:
                reverse_key = f"session_calls:{session_id_str}"
                await r.srem(reverse_key, call_sid)

            result = await r.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete call map {call_sid}: {e}")
            return False

    # Transcript storage
    async def store_transcript(
        self,
        session_id: UUID,
        sequence_number: int,
        speaker: str,
        content: str,
        confidence: float | None = None,
        ttl_seconds: int = 86400,  # 24 hours
    ) -> bool:
        """Store transcript entry in Redis."""
        try:
            r = await self.get_redis()
            key = f"transcript:{session_id}:{sequence_number}"

            transcript_data = Transcript(
                session_id=str(session_id),
                sequence_number=sequence_number,
                timestamp=datetime.now(UTC).isoformat(),
                speaker=speaker,
                content=content,
                confidence=confidence,
            )

            await r.setex(key, ttl_seconds, transcript_data.model_dump_json())

            # Update sequence counter
            counter_key = f"transcript_counter:{session_id}"
            await r.set(counter_key, sequence_number)
            await r.expire(counter_key, ttl_seconds)

            return True
        except Exception as e:
            logger.error(f"Failed to store transcript for session {session_id}: {e}")
            return False

    async def get_transcripts(self, session_id: UUID) -> list[Transcript]:
        """Get all transcripts for a session."""
        try:
            r = await self.get_redis()
            pattern = f"transcript:{session_id}:*"
            keys = await r.keys(pattern)

            transcripts = []
            for key in keys:
                data = await r.get(key)
                if data:
                    try:
                        transcript = Transcript.model_validate_json(data)
                        transcripts.append(transcript)
                    except Exception as e:
                        logger.warning(f"Failed to parse transcript data from {key}: {e}")

            # Sort by sequence number
            transcripts.sort(key=lambda t: t.sequence_number)
            return transcripts
        except Exception as e:
            logger.error(f"Failed to get transcripts for session {session_id}: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and related data."""
        try:
            r = await self.get_redis()
            pattern = "session:*"
            keys = await r.keys(pattern)

            expired_count = 0
            now = datetime.now(UTC)

            for key in keys:
                try:
                    data = await r.get(key)
                    if data:
                        session_data = SessionStorage.model_validate_json(data)
                        updated_at = datetime.fromisoformat(session_data.updated_at)

                        # Clean up sessions older than 24 hours and completed
                        if session_data.status in [
                            "completed",
                            "failed",
                        ] and now - updated_at > timedelta(hours=24):
                            session_id = UUID(session_data.id)

                            # Delete session
                            await r.delete(key)

                            # Delete related call maps
                            call_pattern = f"session_calls:{session_id}"
                            call_sids = await r.smembers(call_pattern)
                            for call_sid in call_sids:
                                await r.delete(f"call_map:{call_sid}")
                            await r.delete(call_pattern)

                            # Delete transcripts
                            transcript_pattern = f"transcript:{session_id}:*"
                            transcript_keys = await r.keys(transcript_pattern)
                            if transcript_keys:
                                await r.delete(*transcript_keys)
                            await r.delete(f"transcript_counter:{session_id}")

                            expired_count += 1
                except Exception as e:
                    logger.warning(f"Failed to process session key {key}: {e}")

            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0


class PersistentSessionManager:
    """Session manager with persistent storage support."""

    def __init__(self):
        """Initialize persistent session manager."""
        self.redis_storage = RedisStorage()
        self._memory_sessions: dict[UUID, Session] = {}  # Fallback cache
        self._providers: dict[UUID, Any] = {}
        self._redis_available = True  # Assume Redis is available

    async def initialize(self):
        """Initialize storage connections."""
        # Test Redis connection
        try:
            r = await self.redis_storage.get_redis()
            await r.ping()
            logger.info("Redis storage initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage only: {e}")
            self._redis_available = False

    async def close(self):
        """Close storage connections."""
        await self.redis_storage.close()

    async def create_session(self, session: Session, ttl_seconds: int = 3600) -> bool:
        """Create session with persistent storage."""
        try:
            # Store in Redis
            success = await self.redis_storage.store_session(session, ttl_seconds)

            if success:
                # Cache in memory for fast access
                self._memory_sessions[session.id] = session
                logger.info(f"Created persistent session {session.id}")
                return True
            else:
                # Fallback to memory-only
                self._memory_sessions[session.id] = session
                logger.warning(f"Session {session.id} stored in memory only (Redis failed)")
                return False
        except Exception as e:
            logger.error(f"Failed to create persistent session {session.id}: {e}")
            # Fallback to memory-only
            self._memory_sessions[session.id] = session
            return False

    async def get_session(self, session_id: UUID) -> Session | None:
        """Get session from persistent storage."""
        try:
            # Check memory cache first
            if session_id in self._memory_sessions:
                return self._memory_sessions[session_id]

            # Try Redis
            session = await self.redis_storage.get_session(session_id)
            if session:
                self._memory_sessions[session_id] = session
                return session

            return None
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return self._memory_sessions.get(session_id)

    async def update_session(self, session: Session, ttl_seconds: int = 3600) -> bool:
        """Update session in persistent storage."""
        try:
            session.updated_at = datetime.now(UTC)
            success = await self.redis_storage.store_session(session, ttl_seconds)

            if success:
                self._memory_sessions[session.id] = session
                return True
            else:
                self._memory_sessions[session.id] = session
                return False
        except Exception as e:
            logger.error(f"Failed to update session {session.id}: {e}")
            self._memory_sessions[session.id] = session
            return False

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session from persistent storage."""
        try:
            # Delete from Redis
            success = await self.redis_storage.delete_session(session_id)

            # Remove from memory cache
            self._memory_sessions.pop(session_id, None)

            # Remove provider instance
            self._providers.pop(session_id, None)

            return success
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            # Clean up memory at least
            self._memory_sessions.pop(session_id, None)
            self._providers.pop(session_id, None)
            return False

    async def list_sessions(self, status: SessionStatus | None = None) -> list[Session]:
        """List sessions from persistent storage."""
        try:
            # Try Redis first
            sessions = await self.redis_storage.list_sessions(status)

            # Merge with memory cache for any missing ones
            memory_sessions = list(self._memory_sessions.values())
            if status:
                memory_sessions = [s for s in memory_sessions if s.status == status]

            # Combine without duplicates
            all_sessions = sessions.copy()
            for session in memory_sessions:
                if not any(s.id == session.id for s in all_sessions):
                    all_sessions.append(session)

            return all_sessions
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            # Fallback to memory only
            sessions = list(self._memory_sessions.values())
            if status:
                sessions = [s for s in sessions if s.status == status]
            return sessions

    def get_provider(self, session_id: UUID) -> Any:
        """Get provider instance for session."""
        return self._providers.get(session_id)

    def set_provider(self, session_id: UUID, provider: Any) -> None:
        """Set provider instance for session."""
        self._providers[session_id] = provider

    def remove_provider(self, session_id: UUID) -> None:
        """Remove provider instance for session."""
        self._providers.pop(session_id, None)


# Global persistent storage instance
_persistent_storage: PersistentSessionManager | None = None


async def get_persistent_storage() -> PersistentSessionManager:
    """Get global persistent storage instance."""
    global _persistent_storage
    if _persistent_storage is None:
        _persistent_storage = PersistentSessionManager()
        await _persistent_storage.initialize()
    return _persistent_storage
