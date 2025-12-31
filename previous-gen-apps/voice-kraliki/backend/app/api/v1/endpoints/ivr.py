"""IVR (Interactive Voice Response) API endpoints."""

from datetime import UTC, datetime

from app.auth.jwt_auth import get_current_user
from app.database import get_db
from app.models.ivr import (
    IVRFlowCreate,
    IVRFlowResponse,
    IVRFlowUpdate,
    IVRSessionCreate,
    IVRSessionResponse,
)
from app.models.user import User
from app.services.ivr import IVRExecutionError, IVRService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


# ===== Flow Management =====

@router.post("/flows", response_model=IVRFlowResponse, status_code=status.HTTP_201_CREATED)
def create_ivr_flow(
    flow_data: IVRFlowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new IVR flow."""
    service = IVRService(db)

    try:
        flow = service.create_flow(flow_data)
        return flow
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create IVR flow: {str(e)}"
        )


@router.get("/flows", response_model=list[IVRFlowResponse])
def list_ivr_flows(
    campaign_id: int | None = Query(None),
    team_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all IVR flows with optional filters."""
    service = IVRService(db)

    flows = service.list_flows(
        campaign_id=campaign_id,
        team_id=team_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return flows


@router.get("/flows/{flow_id}", response_model=IVRFlowResponse)
def get_ivr_flow(
    flow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific IVR flow by ID."""
    service = IVRService(db)

    flow = service.get_flow(flow_id)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    return flow


@router.put("/flows/{flow_id}", response_model=IVRFlowResponse)
def update_ivr_flow(
    flow_id: int,
    flow_data: IVRFlowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an IVR flow."""
    service = IVRService(db)

    flow = service.update_flow(flow_id, flow_data)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    return flow


@router.delete("/flows/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ivr_flow(
    flow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an IVR flow."""
    service = IVRService(db)

    success = service.delete_flow(flow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    return None


@router.post("/flows/{flow_id}/publish", response_model=IVRFlowResponse)
def publish_ivr_flow(
    flow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish an IVR flow (mark as production-ready)."""
    service = IVRService(db)

    flow = service.publish_flow(flow_id)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    return flow


# ===== Session Management =====

@router.post("/sessions/start", response_model=dict, status_code=status.HTTP_201_CREATED)
def start_ivr_session(
    session_data: IVRSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new IVR session for a call.

    Returns the session and the initial action to perform.
    """
    service = IVRService(db)

    try:
        session, initial_action = service.start_session(
            flow_id=session_data.flow_id,
            call_sid=session_data.call_sid,
            caller_phone=session_data.caller_phone,
            language=session_data.language
        )

        return {
            "session": IVRSessionResponse.model_validate(session),
            "action": initial_action
        }
    except IVRExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start IVR session: {str(e)}"
        )


@router.post("/sessions/{call_sid}/input", response_model=dict)
def handle_ivr_input(
    call_sid: str,
    user_input: str = Query(..., description="User input (DTMF digit or speech text)"),
    input_type: str = Query("dtmf", description="Input type: dtmf or speech"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handle user input (DTMF or speech) for an active IVR session.

    Returns the next action to perform.
    """
    service = IVRService(db)

    try:
        action = service.handle_input(call_sid, user_input, input_type)
        return {"action": action}
    except IVRExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle input: {str(e)}"
        )


@router.post("/sessions/{call_sid}/timeout", response_model=dict)
def handle_ivr_timeout(
    call_sid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handle input timeout for an active IVR session.

    Returns the next action to perform (usually replay with timeout message).
    """
    service = IVRService(db)

    try:
        action = service.handle_timeout(call_sid)
        return {"action": action}
    except IVRExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle timeout: {str(e)}"
        )


@router.post("/sessions/{call_sid}/end", response_model=IVRSessionResponse)
def end_ivr_session(
    call_sid: str,
    exit_reason: str = Query(..., description="Reason for ending (completed, abandoned, error)"),
    transferred_to: str | None = Query(None, description="Transfer destination if applicable"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End an active IVR session."""
    service = IVRService(db)

    try:
        session = service.end_session(call_sid, exit_reason, transferred_to)
        return session
    except IVRExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=IVRSessionResponse)
def get_ivr_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an IVR session by ID."""
    service = IVRService(db)

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR session {session_id} not found"
        )

    return session


@router.get("/sessions/by-call/{call_sid}", response_model=IVRSessionResponse)
def get_ivr_session_by_call(
    call_sid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an IVR session by call SID."""
    service = IVRService(db)

    session = service.get_session_by_call_sid(call_sid)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR session not found for call {call_sid}"
        )

    return session


# ===== Analytics =====

@router.get("/flows/{flow_id}/analytics", response_model=dict)
def get_flow_analytics(
    flow_id: int,
    start_date: datetime | None = Query(None, description="Start date for analytics range"),
    end_date: datetime | None = Query(None, description="End date for analytics range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for an IVR flow."""
    service = IVRService(db)

    analytics = service.get_flow_analytics(flow_id, start_date, end_date)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    return analytics


# ===== Testing & Validation =====

@router.post("/flows/{flow_id}/test", response_model=dict)
def test_ivr_flow(
    flow_id: int,
    test_inputs: list[str] = Query(..., description="Sequence of inputs to test"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Test an IVR flow with a sequence of inputs.

    Returns the path taken through the flow.
    """
    service = IVRService(db)

    flow = service.get_flow(flow_id)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IVR flow {flow_id} not found"
        )

    # Create a test session
    test_call_sid = f"test_{flow_id}_{int(datetime.now(UTC).timestamp())}"

    try:
        session, initial_action = service.start_session(
            flow_id=flow_id,
            call_sid=test_call_sid,
            caller_phone="test"
        )

        path = [{
            "node_id": session.current_node_id,
            "action": initial_action
        }]

        # Process test inputs
        for user_input in test_inputs:
            action = service.handle_input(test_call_sid, user_input)
            path.append({
                "input": user_input,
                "action": action
            })

            # Stop if call ended
            if action.get("action") in ["end_call", "transfer"]:
                break

        # Clean up test session
        service.end_session(test_call_sid, "test_completed")

        return {
            "flow_id": flow_id,
            "test_call_sid": test_call_sid,
            "path": path
        }

    except Exception as e:
        # Try to clean up
        try:
            service.end_session(test_call_sid, "test_error")
        except Exception:
            pass  # Ignore cleanup errors during error handling

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )
