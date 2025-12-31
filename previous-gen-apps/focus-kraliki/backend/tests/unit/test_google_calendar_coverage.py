"""
Targeted tests to improve coverage for Google Calendar Service
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.services.google_calendar import GoogleCalendarService

@pytest.fixture
def mock_google_service():
    """Mock Google Calendar API service"""
    with patch("app.services.google_calendar.build") as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        yield mock_service

def test_google_calendar_service_init(mock_google_service):
    """Test service initialization"""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GOOGLE_OAUTH_CLIENT_ID = "cid"
        mock_settings.GOOGLE_OAUTH_CLIENT_SECRET = "secret"
        
        service = GoogleCalendarService(oauth_token="token", refresh_token="refresh")
        assert service is not None

@pytest.mark.asyncio
async def test_sync_events_logic(mock_google_service):
    """Test sync_events logic and _google_to_focus_event"""
    with patch("app.core.config.settings"):
        service = GoogleCalendarService(oauth_token="token")
        
        # Mock API response
        mock_events = [
            {
                "id": "gevent1",
                "summary": "Meeting",
                "description": "Desc",
                "start": {"dateTime": "2025-12-26T10:00:00Z"},
                "end": {"dateTime": "2025-12-26T11:00:00Z"},
                "location": "Office",
                "attendees": [{"email": "a@b.com"}]
            }
        ]
        mock_google_service.events().list().execute.return_value = {"items": mock_events}
        
        results = await service.sync_events(user_id="user1")
        
        assert len(results) == 1
        assert results[0]["title"] == "Meeting"
        assert results[0]["google_event_id"] == "gevent1"
        assert results[0]["attendees"] == ["a@b.com"]

@pytest.mark.asyncio
async def test_create_event_logic(mock_google_service):
    """Test create_event logic"""
    with patch("app.core.config.settings"):
        service = GoogleCalendarService(oauth_token="token")
        
        mock_google_service.events().insert().execute.return_value = {"id": "new_id"}
        
        event_id = await service.create_event(
            title="New Event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            attendees=["test@example.com"]
        )
        
        assert event_id == "new_id"
        mock_google_service.events().insert.assert_called()

@pytest.mark.asyncio
async def test_update_event_logic(mock_google_service):
    """Test update_event logic"""
    with patch("app.core.config.settings"):
        service = GoogleCalendarService(oauth_token="token")
        
        # Mock get then update
        mock_google_service.events().get().execute.return_value = {"id": "eid", "summary": "Old"}
        mock_google_service.events().update().execute.return_value = {"id": "eid", "summary": "New"}
        
        success = await service.update_event(
            google_event_id="eid",
            title="New Title",
            description="New Desc"
        )
        
        assert success is True
        mock_google_service.events().update.assert_called()

@pytest.mark.asyncio
async def test_delete_event_logic(mock_google_service):
    """Test delete_event logic"""
    with patch("app.core.config.settings"):
        service = GoogleCalendarService(oauth_token="token")
        
        success = await service.delete_event(google_event_id="eid")
        
        assert success is True
        mock_google_service.events().delete.assert_called()

@pytest.mark.asyncio
async def test_sync_task_deadline_logic(mock_google_service):
    """Test sync_task_deadline logic"""
    with patch("app.core.config.settings"):
        service = GoogleCalendarService(oauth_token="token")
        
        mock_google_service.events().insert().execute.return_value = {"id": "task_eid"}
        
        event_id = await service.sync_task_deadline(
            task_id="t1",
            task_title="Finish Report",
            due_date=datetime.now()
        )
        
        assert event_id == "task_eid"
