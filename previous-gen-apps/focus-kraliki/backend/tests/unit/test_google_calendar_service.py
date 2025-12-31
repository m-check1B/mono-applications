"""
Comprehensive tests for GoogleCalendarService to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

from app.services.google_calendar import GoogleCalendarService


@pytest.fixture
def mock_settings():
    """Mock settings"""
    with patch("app.core.config.settings") as mock:
        mock.GOOGLE_OAUTH_CLIENT_ID = "test_client_id"
        mock.GOOGLE_OAUTH_CLIENT_SECRET = "test_secret"
        yield mock


@pytest.fixture
def mock_creds():
    """Mock Google credentials"""
    with patch("app.services.google_calendar.Credentials") as mock:
        creds = MagicMock()
        mock.return_value = creds
        yield creds


@pytest.fixture
def mock_google_service():
    """Mock Google Calendar API service"""
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_service.events.return_value = mock_events
    yield mock_service, mock_events


class TestGoogleCalendarServiceInit:
    """Test service initialization"""

    def test_init_with_oauth_token_only(self, mock_settings):
        """Test initialization with only oauth token"""
        with patch("app.services.google_calendar.build") as mock_build:
            service = GoogleCalendarService(oauth_token="test_token")
            assert service is not None
            mock_build.assert_called_once()

    def test_init_with_oauth_and_refresh_token(self, mock_settings):
        """Test initialization with oauth and refresh tokens"""
        with patch("app.services.google_calendar.build") as mock_build:
            service = GoogleCalendarService(
                oauth_token="test_token", refresh_token="test_refresh"
            )
            assert service is not None
            mock_build.assert_called_once()


class TestGoogleToFocusEvent:
    """Test _google_to_focus_event method"""

    @pytest.fixture
    def service(self, mock_settings):
        """Create service instance"""
        with patch("app.services.google_calendar.build"):
            return GoogleCalendarService(oauth_token="test_token")

    def test_convert_event_with_datetime(self, service):
        """Test converting event with datetime fields"""
        google_event = {
            "id": "gevent1",
            "summary": "Test Meeting",
            "description": "Test description",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
            "location": "Office",
            "attendees": [
                {"email": "user1@example.com"},
                {"email": "user2@example.com"},
            ],
            "colorId": "1",
        }

        focus_event = service._google_to_focus_event(
            google_event, user_id="user123", calendar_id="primary"
        )

        assert focus_event["title"] == "Test Meeting"
        assert focus_event["description"] == "Test description"
        assert focus_event["location"] == "Office"
        assert focus_event["google_event_id"] == "gevent1"
        assert focus_event["google_calendar_id"] == "primary"
        assert focus_event["user_id"] == "user123"
        assert focus_event["all_day"] is False
        assert len(focus_event["attendees"]) == 2
        assert focus_event["color"] == "1"

    def test_convert_event_with_date_all_day(self, service):
        """Test converting all-day event with date fields"""
        google_event = {
            "id": "gevent2",
            "summary": "All Day Event",
            "start": {"date": "2025-12-26"},
            "end": {"date": "2025-12-27"},
        }

        focus_event = service._google_to_focus_event(
            google_event, user_id="user123", calendar_id="primary"
        )

        assert focus_event["title"] == "All Day Event"
        assert focus_event["all_day"] is True

    def test_convert_event_without_optional_fields(self, service):
        """Test converting event with minimal fields"""
        google_event = {
            "id": "gevent3",
            "summary": "Minimal Event",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
        }

        focus_event = service._google_to_focus_event(
            google_event, user_id="user123", calendar_id="primary"
        )

        assert focus_event["title"] == "Minimal Event"
        assert focus_event["description"] == ""
        assert focus_event["location"] is None
        assert focus_event["attendees"] is None
        assert focus_event["color"] is None

    def test_convert_event_empty_summary(self, service):
        """Test converting event with no summary"""
        google_event = {
            "id": "gevent4",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
        }

        focus_event = service._google_to_focus_event(
            google_event, user_id="user123", calendar_id="primary"
        )

        assert focus_event["title"] == "Untitled Event"

    def test_convert_event_with_empty_attendees(self, service):
        """Test converting event with empty attendees list"""
        google_event = {
            "id": "gevent5",
            "summary": "No Attendees",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
            "attendees": [],
        }

        focus_event = service._google_to_focus_event(
            google_event, user_id="user123", calendar_id="primary"
        )

        assert focus_event["attendees"] is None


class TestSyncEvents:
    """Test sync_events method"""

    @pytest.fixture
    def service(self, mock_settings, mock_google_service):
        """Create service with mocked API"""
        mock_service, mock_events = mock_google_service
        with patch("app.services.google_calendar.build", return_value=mock_service):
            service = GoogleCalendarService(oauth_token="test_token")
            return service, mock_service, mock_events

    @pytest.mark.asyncio
    async def test_sync_events_default_params(self, service):
        """Test sync_events with default parameters"""
        service_obj, mock_service, mock_events = service

        mock_list = MagicMock()
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "gevent1",
                    "summary": "Meeting",
                    "start": {"dateTime": "2025-12-26T10:00:00Z"},
                    "end": {"dateTime": "2025-12-26T11:00:00Z"},
                }
            ]
        }
        mock_events.list.return_value = mock_list

        events = await service_obj.sync_events(user_id="user123")

        assert len(events) == 1
        assert events[0]["title"] == "Meeting"
        mock_events.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_events_with_custom_time_range(self, service):
        """Test sync_events with custom time range"""
        service_obj, mock_service, mock_events = service

        time_min = datetime(2025, 12, 1)
        time_max = datetime(2025, 12, 31)

        mock_list = MagicMock()
        mock_list.execute.return_value = {"items": []}
        mock_events.list.return_value = mock_list

        await service_obj.sync_events(
            user_id="user123", time_min=time_min, time_max=time_max, max_results=50
        )

        call_args = mock_events.list.call_args
        assert call_args[1]["maxResults"] == 50

    @pytest.mark.asyncio
    async def test_sync_events_empty_list(self, service):
        """Test sync_events when no events returned"""
        service_obj, mock_service, mock_events = service

        mock_list = MagicMock()
        mock_list.execute.return_value = {"items": []}
        mock_events.list.return_value = mock_list

        events = await service_obj.sync_events(user_id="user123")

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_sync_events_http_error(self, service):
        """Test sync_events with HTTP error"""
        service_obj, mock_service, mock_events = service

        mock_list = MagicMock()
        mock_list.execute.side_effect = HttpError(
            MagicMock(status=403), b'{"error": "Forbidden"}'
        )
        mock_events.list.return_value = mock_list

        with pytest.raises(HttpError):
            await service_obj.sync_events(user_id="user123")


class TestCreateEvent:
    """Test create_event method"""

    @pytest.fixture
    def service(self, mock_settings, mock_google_service):
        """Create service with mocked API"""
        mock_service, mock_events = mock_google_service
        with patch("app.services.google_calendar.build", return_value=mock_service):
            service = GoogleCalendarService(oauth_token="test_token")
            return service, mock_events

    @pytest.mark.asyncio
    async def test_create_event_basic(self, service):
        """Test creating a basic event"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "new_event_id"}
        mock_events.insert.return_value = mock_insert

        start_time = datetime(2025, 12, 26, 10, 0)
        end_time = datetime(2025, 12, 26, 11, 0)

        event_id = await service_obj.create_event(
            title="Test Event", start_time=start_time, end_time=end_time
        )

        assert event_id == "new_event_id"
        mock_events.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_with_all_fields(self, service):
        """Test creating event with all optional fields"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "full_event_id"}
        mock_events.insert.return_value = mock_insert

        start_time = datetime(2025, 12, 26, 10, 0)
        end_time = datetime(2025, 12, 26, 11, 0)

        event_id = await service_obj.create_event(
            title="Full Event",
            start_time=start_time,
            end_time=end_time,
            description="Test description",
            location="Test Location",
            attendees=["user1@example.com", "user2@example.com"],
        )

        assert event_id == "full_event_id"
        call_kwargs = mock_events.insert.call_args[1]
        assert len(call_kwargs["body"]["attendees"]) == 2

    @pytest.mark.asyncio
    async def test_create_event_http_error(self, service):
        """Test create_event with HTTP error"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.side_effect = HttpError(
            MagicMock(status=400), b'{"error": "Bad Request"}'
        )
        mock_events.insert.return_value = mock_insert

        with pytest.raises(HttpError):
            await service_obj.create_event(
                title="Error Event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            )


class TestUpdateEvent:
    """Test update_event method"""

    @pytest.fixture
    def service(self, mock_settings, mock_google_service):
        """Create service with mocked API"""
        mock_service, mock_events = mock_google_service
        with patch("app.services.google_calendar.build", return_value=mock_service):
            service = GoogleCalendarService(oauth_token="test_token")
            return service, mock_events

    @pytest.mark.asyncio
    async def test_update_event_title(self, service):
        """Test updating event title"""
        service_obj, mock_events = service

        mock_get = MagicMock()
        mock_get.execute.return_value = {
            "id": "event1",
            "summary": "Old Title",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
        }
        mock_events.get.return_value = mock_get

        mock_update = MagicMock()
        mock_update.execute.return_value = {"id": "event1", "summary": "New Title"}
        mock_events.update.return_value = mock_update

        success = await service_obj.update_event(
            google_event_id="event1", title="New Title"
        )

        assert success is True
        mock_events.get.assert_called_once()
        mock_events.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_event_all_fields(self, service):
        """Test updating all event fields"""
        service_obj, mock_events = service

        mock_get = MagicMock()
        mock_get.execute.return_value = {
            "id": "event1",
            "summary": "Old Title",
            "start": {"dateTime": "2025-12-26T10:00:00Z"},
            "end": {"dateTime": "2025-12-26T11:00:00Z"},
        }
        mock_events.get.return_value = mock_get

        mock_update = MagicMock()
        mock_update.execute.return_value = {"id": "event1"}
        mock_events.update.return_value = mock_update

        new_start = datetime(2025, 12, 27, 9, 0)
        new_end = datetime(2025, 12, 27, 10, 0)

        success = await service_obj.update_event(
            google_event_id="event1",
            title="New Title",
            description="New Description",
            location="New Location",
            start_time=new_start,
            end_time=new_end,
        )

        assert success is True

    @pytest.mark.asyncio
    async def test_update_event_http_error(self, service):
        """Test update_event with HTTP error"""
        service_obj, mock_events = service

        mock_get = MagicMock()
        mock_get.execute.side_effect = HttpError(
            MagicMock(status=404), b'{"error": "Not Found"}'
        )
        mock_events.get.return_value = mock_get

        success = await service_obj.update_event(
            google_event_id="nonexistent", title="New Title"
        )

        assert success is False


class TestDeleteEvent:
    """Test delete_event method"""

    @pytest.fixture
    def service(self, mock_settings, mock_google_service):
        """Create service with mocked API"""
        mock_service, mock_events = mock_google_service
        with patch("app.services.google_calendar.build", return_value=mock_service):
            service = GoogleCalendarService(oauth_token="test_token")
            return service, mock_events

    @pytest.mark.asyncio
    async def test_delete_event_success(self, service):
        """Test successful event deletion"""
        service_obj, mock_events = service

        mock_delete = MagicMock()
        mock_delete.execute.return_value = None
        mock_events.delete.return_value = mock_delete

        success = await service_obj.delete_event(google_event_id="event1")

        assert success is True
        mock_events.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_event_http_error(self, service):
        """Test delete_event with HTTP error"""
        service_obj, mock_events = service

        mock_delete = MagicMock()
        mock_delete.execute.side_effect = HttpError(
            MagicMock(status=404), b'{"error": "Not Found"}'
        )
        mock_events.delete.return_value = mock_delete

        success = await service_obj.delete_event(google_event_id="nonexistent")

        assert success is False


class TestSyncTaskDeadline:
    """Test sync_task_deadline method"""

    @pytest.fixture
    def service(self, mock_settings, mock_google_service):
        """Create service with mocked API"""
        mock_service, mock_events = mock_google_service
        with patch("app.services.google_calendar.build", return_value=mock_service):
            service = GoogleCalendarService(oauth_token="test_token")
            return service, mock_events

    @pytest.mark.asyncio
    async def test_sync_task_deadline_basic(self, service):
        """Test syncing task deadline to calendar"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "task_event_id"}
        mock_events.insert.return_value = mock_insert

        due_date = datetime(2025, 12, 26, 10, 0)

        event_id = await service_obj.sync_task_deadline(
            task_id="task123", task_title="Finish Report", due_date=due_date
        )

        assert event_id == "task_event_id"
        call_kwargs = mock_events.insert.call_args[1]
        assert "Finish Report" in call_kwargs["body"]["summary"]

    @pytest.mark.asyncio
    async def test_sync_task_deadline_with_description(self, service):
        """Test syncing task deadline with description"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "task_event_id"}
        mock_events.insert.return_value = mock_insert

        due_date = datetime(2025, 12, 26, 10, 0)

        event_id = await service_obj.sync_task_deadline(
            task_id="task123",
            task_title="Finish Report",
            due_date=due_date,
            description="Complete all sections",
            duration_minutes=30,
        )

        assert event_id == "task_event_id"
        call_kwargs = mock_events.insert.call_args[1]
        description = call_kwargs["body"]["description"]
        assert "Finish Report" in description
        assert "Complete all sections" in description
        assert "task123" in description

    @pytest.mark.asyncio
    async def test_sync_task_deadline_custom_duration(self, service):
        """Test syncing task deadline with custom duration"""
        service_obj, mock_events = service

        mock_insert = MagicMock()
        mock_insert.execute.return_value = {"id": "task_event_id"}
        mock_events.insert.return_value = mock_insert

        due_date = datetime(2025, 12, 26, 10, 0)

        await service_obj.sync_task_deadline(
            task_id="task123",
            task_title="Long Task",
            due_date=due_date,
            duration_minutes=120,
        )

        call_kwargs = mock_events.insert.call_args[1]
        end_time = datetime.fromisoformat(call_kwargs["body"]["end"]["dateTime"])
        start_time = datetime.fromisoformat(call_kwargs["body"]["start"]["dateTime"])
        duration = (end_time - start_time).total_seconds() / 60
        assert duration == 120
