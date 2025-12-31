"""
Unit tests for Agent Sessions Router
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.models.agent_session import AgentSessionStatus, AgentSessionEventType
from app.models.user import User
from app.core.security import create_agent_token

def test_create_session(client, test_user, auth_headers):
    """Test creating a new agent session"""
    response = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={
            "goal": "Test Goal",
            "context": {"project": "Test Project"},
            "escalationReason": {"reason": "complexity"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["goal"] == "Test Goal"
    assert data["status"] == "pending"
    assert "agentToken" in data
    assert data["context"] == {"project": "Test Project"}


def test_get_session(client, test_user, auth_headers, db):
    """Test getting a session"""
    # Create session first
    create_res = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={"goal": "Test Get"}
    )
    session_id = create_res.json()["id"]

    # Get session
    response = client.get(f"/agent/sessions/{session_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["goal"] == "Test Get"
    assert "agentToken" in data


def test_update_session_status(client, test_user, auth_headers):
    """Test updating session status"""
    # Create session
    create_res = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={"goal": "Test Status"}
    )
    session_id = create_res.json()["id"]

    # Update status
    response = client.patch(
        f"/agent/sessions/{session_id}/status",
        headers=auth_headers,
        json={
            "status": "running"
        }
    )
    assert response.status_code == 200
    assert response.json()["session"]["status"] == "running"

    # Complete
    response = client.patch(
        f"/agent/sessions/{session_id}/status",
        headers=auth_headers,
        json={
            "status": "completed",
            "result": {"done": True}
        }
    )
    assert response.status_code == 200
    assert response.json()["session"]["status"] == "completed"


def test_update_session_progress(client, test_user, auth_headers):
    """Test updating session progress"""
    # Create session
    create_res = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={"goal": "Test Progress"}
    )
    session_id = create_res.json()["id"]

    response = client.patch(
        f"/agent/sessions/{session_id}/progress",
        headers=auth_headers,
        json={
            "progressPercent": 50.5,
            "currentStep": "Working hard"
        }
    )
    assert response.status_code == 200
    assert response.json()["session"]["progressPercent"] == 50.5
    assert response.json()["session"]["currentStep"] == "Working hard"


def test_record_session_tool_call(client, test_user, auth_headers):
    """Test recording tool call"""
    # Create session
    create_res = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={"goal": "Test Tool"}
    )
    session_id = create_res.json()["id"]

    response = client.post(
        f"/agent/sessions/{session_id}/tool-calls",
        headers=auth_headers,
        json={
            "toolName": "test_tool",
            "toolInput": {"arg": 1},
            "durationMs": 100
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "event_id" in response.json()


def test_list_session_events(client, test_user, auth_headers):
    """Test listing session events"""
    # Create session
    create_res = client.post(
        "/agent/sessions",
        headers=auth_headers,
        json={"goal": "Test Events"}
    )
    session_id = create_res.json()["id"]

    # Create some events (status update, tool call)
    client.patch(
        f"/agent/sessions/{session_id}/status",
        headers=auth_headers,
        json={"status": "running"}
    )
    client.post(
        f"/agent/sessions/{session_id}/tool-calls",
        headers=auth_headers,
        json={"toolName": "test", "durationMs": 10}
    )

    # List events
    response = client.get(f"/agent/sessions/{session_id}/events", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    # Should have STARTED (from create), RUNNING (implied?), and TOOL_CALL
    # Note: update_status doesn't record generic event unless completed/failed, 
    # but create_session records STARTED.
    assert len(events) >= 1 


def test_list_user_sessions(client, test_user, auth_headers):
    """Test listing user sessions"""
    # Create 2 sessions
    client.post("/agent/sessions", headers=auth_headers, json={"goal": "1"})
    client.post("/agent/sessions", headers=auth_headers, json={"goal": "2"})

    response = client.get("/agent/sessions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@patch("app.routers.agent_sessions.webhook_verifier.verify_ii_agent_webhook")
def test_ii_agent_webhook_callback(mock_verify, client, db, test_user):
    """Test webhook callback"""
    # Create session first
    create_res = client.post(
        "/agent/sessions",
        headers={"Authorization": f"Bearer {create_agent_token(test_user.id)}"}, # Use agent token or user token
        json={"goal": "Test Webhook"}
    )
    # Need to use user token to create session
    # But here I can't easily switch tokens in the middle of test setup without multiple headers.
    # Let's just use the service to create a session directly.
    from app.services.agent_session import create_agent_session
    session = create_agent_session(
        db,
        user_id=test_user.id,
        session_uuid="webhook-uuid",
        goal="Test Webhook"
    )
    session_id = session.id

    # Mock verification
    mock_verify.return_value = {
        "session_id": session_id,
        "event_type": "completed",
        "data": {"result": {"success": True}}
    }

    # Call webhook
    response = client.post(
        "/agent/sessions/webhook/callback",
        headers={
            "X-II-Agent-Signature": "dummy",
            "X-II-Agent-Timestamp": "123456"
        },
        json={} # Body doesn't matter as we mock the verifier return
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify session status updated
    db.refresh(session)
    assert session.status == AgentSessionStatus.COMPLETED
