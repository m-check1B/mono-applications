"""
Targeted tests to improve coverage for Agent Session Service
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services import agent_session as service
from app.models.agent_session import AgentSession, AgentSessionEvent, AgentSessionStatus, AgentSessionEventType
from app.models.user import User

def test_create_agent_session_logic(db: Session, test_user: User):
    """Test create_agent_session service logic"""
    session = service.create_agent_session(
        db, 
        user_id=test_user.id,
        session_uuid="uuid-123",
        goal="Test goal"
    )
    
    assert session.userId == test_user.id
    assert session.sessionUuid == "uuid-123"
    assert session.goal == "Test goal"
    assert session.status == AgentSessionStatus.PENDING
    
    # Verify in DB
    db_session = db.query(AgentSession).filter_by(id=session.id).first()
    assert db_session is not None

def test_update_agent_session_status_logic(db: Session, test_user: User):
    """Test updating agent session status"""
    session = service.create_agent_session(db, user_id=test_user.id, session_uuid="u1", goal="g")
    
    updated = service.update_agent_session_status(db, session_id=session.id, status=AgentSessionStatus.RUNNING)
    assert updated.status == AgentSessionStatus.RUNNING
    assert updated.startedAt is not None
    
    # Test completed status sets end time
    updated = service.update_agent_session_status(db, session_id=session.id, status=AgentSessionStatus.COMPLETED)
    assert updated.status == AgentSessionStatus.COMPLETED
    assert updated.completedAt is not None

def test_record_session_event_logic(db: Session, test_user: User):
    """Test recording events in session"""
    session = service.create_agent_session(db, user_id=test_user.id, session_uuid="u1", goal="g")
    
    event = service.record_session_event(
        db, 
        session_id=session.id,
        event_type=AgentSessionEventType.PROGRESS_UPDATE,
        event_data={"progress": 50}
    )
    
    assert event.sessionId == session.id
    assert event.eventType == AgentSessionEventType.PROGRESS_UPDATE
    assert event.eventData == {"progress": 50}
    
    # Verify in DB
    db_event = db.query(AgentSessionEvent).filter_by(id=event.id).first()
    assert db_event is not None

def test_record_tool_call_logic(db: Session, test_user: User):
    """Test recording tool calls"""
    session = service.create_agent_session(db, user_id=test_user.id, session_uuid="u1", goal="g")
    
    event = service.record_tool_call(
        db,
        session_id=session.id,
        tool_name="web_search",
        tool_input={"query": "test"},
        tool_output={"results": "none"}
    )
    
    assert event.sessionId == session.id
    assert event.eventType == AgentSessionEventType.TOOL_CALL
    assert event.toolName == "web_search"
    assert event.toolInput == {"query": "test"}
    assert event.toolOutput == {"results": "none"}
    
    # Verify session updated
    db.refresh(session)
    assert session.toolCallCount == 1
    assert session.lastToolCall == "web_search"

def test_get_user_sessions_logic(db: Session, test_user: User):
    """Test retrieving sessions for a user"""
    # Clear sessions
    db.query(AgentSessionEvent).delete()
    db.query(AgentSession).delete()
    db.commit()
    
    service.create_agent_session(db, user_id=test_user.id, session_uuid="u1", goal="g1")
    service.create_agent_session(db, user_id=test_user.id, session_uuid="u2", goal="g2")
    
    sessions = service.get_user_sessions(db, user_id=test_user.id)
    assert len(sessions) == 2

def test_update_agent_session_progress_logic(db: Session, test_user: User):
    """Test updating agent session progress"""
    session = service.create_agent_session(db, user_id=test_user.id, session_uuid="u1", goal="g")
    
    updated = service.update_agent_session_progress(
        db, 
        session_id=session.id, 
        progress_percent=75.0,
        current_step="Analyzing data"
    )
    
    assert updated.progressPercent == 75.0
    assert updated.currentStep == "Analyzing data"