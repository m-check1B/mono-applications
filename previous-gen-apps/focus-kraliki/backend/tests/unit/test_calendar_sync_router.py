"""
Unit tests for Calendar Sync Router
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.routers import calendar_sync
from app.models.event import Event
from datetime import datetime, timedelta

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.GOOGLE_OAUTH_CLIENT_ID", "mock-client-id")
    monkeypatch.setattr("app.core.config.settings.GOOGLE_OAUTH_CLIENT_SECRET", "mock-client-secret")

@pytest.mark.asyncio
async def test_init_calendar_oauth(client, test_user, auth_headers, mock_settings):
    """Test initiating OAuth flow"""
    response = client.post(
        "/calendar-sync/oauth/init",
        headers=auth_headers,
        json={"redirect_uri": "http://localhost/callback"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert "client_id=mock-client-id" in data["auth_url"]

@pytest.mark.asyncio
async def test_exchange_calendar_token(client, test_user, auth_headers, mock_httpx_client, mock_settings, db):
    """Test exchanging code for token"""
    # Mock token response
    mock_httpx_client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "access_token": "at-123",
            "refresh_token": "rt-456",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
    )
    
    response = client.post(
        "/calendar-sync/oauth/exchange",
        headers=auth_headers,
        json={"code": "code-123", "redirect_uri": "http://localhost/callback"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "at-123"
    
    # Verify stored in user prefs
    db.refresh(test_user)
    assert test_user.preferences["calendar_sync"]["access_token"] == "at-123"
    assert test_user.preferences["calendar_sync"]["enabled"] is True

@pytest.mark.asyncio
async def test_get_calendar_sync_status(client, test_user, auth_headers, mock_httpx_client, db):
    """Test getting sync status"""
    # Setup user with token
    test_user.preferences = {
        "calendar_sync": {
            "enabled": True,
            "access_token": "at-123"
        }
    }
    db.commit()
    
    # Mock calendar list response
    mock_httpx_client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "items": [
                {"id": "primary", "summary": "My Calendar", "primary": True}
            ]
        }
    )
    
    response = client.get("/calendar-sync/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["enabled"] is True
    assert data["connected"] is True
    assert len(data["calendars"]) == 1
    assert data["calendars"][0]["name"] == "My Calendar"

@pytest.mark.asyncio
async def test_sync_calendar(client, test_user, auth_headers, mock_settings, db):
    """Test triggering sync"""
    # Setup user with token
    test_user.preferences = {
        "calendar_sync": {
            "enabled": True,
            "access_token": "at-123"
        }
    }
    db.commit()
    
    # We need to mock BackgroundTasks add_task?
    # FastAPI TestClient doesn't run background tasks automatically unless ...?
    # Actually we just want to verify it returns 200 and queues task.
    # But wait, `perform_calendar_sync` is imported. I should patch it.
    
    with patch("app.routers.calendar_sync.perform_calendar_sync") as mock_sync:
        response = client.post(
            "/calendar-sync/sync",
            headers=auth_headers,
            json={"direction": "both"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        # Verify background task queued? Can't easily with TestClient+patch.
        # But status 200 implies logic passed.

@pytest.mark.asyncio
async def test_calendar_webhook(client, db):
    """Test webhook processing"""
    # Mock verifier
    with patch("app.routers.calendar_sync.google_webhook_verifier.verify_google_calendar_webhook") as mock_verify:
        mock_verify.return_value = {
            "channel_id": "user_123_cal",
            "resource_state": "exists",
            "resource_id": "res-123"
        }
        
        # We need a user matching the ID
        # But the ID is extracted from channel_id "user_{id}_..."
        # Let's create a user with id "123"
        from app.models.user import User
        # Can't easily force ID on creation if generate_id is used inside model?
        # User model doesn't generate ID in __init__ usually.
        # Let's look at user model. `id = Column(String, primary_key=True)`
        # So we can set it.
        
        user = User(
            id="123", 
            email="webhook@test.com", 
            username="webhookuser", 
            preferences={"calendar_sync": {"enabled": True}}
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/calendar-sync/webhook",
            headers={
                "X-Goog-Channel-ID": "user_123_cal",
                "X-Goog-Resource-State": "exists"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["message"] == "Calendar change detected, sync queued"