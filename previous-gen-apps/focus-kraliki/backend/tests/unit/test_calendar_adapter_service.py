"""
Comprehensive tests for Calendar Adapter Service to improve coverage
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.calendar_adapter import (
    get_calendar_service,
    ping_calendar,
    create_calendar_event,
    CalendarNotConfigured,
)


class TestGetCalendarService:
    """Test get_calendar_service function"""

    def test_get_calendar_service_disabled(self):
        """Test when calendar integration is disabled"""
        with patch(
            "app.services.calendar_adapter.settings",
            MagicMock(ENABLE_CALENDAR_INTEGRATION=False),
        ):
            with pytest.raises(CalendarNotConfigured) as exc_info:
                get_calendar_service()
            assert "disabled" in str(exc_info.value)

    @patch("app.services.calendar_adapter.GoogleCalendarService", None)
    def test_get_calendar_service_tools_unavailable(self):
        """Test when tools-core is not available"""
        with patch(
            "app.services.calendar_adapter.settings",
            MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
        ):
            with pytest.raises(CalendarNotConfigured) as exc_info:
                get_calendar_service()
            assert "not available" in str(exc_info.value)

    @patch("app.services.calendar_adapter.GoogleCalendarService")
    @patch("app.services.calendar_adapter.CalendarEvent")
    def test_get_calendar_service_success(self, mock_event, mock_service):
        """Test successful service creation"""
        mock_service.return_value = MagicMock()

        with patch(
            "app.services.calendar_adapter.settings",
            MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
        ):
            result = get_calendar_service()
            assert result is not None


class TestPingCalendar:
    """Test ping_calendar function"""

    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=False),
    )
    async def test_ping_calendar_disabled(self):
        """Test ping when calendar integration is disabled"""
        try:
            result = await ping_calendar()
            assert result is False
        except CalendarNotConfigured:
            pass

    @patch("app.services.calendar_adapter.GoogleCalendarService", None)
    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
    )
    async def test_ping_calendar_unavailable(self):
        """Test ping when tools-core is unavailable"""
        try:
            result = await ping_calendar()
            assert result is False
        except CalendarNotConfigured:
            pass

    @patch("app.services.calendar_adapter.GoogleCalendarService")
    @patch("app.services.calendar_adapter.CalendarEvent")
    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
    )
    async def test_ping_calendar_success(self, mock_event, mock_service):
        """Test successful ping"""
        result = await ping_calendar()
        assert result is True


class TestCreateCalendarEvent:
    """Test create_calendar_event function"""

    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=False),
    )
    async def test_create_calendar_event_disabled(self):
        """Test when calendar integration is disabled"""
        with pytest.raises(CalendarNotConfigured):
            await create_calendar_event(
                title="Test Event",
                start_iso="2025-12-26T10:00:00Z",
                end_iso="2025-12-26T11:00:00Z",
            )

    @patch("app.services.calendar_adapter.GoogleCalendarService", None)
    @patch("app.services.calendar_adapter.CalendarEvent")
    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
    )
    async def test_create_calendar_event_tools_unavailable(self, mock_event):
        """Test when CalendarEvent model is unavailable"""
        with pytest.raises(CalendarNotConfigured) as exc_info:
            await create_calendar_event(
                title="Test Event",
                start_iso="2025-12-26T10:00:00Z",
                end_iso="2025-12-26T11:00:00Z",
            )
        assert "not available" in str(exc_info.value)

    @patch("app.services.calendar_adapter.GoogleCalendarService")
    @patch("app.services.calendar_adapter.CalendarEvent")
    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
    )
    async def test_create_calendar_event_success(self, mock_event, mock_service):
        """Test successful event creation"""
        # Mock service
        mock_svc_instance = MagicMock()
        mock_svc_instance.create_event = AsyncMock(
            return_value=MagicMock(id="event123")
        )
        mock_service.return_value = mock_svc_instance

        # Mock CalendarEvent
        mock_event_instance = MagicMock()
        mock_event_instance.id = "event123"
        mock_event.return_value = mock_event_instance

        result = await create_calendar_event(
            title="Test Event",
            start_iso="2025-12-26T10:00:00Z",
            end_iso="2025-12-26T11:00:00Z",
        )

        assert result == "event123"
        mock_event.assert_called_once()
        mock_service.assert_called_once()

    @patch("app.services.calendar_adapter.GoogleCalendarService")
    @patch("app.services.calendar_adapter.CalendarEvent")
    @patch(
        "app.services.calendar_adapter.settings",
        MagicMock(ENABLE_CALENDAR_INTEGRATION=True),
    )
    async def test_create_calendar_event_with_custom_calendar(
        self, mock_event, mock_service
    ):
        """Test event creation with custom calendar ID"""
        # Mock service
        mock_svc_instance = MagicMock()
        mock_svc_instance.create_event = AsyncMock(
            return_value=MagicMock(id="event456")
        )
        mock_service.return_value = mock_svc_instance

        # Mock CalendarEvent
        mock_event_instance = MagicMock()
        mock_event_instance.id = "event456"
        mock_event.return_value = mock_event_instance

        result = await create_calendar_event(
            title="Test Event",
            start_iso="2025-12-26T10:00:00Z",
            end_iso="2025-12-26T11:00:00Z",
            calendar_id="custom_calendar",
        )

        assert result == "event456"
        call_kwargs = mock_event.call_args[1]
        assert call_kwargs["calendar_id"] == "custom_calendar"
