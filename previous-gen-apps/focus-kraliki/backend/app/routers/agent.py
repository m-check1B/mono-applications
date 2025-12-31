"""
Agent Router - Authentication and session management for II-Agent
"""

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Dict, Optional

from app.core.database import get_db
from app.core.security import get_current_user, create_agent_token, generate_id
from app.models.user import User
from app.services.request_telemetry import mark_route_decision, TelemetryRoute

router = APIRouter(prefix="/agent", tags=["agent"])

# ========== Request/Response Schemas ==========

class AgentSessionResponse(BaseModel):
    """Response schema for agent session creation"""
    agentToken: str
    sessionUuid: str
    userId: str
    expiresIn: int = 7200  # 2 hours in seconds


class AgentSessionRequest(BaseModel):
    """Optional telemetry payload when creating agent session"""
    telemetryId: Optional[str] = None
    reason: Optional[Dict[str, Any]] = None

# ========== Agent Session Endpoints ==========

@router.post("/sessions", response_model=AgentSessionResponse)
async def create_agent_session(
    payload: Optional[AgentSessionRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new agent session token for II-Agent.

    This endpoint allows the frontend to obtain an agent-scoped JWT token
    that II-Agent can use to access Focus by Kraliki APIs on behalf of the user.

    The agent token:
    - Has a longer expiry (2 hours) than regular access tokens
    - Includes a scope claim to identify it as an agent token
    - Can be used with all Focus by Kraliki APIs that require authentication

    Returns:
        agentToken: JWT token for II-Agent to use
        sessionUuid: Unique session identifier
        userId: The authenticated user's ID
        expiresIn: Token expiry time in seconds (7200 = 2 hours)
    """
    # Create agent-scoped token
    agent_token = create_agent_token(current_user.id)

    # Generate unique session identifier
    session_uuid = generate_id()

    if payload and payload.telemetryId:
        mark_route_decision(
            db,
            telemetry_id=payload.telemetryId,
            route=TelemetryRoute.ORCHESTRATED,
            reason=payload.reason,
        )

    return AgentSessionResponse(
        agentToken=agent_token,
        sessionUuid=session_uuid,
        userId=current_user.id,
        expiresIn=7200
    )
