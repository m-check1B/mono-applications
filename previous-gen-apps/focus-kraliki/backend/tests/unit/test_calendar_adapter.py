"""
Unit tests for Calendar Adapter Service
Tests calendar service retrieval, ping, and event creation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.calendar_adapter import (
    get_calendar_service,
    ping_calendar,
    create_calendar_event,
    CalendarNotConfigured,
)


class TestGetCalendarService:
    """Tests for get_calendar_service function"""

    def test_get_service_when_enabled(self):
        """Get service when integration is enabled"""
        with patch(
            "app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION", True
        ):
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=Mock(),
            ):
                service = get_calendar_service()
                assert service is not None

    def test_get_service_raises_when_disabled(self):
        """Get service raises when integration disabled"""
        with patch(
            "app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION", False
        ):
            with pytest.raises(
                CalendarNotConfigured, match="Calendar integration disabled"
            ):
                get_calendar_service()

    def test_get_service_raises_when_tools_core_missing(self):
        """Get service raises when tools-core not available"""
        with patch(
            "app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION", True
        ):
            with patch("app.services.calendar_adapter.GoogleCalendarService", None):
                with pytest.raises(
                    CalendarNotConfigured, match="tools-core not available"
                ):
                    get_calendar_service()


class TestPingCalendar:
    """Tests for ping_calendar function"""

    @pytest.mark.asyncio
    async def test_ping_returns_true_when_configured(self):
        """Ping returns True when calendar is configured"""
        with patch(
            "app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION", True
        ):
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=Mock(),
            ):
                result = await ping_calendar()
                assert result is True

    @pytest.mark.asyncio
    async def test_ping_raises_when_disabled(self):
        """Ping raises CalendarNotConfigured when disabled"""
        with patch(
            "app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION", False
        ):
            with pytest.raises(CalendarNotConfigured):
                await ping_calendar()


class TestCreateCalendarEvent:
    """Tests for create_calendar_event function"""

    @pytest.mark.asyncio
    async def test_create_event_success(self):
        """Create calendar event successfully"""
        mock_service = Mock()
        mock_event = Mock()
        mock_event.id = "event-123"
        mock_service.create_event = AsyncMock(return_value=mock_event)

        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=mock_service,
            ):
                with patch(
                    "app.services.calendar_adapter.CalendarEvent"
                ) as mock_event_class:
                    mock_event_class.return_value = mock_event

                    result = await create_calendar_event(
                        title="Test Event",
                        start_iso="2024-01-01T10:00:00Z",
                        end_iso="2024-01-01T11:00:00Z",
                    )

                    assert result == "event-123"
                    mock_event_class.assert_called_once()
                    mock_service.create_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_event_with_custom_calendar_id(self):
        """Create event with custom calendar ID"""
        mock_service = Mock()
        mock_event = Mock()
        mock_event.id = "event-456"
        mock_service.create_event = AsyncMock(return_value=mock_event)

        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=mock_service,
            ):
                with patch(
                    "app.services.calendar_adapter.CalendarEvent"
                ) as mock_event_class:
                    mock_event_class.return_value = mock_event

                    await create_calendar_event(
                        title="Test Event",
                        start_iso="2024-01-01T10:00:00Z",
                        end_iso="2024-01-01T11:00:00Z",
                        calendar_id="custom-calendar",
                    )

                    call_args = mock_event_class.call_args
                    assert call_args[1]["calendar_id"] == "custom-calendar"

    @pytest.mark.asyncio
    async def test_create_event_uses_primary_calendar_by_default(self):
        """Create event uses 'primary' calendar by default"""
        mock_service = Mock()
        mock_event = Mock()
        mock_event.id = "event-789"
        mock_service.create_event = AsyncMock(return_value=mock_event)

        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=mock_service,
            ):
                with patch(
                    "app.services.calendar_adapter.CalendarEvent"
                ) as mock_event_class:
                    mock_event_class.return_value = mock_event

                    await create_calendar_event(
                        title="Test Event",
                        start_iso="2024-01-01T10:00:00Z",
                        end_iso="2024-01-01T11:00:00Z",
                        calendar_id=None,
                    )

                    call_args = mock_event_class.call_args
                    assert call_args[1]["calendar_id"] == "primary"

    @pytest.mark.asyncio
    async def test_create_event_raises_when_disabled(self):
        """Create event raises when integration disabled"""
        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = False
            with pytest.raises(CalendarNotConfigured):
                await create_calendar_event(
                    title="Test Event",
                    start_iso="2024-01-01T10:00:00Z",
                    end_iso="2024-01-01T11:00:00Z",
                )

    @pytest.mark.asyncio
    async def test_create_event_raises_when_tools_core_missing(self):
        """Create event raises when tools-core not available"""
        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch("app.services.calendar_adapter.GoogleCalendarService", None):
                with pytest.raises(CalendarNotConfigured):
                    await create_calendar_event(
                        title="Test Event",
                        start_iso="2024-01-01T10:00:00Z",
                        end_iso="2024-01-01T11:00:00Z",
                    )

    @pytest.mark.asyncio
    async def test_create_event_raises_when_event_model_missing(self):
        """Create event raises when CalendarEvent model not available"""
        mock_service = Mock()

        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=mock_service,
            ):
                with patch("app.services.calendar_adapter.CalendarEvent", None):
                    with pytest.raises(
                        CalendarNotConfigured, match="CalendarEvent model not available"
                    ):
                        await create_calendar_event(
                            title="Test Event",
                            start_iso="2024-01-01T10:00:00Z",
                            end_iso="2024-01-01T11:00:00Z",
                        )


class TestCalendarAdapterIntegration:
    """Integration tests for calendar adapter workflows"""

    @pytest.mark.asyncio
    async def test_ping_then_create_workflow(self):
        """Test ping then create event workflow"""
        mock_service = Mock()
        mock_event = Mock()
        mock_event.id = "event-integration"
        mock_service.create_event = AsyncMock(return_value=mock_event)

        with patch("app.services.calendar_adapter.settings") as mock_settings:
            mock_settings.ENABLE_CALENDAR_INTEGRATION = True
            with patch(
                "app.services.calendar_adapter.GoogleCalendarService",
                return_value=mock_service,
            ):
                with patch(
                    "app.services.calendar_adapter.CalendarEvent", return_value=mock_event
                ):
                    is_ready = await ping_calendar()
                    assert is_ready is True

                    event_id = await create_calendar_event(
                        title="Integration Test",
                        start_iso="2024-01-01T10:00:00Z",
                        end_iso="2024-01-01T11:00:00Z",
                    )
                    assert event_id == "event-integration"
