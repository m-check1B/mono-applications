"""Persistent mapping for telephony call sessions.

This module provides backwards-compatible API for call state management,
now backed by database persistence instead of in-memory dictionaries.

The persistent implementation ensures call state survives server restarts
and provides Redis caching for performance.
"""

from __future__ import annotations

import logging
from uuid import UUID

from app.telephony.call_state_manager import get_call_state_manager

logger = logging.getLogger(__name__)

# Backwards compatibility for tests that expect in-memory dicts.
# These are no-op stubs; actual state is persisted via call_state_manager.
_CALL_TO_SESSION: dict[str, UUID] = {}
_SESSION_TO_CALL: dict[UUID, str] = {}


def register_call(call_sid: str, session_id: UUID) -> None:
    """Associate telephony call SID with session ID.

    Now persists to database with Redis caching for performance.

    Args:
        call_sid: Telephony provider's call identifier
        session_id: Internal session UUID
    """
    manager = get_call_state_manager()
    try:
        manager.register_call(
            call_id=call_sid,
            session_id=session_id,
            provider="unknown",  # Provider can be enhanced later
            direction="inbound"   # Direction can be enhanced later
        )
    except Exception as exc:
        logger.error("Failed to register call %s: %s", call_sid, exc)


def get_session_for_call(call_sid: str) -> UUID | None:
    """Return session linked to call SID.

    Uses Redis cache with database fallback for reliability.

    Args:
        call_sid: Telephony provider's call identifier

    Returns:
        UUID: Session UUID or None if not found
    """
    manager = get_call_state_manager()
    try:
        return manager.get_session_for_call(call_sid)
    except Exception as exc:
        logger.error("Failed to get session for call %s: %s", call_sid, exc)
        return None


def get_call_for_session(session_id: UUID) -> str | None:
    """Return call SID linked to session.

    Uses Redis cache with database fallback for reliability.

    Args:
        session_id: Internal session UUID

    Returns:
        str: Call SID or None if not found
    """
    manager = get_call_state_manager()
    try:
        return manager.get_call_for_session(session_id)
    except Exception as exc:
        logger.error("Failed to get call for session %s: %s", session_id, exc)
        return None


def unregister_call(call_sid: str) -> None:
    """Remove call/session mapping by call SID.

    Marks call as completed in database and removes from Redis cache.
    Database record is preserved for historical tracking.

    Args:
        call_sid: Telephony provider's call identifier
    """
    manager = get_call_state_manager()
    try:
        manager.unregister_call(call_sid)
    except Exception as exc:
        logger.error("Failed to unregister call %s: %s", call_sid, exc)


def unregister_session(session_id: UUID) -> None:
    """Remove session/call mapping by session ID.

    Finds the associated call and marks it as completed.

    Args:
        session_id: Internal session UUID
    """
    manager = get_call_state_manager()
    try:
        call_sid = manager.get_call_for_session(session_id)
        if call_sid:
            manager.unregister_call(call_sid)
    except Exception as exc:
        logger.error("Failed to unregister session %s: %s", session_id, exc)
