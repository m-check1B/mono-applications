"""Session Management API Routes.

This module provides REST API endpoints for managing AI provider sessions,
including session lifecycle management and mid-call provider switching.
"""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from app.auth.jwt_auth import get_current_user
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    limiter,
)
from app.models.user import User
from app.services.provider_failover import get_failover_service
from app.services.provider_orchestration import get_orchestrator
from app.sessions.manager import get_session_manager
from app.sessions.models import SessionStatus

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


# Request/Response Models
class ProviderSwitchRequest(BaseModel):
    """Request for switching provider during active session."""
    provider: str = Field(..., description="Target provider ID")
    preserve_context: bool = Field(default=True, description="Preserve conversation context")
    reason: str | None = Field(default=None, description="Reason for switch")


class ProviderSwitchResponse(BaseModel):
    """Response for provider switch operation."""
    success: bool
    session_id: str
    from_provider: str
    to_provider: str
    context_preserved: int
    switched_at: str
    error_message: str | None = None


class SessionDetailResponse(BaseModel):
    """Detailed session information."""
    id: str
    provider_type: str
    provider_model: str
    status: str
    created_at: str
    updated_at: str
    ended_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    switch_history: list[dict[str, Any]] = Field(default_factory=list)


class SessionListResponse(BaseModel):
    """List of sessions."""
    sessions: list[SessionDetailResponse]
    total: int
    offset: int
    limit: int


class AutoFailoverRequest(BaseModel):
    """Request for triggering auto-failover check."""
    force: bool = Field(default=False, description="Force failover even if provider healthy")


# Session Management Endpoints
@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get session details by ID.

    Args:
        session_id: Session identifier
        current_user: Authenticated user

    Returns:
        Session details including switch history

    Raises:
        HTTPException: If session not found
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    session_manager = get_session_manager()
    session = await session_manager.get_session(session_uuid)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )

    # Get switch history
    failover_service = get_failover_service()
    switch_history = failover_service.get_switch_history(session_uuid)

    # Format switch history
    formatted_history = [
        {
            "from_provider": switch.from_provider,
            "to_provider": switch.to_provider,
            "switched_at": switch.switched_at.isoformat(),
            "context_preserved": switch.context_preserved,
            "success": switch.success,
            "error_message": switch.error_message
        }
        for switch in switch_history
    ]

    return SessionDetailResponse(
        id=str(session.id),
        provider_type=session.provider_type,
        provider_model=session.provider_model,
        status=session.status.value,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        ended_at=session.ended_at.isoformat() if session.ended_at else None,
        metadata=session.metadata or {},
        switch_history=formatted_history
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """List sessions with optional filtering.

    Args:
        status_filter: Optional status filter
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        current_user: Authenticated user

    Returns:
        List of sessions
    """
    session_manager = get_session_manager()

    # Parse status filter if provided
    status_enum = None
    if status_filter:
        try:
            status_enum = SessionStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    # Get sessions
    sessions = await session_manager.list_sessions(status=status_enum)

    # Get switch history for each session
    failover_service = get_failover_service()

    session_responses = []
    for session in sessions[offset:offset + limit]:
        switch_history = failover_service.get_switch_history(session.id)
        formatted_history = [
            {
                "from_provider": switch.from_provider,
                "to_provider": switch.to_provider,
                "switched_at": switch.switched_at.isoformat(),
                "context_preserved": switch.context_preserved,
                "success": switch.success,
                "error_message": switch.error_message
            }
            for switch in switch_history
        ]

        session_responses.append(
            SessionDetailResponse(
                id=str(session.id),
                provider_type=session.provider_type,
                provider_model=session.provider_model,
                status=session.status.value,
                created_at=session.created_at.isoformat(),
                updated_at=session.updated_at.isoformat(),
                ended_at=session.ended_at.isoformat() if session.ended_at else None,
                metadata=session.metadata or {},
                switch_history=formatted_history
            )
        )

    return SessionListResponse(
        sessions=session_responses,
        total=len(sessions),
        offset=offset,
        limit=limit
    )


# Provider Switching Endpoints
@router.post("/{session_id}/switch-provider", response_model=ProviderSwitchResponse)
async def switch_provider(
    session_id: str,
    request: ProviderSwitchRequest = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Switch AI provider for active session.

    This endpoint enables mid-call provider switching while preserving
    conversation context and state.

    Args:
        session_id: Session identifier
        request: Provider switch request
        current_user: Authenticated user

    Returns:
        Provider switch result

    Raises:
        HTTPException: If session not found or switch fails
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    if not request.provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider required"
        )

    orchestrator = get_orchestrator()

    try:
        logger.info(
            f"User {current_user.id} switching provider for session {session_id} "
            f"to {request.provider}"
        )

        result = await orchestrator.switch_session_provider(
            session_uuid,
            request.provider,
            request.preserve_context
        )

        return ProviderSwitchResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider switch failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during provider switch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provider switch failed: {str(e)}"
        )


@router.get("/{session_id}/switch-status")
async def get_switch_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get current provider switch status for session.

    Args:
        session_id: Session identifier
        current_user: Authenticated user

    Returns:
        Switch status or None if no switch in progress
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    failover_service = get_failover_service()
    switch_status = failover_service.get_switch_status(session_uuid)

    if not switch_status:
        return {
            "in_progress": False,
            "message": "No switch in progress"
        }

    return {
        "in_progress": True,
        "from_provider": switch_status.from_provider,
        "to_provider": switch_status.to_provider,
        "started_at": switch_status.started_at.isoformat(),
        "reason": switch_status.reason,
        "status": switch_status.status
    }


@router.post("/{session_id}/auto-failover")
async def trigger_auto_failover(
    session_id: str,
    request: AutoFailoverRequest = Body(default=AutoFailoverRequest()),
    current_user: User = Depends(get_current_user)
):
    """Trigger automatic failover check for session.

    Checks if current provider is unhealthy and switches to a healthy
    alternative if needed.

    Args:
        session_id: Session identifier
        request: Auto-failover request
        current_user: Authenticated user

    Returns:
        Failover result or message if no failover needed
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    failover_service = get_failover_service()

    logger.info(
        f"User {current_user.id} triggering auto-failover check "
        f"for session {session_id}"
    )

    result = await failover_service.auto_failover_if_needed(session_uuid)

    if not result:
        return {
            "failover_triggered": False,
            "message": "Current provider is healthy, no failover needed"
        }

    return {
        "failover_triggered": True,
        "success": result.success,
        "from_provider": result.from_provider,
        "to_provider": result.to_provider,
        "context_preserved": result.context_preserved,
        "switched_at": result.switched_at.isoformat(),
        "error_message": result.error_message
    }


@router.get("/{session_id}/switch-history")
async def get_switch_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get provider switch history for session.

    Args:
        session_id: Session identifier
        current_user: Authenticated user

    Returns:
        List of provider switches
    """
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    failover_service = get_failover_service()
    switch_history = failover_service.get_switch_history(session_uuid)

    return {
        "session_id": session_id,
        "total_switches": len(switch_history),
        "switches": [
            {
                "from_provider": switch.from_provider,
                "to_provider": switch.to_provider,
                "switched_at": switch.switched_at.isoformat(),
                "context_preserved": switch.context_preserved,
                "success": switch.success,
                "error_message": switch.error_message
            }
            for switch in switch_history
        ]
    }


# Health Check
@limiter.limit(API_RATE_LIMIT)
@router.get("/health")
async def health_check(request: Request):
    """Health check endpoint for sessions API."""
    return {
        "status": "healthy",
        "service": "sessions-api",
        "features": [
            "session_management",
            "provider_switching",
            "auto_failover",
            "context_preservation"
        ]
    }
