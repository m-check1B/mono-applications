"""
Tests for Usage Recording in Session Manager
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from uuid import uuid4

from app.sessions.manager import SessionManager
from app.sessions.models import Session, SessionStatus

@pytest.fixture
def session_manager():
    """Create a fresh session manager instance."""
    manager = SessionManager()
    manager._sessions = {}
    manager._providers = {}
    return manager

@pytest.fixture
def mock_usage_service():
    """Mock usage service."""
    with patch("app.sessions.manager.usage_service") as mock:
        yield mock

@pytest.fixture
def mock_session_local():
    """Mock SessionLocal."""
    with patch("app.sessions.manager.SessionLocal") as mock:
        yield mock

@pytest.mark.asyncio
async def test_end_session_records_gemini_usage(session_manager, mock_usage_service, mock_session_local):
    """Test that ending a Gemini session records both voice_minutes and voice_gemini."""
    user_id = str(uuid4())
    session_id = uuid4()
    
    # Create a Gemini session
    session = Session(
        id=session_id,
        provider_type="gemini",
        provider_model="gemini-2.5-flash",
        metadata={"user_id": user_id}
    )
    
    # Set start/end times to create a 60s duration
    session.started_at = datetime.now(timezone.utc) - timedelta(seconds=60)
    session.status = SessionStatus.ACTIVE
    
    session_manager._sessions[session_id] = session
    
    # End the session
    await session_manager.end_session(session_id)
    
    # Verify usage was recorded twice: once for voice_minutes, once for voice_gemini
    assert mock_usage_service.record_usage.call_count == 2
    
    calls = mock_usage_service.record_usage.call_args_list
    
    # First call: voice_minutes
    assert calls[0].kwargs["service_type"] == "voice_minutes"
    assert calls[0].kwargs["user_id"] == user_id
    assert calls[0].kwargs["quantity"] >= 60
    
    # Second call: voice_gemini
    assert calls[1].kwargs["service_type"] == "voice_gemini"
    assert calls[1].kwargs["user_id"] == user_id
    assert calls[1].kwargs["quantity"] >= 60

@pytest.mark.asyncio
async def test_end_session_records_openai_usage(session_manager, mock_usage_service, mock_session_local):
    """Test that ending an OpenAI session records both voice_minutes and voice_openai."""
    user_id = str(uuid4())
    session_id = uuid4()
    
    # Create an OpenAI session
    session = Session(
        id=session_id,
        provider_type="openai",
        provider_model="gpt-4o-mini",
        metadata={"user_id": user_id}
    )
    
    # Set start/end times to create a 60s duration
    session.started_at = datetime.now(timezone.utc) - timedelta(seconds=60)
    session.status = SessionStatus.ACTIVE
    
    session_manager._sessions[session_id] = session
    
    # End the session
    await session_manager.end_session(session_id)
    
    # Verify usage was recorded twice: once for voice_minutes, once for voice_openai
    assert mock_usage_service.record_usage.call_count == 2
    
    calls = mock_usage_service.record_usage.call_args_list
    
    # First call: voice_minutes
    assert calls[0].kwargs["service_type"] == "voice_minutes"
    
    # Second call: voice_openai
    assert calls[1].kwargs["service_type"] == "voice_openai"
    assert calls[1].kwargs["user_id"] == user_id

@pytest.mark.asyncio
async def test_end_session_records_other_usage(session_manager, mock_usage_service, mock_session_local):
    """Test that ending a session with another provider only records voice_minutes."""
    user_id = str(uuid4())
    session_id = uuid4()
    
    # Create a Deepgram session (or other)
    session = Session(
        id=session_id,
        provider_type="deepgram",
        provider_model="nova-2",
        metadata={"user_id": user_id}
    )
    
    session.started_at = datetime.now(timezone.utc) - timedelta(seconds=60)
    session.status = SessionStatus.ACTIVE
    
    session_manager._sessions[session_id] = session
    
    # End the session
    await session_manager.end_session(session_id)
    
    # Verify usage was recorded only once
    assert mock_usage_service.record_usage.call_count == 1
    assert mock_usage_service.record_usage.call_args.kwargs["service_type"] == "voice_minutes"
