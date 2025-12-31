"""
Agent Session Service - Business logic for II-Agent session management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.security import generate_id
from app.models.agent_session import (
    AgentSession,
    AgentSessionEvent,
    AgentSessionStatus,
    AgentSessionEventType,
)


def create_agent_session(
    db: Session,
    *,
    user_id: str,
    session_uuid: str,
    goal: str,
    structured_goal: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    escalation_reason: Optional[Dict[str, Any]] = None,
    telemetry_id: Optional[str] = None,
) -> AgentSession:
    """
    Create a new agent session.

    Args:
        db: Database session
        user_id: User ID
        session_uuid: Unique session identifier
        goal: Natural language goal
        structured_goal: Parsed goal with steps
        context: User context (tasks, projects, etc.)
        escalation_reason: Why was this escalated to agent
        telemetry_id: Associated telemetry record ID

    Returns:
        Created agent session
    """
    session = AgentSession(
        id=generate_id(),
        userId=user_id,
        sessionUuid=session_uuid,
        goal=goal,
        structuredGoal=structured_goal,
        context=context,
        escalationReason=escalation_reason,
        telemetryId=telemetry_id,
        status=AgentSessionStatus.PENDING,
        toolCallCount=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_agent_session_status(
    db: Session,
    *,
    session_id: str,
    status: AgentSessionStatus,
    error_message: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
) -> Optional[AgentSession]:
    """
    Update agent session status.

    Args:
        db: Database session
        session_id: Agent session ID
        status: New status
        error_message: Error message if failed
        result: Final result if completed

    Returns:
        Updated agent session or None if not found
    """
    session = db.query(AgentSession).filter(AgentSession.id == session_id).first()
    if not session:
        return None

    session.status = status
    if error_message:
        session.errorMessage = error_message
    if result:
        session.result = result

    if status == AgentSessionStatus.RUNNING and not session.startedAt:
        session.startedAt = datetime.utcnow()
    elif status in (AgentSessionStatus.COMPLETED, AgentSessionStatus.FAILED, AgentSessionStatus.CANCELLED):
        session.completedAt = datetime.utcnow()

    db.commit()
    db.refresh(session)
    return session


def update_agent_session_progress(
    db: Session,
    *,
    session_id: str,
    progress_percent: Optional[float] = None,
    current_step: Optional[str] = None,
) -> Optional[AgentSession]:
    """
    Update agent session progress.

    Args:
        db: Database session
        session_id: Agent session ID
        progress_percent: Progress percentage (0-100)
        current_step: Current step description

    Returns:
        Updated agent session or None if not found
    """
    session = db.query(AgentSession).filter(AgentSession.id == session_id).first()
    if not session:
        return None

    if progress_percent is not None:
        session.progressPercent = progress_percent
    if current_step is not None:
        session.currentStep = current_step

    db.commit()
    db.refresh(session)
    return session


def record_tool_call(
    db: Session,
    *,
    session_id: str,
    tool_name: str,
    tool_input: Optional[Dict[str, Any]] = None,
    tool_output: Optional[Dict[str, Any]] = None,
    tool_error: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> AgentSessionEvent:
    """
    Record a tool call event.

    Args:
        db: Database session
        session_id: Agent session ID
        tool_name: Name of the tool called
        tool_input: Tool input parameters
        tool_output: Tool output/result
        tool_error: Error message if failed
        duration_ms: Duration in milliseconds

    Returns:
        Created event record
    """
    # Create the event
    event = AgentSessionEvent(
        id=generate_id(),
        sessionId=session_id,
        eventType=AgentSessionEventType.TOOL_CALL,
        toolName=tool_name,
        toolInput=tool_input,
        toolOutput=tool_output,
        toolError=tool_error,
        toolDurationMs=duration_ms,
        eventData={
            "tool_name": tool_name,
            "success": tool_error is None,
        },
    )
    db.add(event)

    # Update session's tool call tracking
    session = db.query(AgentSession).filter(AgentSession.id == session_id).first()
    if session:
        session.toolCallCount += 1
        session.lastToolCall = tool_name
        session.lastToolCallAt = datetime.utcnow()

    db.commit()
    db.refresh(event)
    return event


def record_session_event(
    db: Session,
    *,
    session_id: str,
    event_type: AgentSessionEventType,
    event_data: Optional[Dict[str, Any]] = None,
) -> AgentSessionEvent:
    """
    Record a general session event.

    Args:
        db: Database session
        session_id: Agent session ID
        event_type: Type of event
        event_data: Event-specific data

    Returns:
        Created event record
    """
    event = AgentSessionEvent(
        id=generate_id(),
        sessionId=session_id,
        eventType=event_type,
        eventData=event_data,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_agent_session(
    db: Session,
    *,
    session_id: Optional[str] = None,
    session_uuid: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[AgentSession]:
    """
    Get an agent session by ID or UUID.

    Args:
        db: Database session
        session_id: Agent session ID
        session_uuid: Session UUID
        user_id: User ID (for authorization)

    Returns:
        Agent session or None if not found
    """
    query = db.query(AgentSession)

    if session_id:
        query = query.filter(AgentSession.id == session_id)
    elif session_uuid:
        query = query.filter(AgentSession.sessionUuid == session_uuid)
    else:
        return None

    if user_id:
        query = query.filter(AgentSession.userId == user_id)

    return query.first()


def get_session_events(
    db: Session,
    *,
    session_id: str,
    event_type: Optional[AgentSessionEventType] = None,
    limit: int = 100,
) -> List[AgentSessionEvent]:
    """
    Get events for an agent session.

    Args:
        db: Database session
        session_id: Agent session ID
        event_type: Filter by event type (optional)
        limit: Maximum number of events to return

    Returns:
        List of session events
    """
    query = db.query(AgentSessionEvent).filter(AgentSessionEvent.sessionId == session_id)

    if event_type:
        query = query.filter(AgentSessionEvent.eventType == event_type)

    return query.order_by(AgentSessionEvent.createdAt.desc()).limit(limit).all()


def get_user_sessions(
    db: Session,
    *,
    user_id: str,
    status: Optional[AgentSessionStatus] = None,
    limit: int = 50,
) -> List[AgentSession]:
    """
    Get agent sessions for a user.

    Args:
        db: Database session
        user_id: User ID
        status: Filter by status (optional)
        limit: Maximum number of sessions to return

    Returns:
        List of agent sessions
    """
    query = db.query(AgentSession).filter(AgentSession.userId == user_id)

    if status:
        query = query.filter(AgentSession.status == status)

    return query.order_by(AgentSession.createdAt.desc()).limit(limit).all()
