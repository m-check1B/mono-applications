"""
Agent Sessions Router - Manage II-Agent execution sessions
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user, create_agent_token
from app.core.webhook_security import webhook_verifier
from app.models.user import User
from app.models.agent_session import AgentSessionStatus, AgentSessionEventType
from app.schemas.ai import (
    AgentSessionCreate,
    AgentSessionResponse,
    AgentSessionEventResponse,
    AgentSessionStatusUpdate,
    AgentSessionProgressUpdate,
    AgentToolCallEvent,
)
from app.services.agent_session import (
    create_agent_session,
    update_agent_session_status,
    update_agent_session_progress,
    record_tool_call,
    record_session_event,
    get_agent_session,
    get_session_events,
    get_user_sessions,
)
from app.services.request_telemetry import mark_route_decision, TelemetryRoute
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent/sessions", tags=["agent-sessions"])


@router.post("", response_model=AgentSessionResponse)
async def create_session(
    payload: AgentSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new II-Agent session with structured goals and context.

    This endpoint:
    1. Creates an agent session record with goals/context
    2. Generates an agent-scoped JWT token
    3. Updates telemetry if telemetryId provided
    4. Returns session details and token for II-Agent initialization

    The frontend can use this to:
    - Mint sessions when user clicks "Send to II-Agent"
    - Auto-escalate based on `shouldEscalate` from /ai/enhance-input or /ai/orchestrate-task
    - Provide II-Agent with Focus by Kraliki context (tasks, projects, etc.)
    """
    # Create agent token
    agent_token = create_agent_token(current_user.id)

    # Create session record
    session = create_agent_session(
        db,
        user_id=current_user.id,
        session_uuid=f"session_{current_user.id}_{payload.goal[:20]}",  # Simplified UUID
        goal=payload.goal,
        structured_goal=payload.structuredGoal,
        context=payload.context,
        escalation_reason=payload.escalationReason,
        telemetry_id=payload.telemetryId,
    )

    # Update telemetry to mark as orchestrated
    if payload.telemetryId:
        mark_route_decision(
            db,
            telemetry_id=payload.telemetryId,
            route=TelemetryRoute.ORCHESTRATED,
            reason=payload.escalationReason,
        )

    # Record session started event
    record_session_event(
        db,
        session_id=session.id,
        event_type=AgentSessionEventType.STARTED,
        event_data={
            "goal": payload.goal,
            "context_keys": list(payload.context.keys()) if payload.context else [],
        },
    )

    return AgentSessionResponse(
        id=session.id,
        sessionUuid=session.sessionUuid,
        status=session.status.value,
        goal=session.goal,
        structuredGoal=session.structuredGoal,
        context=session.context,
        agentToken=agent_token,
        toolCallCount=session.toolCallCount,
        progressPercent=session.progressPercent,
        currentStep=session.currentStep,
        createdAt=session.createdAt,
    )


@router.get("/{session_id}", response_model=AgentSessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get agent session details by ID."""
    session = get_agent_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    # Generate fresh token for this session
    agent_token = create_agent_token(current_user.id)

    return AgentSessionResponse(
        id=session.id,
        sessionUuid=session.sessionUuid,
        status=session.status.value,
        goal=session.goal,
        structuredGoal=session.structuredGoal,
        context=session.context,
        agentToken=agent_token,
        toolCallCount=session.toolCallCount,
        progressPercent=session.progressPercent,
        currentStep=session.currentStep,
        createdAt=session.createdAt,
    )


@router.patch("/{session_id}/status")
async def update_session_status(
    session_id: str,
    payload: AgentSessionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update agent session status.

    Called by:
    - Frontend when user cancels agent execution
    - II-Agent when task completes/fails (via webhook or polling)
    """
    session = get_agent_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    # Validate status enum
    try:
        status_enum = AgentSessionStatus(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {payload.status}")

    updated_session = update_agent_session_status(
        db,
        session_id=session_id,
        status=status_enum,
        error_message=payload.errorMessage,
        result=payload.result,
    )

    # Record appropriate event
    if status_enum == AgentSessionStatus.COMPLETED:
        record_session_event(
            db,
            session_id=session_id,
            event_type=AgentSessionEventType.COMPLETED,
            event_data=payload.result,
        )
    elif status_enum == AgentSessionStatus.FAILED:
        record_session_event(
            db,
            session_id=session_id,
            event_type=AgentSessionEventType.ERROR,
            event_data={"error": payload.errorMessage},
        )

    agent_token = create_agent_token(current_user.id)
    return {
        "success": True,
        "session": AgentSessionResponse(
            id=updated_session.id,
            sessionUuid=updated_session.sessionUuid,
            status=updated_session.status.value,
            goal=updated_session.goal,
            structuredGoal=updated_session.structuredGoal,
            context=updated_session.context,
            agentToken=agent_token,
            toolCallCount=updated_session.toolCallCount,
            progressPercent=updated_session.progressPercent,
            currentStep=updated_session.currentStep,
            createdAt=updated_session.createdAt,
        )
    }


@router.patch("/{session_id}/progress")
async def update_session_progress(
    session_id: str,
    payload: AgentSessionProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update agent session progress.

    II-Agent can call this periodically to update progress percentage
    and current step description for real-time UI updates.
    """
    session = get_agent_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    updated_session = update_agent_session_progress(
        db,
        session_id=session_id,
        progress_percent=payload.progressPercent,
        current_step=payload.currentStep,
    )

    # Record progress update event
    record_session_event(
        db,
        session_id=session_id,
        event_type=AgentSessionEventType.PROGRESS_UPDATE,
        event_data={
            "progress": payload.progressPercent,
            "step": payload.currentStep,
        },
    )

    agent_token = create_agent_token(current_user.id)
    return {
        "success": True,
        "session": AgentSessionResponse(
            id=updated_session.id,
            sessionUuid=updated_session.sessionUuid,
            status=updated_session.status.value,
            goal=updated_session.goal,
            structuredGoal=updated_session.structuredGoal,
            context=updated_session.context,
            agentToken=agent_token,
            toolCallCount=updated_session.toolCallCount,
            progressPercent=updated_session.progressPercent,
            currentStep=updated_session.currentStep,
            createdAt=updated_session.createdAt,
        )
    }


@router.post("/{session_id}/tool-calls")
async def record_session_tool_call(
    session_id: str,
    payload: AgentToolCallEvent,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a tool call event for telemetry.

    II-Agent (or the Focus tools themselves) can call this to log
    which tools were used, their inputs/outputs, and execution time.
    This enables:
    - Observability into agent execution
    - Debugging failed workflows
    - Analytics on tool usage patterns
    """
    session = get_agent_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    event = record_tool_call(
        db,
        session_id=session_id,
        tool_name=payload.toolName,
        tool_input=payload.toolInput,
        tool_output=payload.toolOutput,
        tool_error=payload.toolError,
        duration_ms=payload.durationMs,
    )

    return {"success": True, "event_id": event.id}


@router.get("/{session_id}/events", response_model=List[AgentSessionEventResponse])
async def list_session_events(
    session_id: str,
    event_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get events for an agent session.

    Returns chronological log of:
    - Session start/completion
    - Tool calls with inputs/outputs
    - Progress updates
    - Errors

    Useful for:
    - Debugging agent execution
    - Showing execution timeline in UI
    - Post-mortem analysis of failed tasks
    """
    session = get_agent_session(db, session_id=session_id, user_id=current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Agent session not found")

    # Parse event type if provided
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = AgentSessionEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event_type: {event_type}")

    events = get_session_events(
        db,
        session_id=session_id,
        event_type=event_type_enum,
        limit=limit,
    )

    return [
        AgentSessionEventResponse(
            id=e.id,
            sessionId=e.sessionId,
            eventType=e.eventType.value,
            toolName=e.toolName,
            toolInput=e.toolInput,
            toolOutput=e.toolOutput,
            toolError=e.toolError,
            eventData=e.eventData,
            createdAt=e.createdAt,
        )
        for e in events
    ]


@router.get("", response_model=List[AgentSessionResponse])
async def list_user_sessions(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get agent sessions for the current user.

    Supports filtering by status and pagination via limit.
    Useful for showing session history in the UI.
    """
    # Parse status if provided
    status_enum = None
    if status:
        try:
            status_enum = AgentSessionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    sessions = get_user_sessions(
        db,
        user_id=current_user.id,
        status=status_enum,
        limit=limit,
    )

    # Generate fresh token (though not typically needed for listing)
    agent_token = create_agent_token(current_user.id)

    return [
        AgentSessionResponse(
            id=s.id,
            sessionUuid=s.sessionUuid,
            status=s.status.value,
            goal=s.goal,
            structuredGoal=s.structuredGoal,
            context=s.context,
            agentToken=agent_token,  # Same token for all in list
            toolCallCount=s.toolCallCount,
            progressPercent=s.progressPercent,
            currentStep=s.currentStep,
            createdAt=s.createdAt,
        )
        for s in sessions
    ]


@router.post("/webhook/callback")
async def ii_agent_webhook_callback(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(None, alias="X-II-Agent-Signature"),
    x_timestamp: Optional[str] = Header(None, alias="X-II-Agent-Timestamp"),
    x_signature_type: Optional[str] = Header(None, alias="X-II-Agent-Signature-Type")
):
    """
    Webhook callback for II-Agent execution updates.

    This endpoint receives secure callbacks from II-Agent when:
    - Task execution completes
    - Task execution fails
    - Progress updates occur
    - Tool calls are executed

    Security:
    - Ed25519 or HMAC-SHA256 signature verification required
    - Timestamp validation to prevent replay attacks
    - Fail-closed: rejects requests with invalid/missing signatures

    Headers required:
    - X-II-Agent-Signature: Base64-encoded signature
    - X-II-Agent-Timestamp: Unix timestamp
    - X-II-Agent-Signature-Type: "ed25519" or "hmac-sha256" (optional, defaults to "hmac-sha256")

    Request body:
    {
        "session_id": "string",
        "event_type": "completed" | "failed" | "progress" | "tool_call",
        "data": {
            "status": "completed",  // for completion/failure
            "result": {},           // for completion
            "error": "string",      // for failure
            "progress": 75,         // for progress updates
            "current_step": "...",  // for progress updates
            "tool_name": "...",     // for tool calls
            "tool_output": {}       // for tool calls
        }
    }
    """
    # Verify webhook signature (fail closed)
    try:
        payload = await webhook_verifier.verify_ii_agent_webhook(
            request,
            x_signature=x_signature,
            x_timestamp=x_timestamp,
            x_signature_type=x_signature_type
        )
    except HTTPException as e:
        logger.error(f"II-Agent webhook signature verification failed: {e.detail}")
        raise

    # Extract payload fields
    session_id = payload.get("session_id")
    event_type = payload.get("event_type")
    data = payload.get("data", {})

    if not session_id or not event_type:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: session_id, event_type"
        )

    # Get session (no user auth needed - signature verified)
    session = get_agent_session(db, session_id=session_id)

    if not session:
        logger.warning(f"II-Agent webhook for unknown session: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    # Process event based on type
    try:
        if event_type == "completed":
            # Update session status to completed
            update_agent_session_status(
                db,
                session_id=session_id,
                status=AgentSessionStatus.COMPLETED,
                result=data.get("result")
            )
            record_session_event(
                db,
                session_id=session_id,
                event_type=AgentSessionEventType.COMPLETED,
                event_data=data
            )
            logger.info(f"II-Agent session {session_id} completed via webhook")

        elif event_type == "failed":
            # Update session status to failed
            update_agent_session_status(
                db,
                session_id=session_id,
                status=AgentSessionStatus.FAILED,
                error_message=data.get("error")
            )
            record_session_event(
                db,
                session_id=session_id,
                event_type=AgentSessionEventType.ERROR,
                event_data=data
            )
            logger.error(f"II-Agent session {session_id} failed: {data.get('error')}")

        elif event_type == "progress":
            # Update progress
            update_agent_session_progress(
                db,
                session_id=session_id,
                progress_percent=data.get("progress"),
                current_step=data.get("current_step")
            )
            record_session_event(
                db,
                session_id=session_id,
                event_type=AgentSessionEventType.PROGRESS_UPDATE,
                event_data=data
            )
            logger.debug(f"II-Agent session {session_id} progress: {data.get('progress')}%")

        elif event_type == "tool_call":
            # Record tool call
            record_tool_call(
                db,
                session_id=session_id,
                tool_name=data.get("tool_name"),
                tool_input=data.get("tool_input"),
                tool_output=data.get("tool_output"),
                tool_error=data.get("tool_error"),
                duration_ms=data.get("duration_ms")
            )
            logger.debug(f"II-Agent session {session_id} tool call: {data.get('tool_name')}")

        else:
            logger.warning(f"Unknown II-Agent webhook event type: {event_type}")
            raise HTTPException(status_code=400, detail=f"Unknown event_type: {event_type}")

        return {
            "success": True,
            "session_id": session_id,
            "event_type": event_type,
            "message": "Webhook processed successfully"
        }

    except Exception as e:
        logger.error(f"Error processing II-Agent webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process webhook: {str(e)}"
        )
