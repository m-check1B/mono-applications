"""
Unit tests for Agent Session Service
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.agent_session import AgentSessionStatus, AgentSessionEventType
from app.services import agent_session as service


def test_create_agent_session(db: Session, test_user: User):
    """Test creating a new agent session"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal",
        context={"project": "Test Project"},
        escalation_reason={"reason": "Too complex"}
    )

    assert session.id is not None
    assert session.userId == test_user.id
    assert session.sessionUuid == "uuid-123"
    assert session.goal == "Test Goal"
    assert session.context == {"project": "Test Project"}
    assert session.escalationReason == {"reason": "Too complex"}
    assert session.status == AgentSessionStatus.PENDING
    assert session.toolCallCount == 0


def test_update_agent_session_status(db: Session, test_user: User):
    """Test updating session status"""
    # Create initial session
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    # Update to RUNNING
    updated = service.update_agent_session_status(
        db=db,
        session_id=session.id,
        status=AgentSessionStatus.RUNNING
    )
    assert updated.status == AgentSessionStatus.RUNNING
    assert updated.startedAt is not None

    # Update to COMPLETED
    updated = service.update_agent_session_status(
        db=db,
        session_id=session.id,
        status=AgentSessionStatus.COMPLETED,
        result={"outcome": "Success"}
    )
    assert updated.status == AgentSessionStatus.COMPLETED
    assert updated.completedAt is not None
    assert updated.result == {"outcome": "Success"}


def test_update_agent_session_status_not_found(db: Session):
    """Test updating non-existent session"""
    result = service.update_agent_session_status(
        db=db,
        session_id="non-existent",
        status=AgentSessionStatus.RUNNING
    )
    assert result is None


def test_update_agent_session_progress(db: Session, test_user: User):
    """Test updating session progress"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    updated = service.update_agent_session_progress(
        db=db,
        session_id=session.id,
        progress_percent=50.0,
        current_step="Halfway there"
    )

    assert updated.progressPercent == 50.0
    assert updated.currentStep == "Halfway there"


def test_update_agent_session_progress_not_found(db: Session):
    """Test updating progress for non-existent session"""
    result = service.update_agent_session_progress(
        db=db,
        session_id="non-existent",
        progress_percent=50.0
    )
    assert result is None


def test_record_tool_call(db: Session, test_user: User):
    """Test recording a tool call"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    event = service.record_tool_call(
        db=db,
        session_id=session.id,
        tool_name="web_search",
        tool_input={"query": "python"},
        tool_output={"results": []},
        duration_ms=100
    )

    assert event.id is not None
    assert event.sessionId == session.id
    assert event.eventType == AgentSessionEventType.TOOL_CALL
    assert event.toolName == "web_search"
    assert event.toolInput == {"query": "python"}
    assert event.toolDurationMs == 100

    # Verify session update
    db.refresh(session)
    assert session.toolCallCount == 1
    assert session.lastToolCall == "web_search"
    assert session.lastToolCallAt is not None


def test_record_session_event(db: Session, test_user: User):
    """Test recording a general event"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    event = service.record_session_event(
        db=db,
        session_id=session.id,
        event_type=AgentSessionEventType.PROGRESS_UPDATE,
        event_data={"thought": "Planning..."}
    )

    assert event.id is not None
    assert event.sessionId == session.id
    assert event.eventType == AgentSessionEventType.PROGRESS_UPDATE
    assert event.eventData == {"thought": "Planning..."}


def test_get_agent_session(db: Session, test_user: User):
    """Test retrieving session"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    # Get by ID
    found = service.get_agent_session(db=db, session_id=session.id)
    assert found.id == session.id

    # Get by UUID
    found = service.get_agent_session(db=db, session_uuid="uuid-123")
    assert found.id == session.id

    # Get by User ID (auth check)
    found = service.get_agent_session(db=db, session_id=session.id, user_id=test_user.id)
    assert found.id == session.id

    # Wrong User ID
    found = service.get_agent_session(db=db, session_id=session.id, user_id="wrong-user")
    assert found is None


def test_get_session_events(db: Session, test_user: User):
    """Test retrieving session events"""
    session = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test Goal"
    )

    # Create events
    service.record_session_event(
        db=db,
        session_id=session.id,
        event_type=AgentSessionEventType.PROGRESS_UPDATE,
        event_data={"thought": "1"}
    )
    service.record_tool_call(
        db=db,
        session_id=session.id,
        tool_name="test",
        duration_ms=10
    )

    events = service.get_session_events(db=db, session_id=session.id)
    assert len(events) == 2

    # Filter by type
    tool_events = service.get_session_events(
        db=db,
        session_id=session.id,
        event_type=AgentSessionEventType.TOOL_CALL
    )
    assert len(tool_events) == 1
    assert tool_events[0].eventType == AgentSessionEventType.TOOL_CALL


def test_get_user_sessions(db: Session, test_user: User):
    """Test retrieving user sessions"""
    # Create sessions
    s1 = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-1",
        goal="Goal 1"
    )
    s2 = service.create_agent_session(
        db=db,
        user_id=test_user.id,
        session_uuid="uuid-2",
        goal="Goal 2"
    )

    sessions = service.get_user_sessions(db=db, user_id=test_user.id)
    assert len(sessions) == 2

    # Filter by status
    service.update_agent_session_status(
        db=db,
        session_id=s1.id,
        status=AgentSessionStatus.COMPLETED
    )

    completed = service.get_user_sessions(
        db=db,
        user_id=test_user.id,
        status=AgentSessionStatus.COMPLETED
    )
    assert len(completed) == 1
    assert completed[0].id == s1.id
