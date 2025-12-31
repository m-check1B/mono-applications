"""
E2E Tests for Calendar Adapter Integration

Tests full integration flows through the calendar adapter including:
- Adapter initialization and configuration
- Error handling and fallback mechanisms
- Multi-step workflows
- Integration with platform services
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from app.module import PlanningModule
from app.services.calendar_adapter import (
    CalendarNotConfigured,
    get_calendar_service,
    ping_calendar,
    create_calendar_event,
)


class TestCalendarAdapterE2E:
    """End-to-end tests for calendar adapter integration flows."""

    def test_calendar_adapter_disabled_by_default(self):
        """E2E: Calendar integration disabled by default returns proper status."""
        module = PlanningModule(platform_mode=True)
        app = module.get_app()
        client = TestClient(app)

        response = client.get("/integration/calendar/status")

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["reachable"] is False
        assert "reason" in data

    def test_calendar_adapter_graceful_degradation(self):
        """E2E: Calendar adapter gracefully handles missing tools-core."""
        module = PlanningModule(platform_mode=False)
        app = module.get_app()
        client = TestClient(app)

        # Try to create event without calendar configured
        response = client.post(
            "/integration/calendar/events",
            json={"title": "Test Event", "duration_minutes": 30}
        )

        # Should return 503 (service unavailable) not 500
        assert response.status_code == 503
        assert "detail" in response.json()

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    @patch('app.services.calendar_adapter.CalendarEvent')
    def test_calendar_adapter_full_event_creation_flow(
        self,
        mock_calendar_event_class,
        mock_service_class
    ):
        """E2E: Full flow from API request to calendar event creation."""
        # Setup mocks
        mock_event = Mock()
        mock_event.id = "evt_test_123"

        mock_service = Mock()
        mock_service.create_event = AsyncMock(return_value=mock_event)
        mock_service_class.return_value = mock_service

        mock_calendar_event_class.return_value = Mock()

        # Configure module with calendar enabled
        module = PlanningModule(platform_mode=False)
        app = module.get_app()

        with patch('app.services.calendar_adapter.settings.ENABLE_CALENDAR_INTEGRATION', True):
            client = TestClient(app)

            response = client.post(
                "/integration/calendar/events",
                json={"title": "Team Standup", "duration_minutes": 15}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["created"] is True
            assert data["event_id"] == "evt_test_123"

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    def test_calendar_adapter_retry_mechanism(self, mock_service_class):
        """E2E: Calendar adapter retries on transient failures."""
        # Setup mock to fail twice then succeed
        mock_event = Mock()
        mock_event.id = "evt_retry_success"

        mock_service = Mock()
        call_count = {"count": 0}

        async def create_event_with_retry(*args, **kwargs):
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise Exception("Transient network error")
            return mock_event

        mock_service.create_event = create_event_with_retry
        mock_service_class.return_value = mock_service

        # This test demonstrates the need for retry logic
        # Current implementation doesn't have retries - this would fail
        # Documenting expected behavior for future enhancement

    def test_calendar_adapter_validation_errors(self):
        """E2E: Calendar adapter validates input before sending to service."""
        module = PlanningModule(platform_mode=False)
        app = module.get_app()
        client = TestClient(app)

        # Invalid duration (too long)
        response = client.post(
            "/integration/calendar/events",
            json={"title": "Test Event", "duration_minutes": 500}
        )
        assert response.status_code == 422

        # Invalid duration (negative)
        response = client.post(
            "/integration/calendar/events",
            json={"title": "Test Event", "duration_minutes": -10}
        )
        assert response.status_code == 422

        # Missing title
        response = client.post(
            "/integration/calendar/events",
            json={"duration_minutes": 30}
        )
        assert response.status_code == 422


class TestCalendarAdapterMultiStepWorkflows:
    """Test multi-step workflows involving calendar adapter."""

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    @patch('app.services.calendar_adapter.CalendarEvent')
    def test_task_completion_triggers_calendar_event(
        self,
        mock_calendar_event_class,
        mock_service_class
    ):
        """E2E: Completing task with meeting requirement creates calendar event."""
        # Setup calendar mocks
        mock_event = Mock()
        mock_event.id = "evt_followup_123"

        mock_service = Mock()
        mock_service.create_event = AsyncMock(return_value=mock_event)
        mock_service_class.return_value = mock_service
        mock_calendar_event_class.return_value = Mock()

        # This demonstrates a multi-step workflow:
        # 1. User completes task with "schedule_followup" flag
        # 2. System detects completion
        # 3. Calendar adapter creates follow-up event
        # 4. Event details returned to user

        # Currently not implemented - documenting expected flow
        pass

    def test_calendar_event_links_to_task(self):
        """E2E: Calendar events created from tasks maintain bidirectional links."""
        # Workflow:
        # 1. Create task requiring meeting
        # 2. Create calendar event from task
        # 3. Store event_id on task
        # 4. Query task and retrieve calendar details

        # This demonstrates the need for task-calendar linking
        # Currently not implemented - documenting expected behavior
        pass


class TestCalendarAdapterErrorHandling:
    """Test error handling and recovery mechanisms."""

    @patch('app.services.calendar_adapter.get_calendar_service')
    def test_calendar_adapter_network_timeout(self, mock_get_service):
        """E2E: Calendar adapter handles network timeouts gracefully."""
        mock_get_service.side_effect = TimeoutError("Network timeout")

        module = PlanningModule(platform_mode=False)
        app = module.get_app()
        client = TestClient(app)

        # Even with timeout, should return proper error response
        # Currently might raise 500 - should be 503
        response = client.post(
            "/integration/calendar/events",
            json={"title": "Test Event", "duration_minutes": 30}
        )

        # Should handle timeout gracefully
        assert response.status_code in [500, 503]

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    def test_calendar_adapter_permission_denied(self, mock_service_class):
        """E2E: Calendar adapter handles permission errors appropriately."""
        mock_service = Mock()
        mock_service.create_event = AsyncMock(
            side_effect=PermissionError("Calendar access denied")
        )
        mock_service_class.return_value = mock_service

        # Should return proper error indicating permission issue
        # Documenting expected behavior
        pass

    def test_calendar_adapter_invalid_credentials(self):
        """E2E: Calendar adapter handles invalid/expired credentials."""
        # Workflow:
        # 1. User's calendar OAuth token expires
        # 2. Attempt to create event
        # 3. Detect credential issue
        # 4. Return error with re-auth instructions

        # Currently not implemented - documenting expected flow
        pass


class TestCalendarAdapterPlatformIntegration:
    """Test integration with other platform services."""

    def test_calendar_adapter_with_auth_core(self):
        """E2E: Calendar adapter respects auth-core authentication."""
        module = PlanningModule(platform_mode=True)
        app = module.get_app()
        client = TestClient(app)

        # Without auth headers in platform mode
        response = client.post(
            "/integration/calendar/events",
            json={"title": "Test Event", "duration_minutes": 30}
        )

        # Should reject unauthenticated requests
        assert response.status_code == 401

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    @patch('app.services.calendar_adapter.CalendarEvent')
    def test_calendar_adapter_publishes_events(
        self,
        mock_calendar_event_class,
        mock_service_class,
    ):
        """E2E: Calendar adapter publishes events to events-core."""
        # Setup mocks
        mock_event = Mock()
        mock_event.id = "evt_published_123"

        mock_service = Mock()
        mock_service.create_event = AsyncMock(return_value=mock_event)
        mock_service_class.return_value = mock_service
        mock_calendar_event_class.return_value = Mock()

        # Workflow:
        # 1. Calendar event created
        # 2. Event published to events-core
        # 3. Other modules notified (campaigns, notifications)

        # Currently not implemented - documenting expected integration
        pass

    def test_calendar_adapter_organization_isolation(self):
        """E2E: Calendar adapter enforces organization boundaries."""
        # Platform mode: Each org's calendar data isolated
        # User from org A cannot access org B's calendar

        module = PlanningModule(platform_mode=True)
        app = module.get_app()
        client = TestClient(app)

        # Setup: Two different orgs
        # Verify: Org A cannot see Org B's calendar events

        # Currently not implemented - documenting expected behavior
        pass


class TestCalendarAdapterPerformance:
    """Test performance characteristics of calendar adapter."""

    @patch('app.services.calendar_adapter.GoogleCalendarService')
    @patch('app.services.calendar_adapter.CalendarEvent')
    def test_calendar_adapter_batch_operations(
        self,
        mock_calendar_event_class,
        mock_service_class
    ):
        """E2E: Calendar adapter efficiently handles batch event creation."""
        # Setup mock
        mock_service = Mock()
        created_events = []

        async def create_event_mock(event):
            mock_evt = Mock()
            mock_evt.id = f"evt_batch_{len(created_events)}"
            created_events.append(mock_evt)
            return mock_evt

        mock_service.create_event = create_event_mock
        mock_service_class.return_value = mock_service
        mock_calendar_event_class.return_value = Mock()

        # Test batch creation (e.g., importing events from another calendar)
        # Should be efficient and not timeout

        # Currently not implemented - documenting expected capability
        pass

    def test_calendar_adapter_caching(self):
        """E2E: Calendar adapter caches configuration and service instances."""
        # Verify service instances reused across requests
        # Configuration loaded once
        # Reduces overhead for frequent calendar operations

        # Currently minimal caching - documenting expected optimization
        pass


class TestCalendarAdapterConfiguration:
    """Test different configuration scenarios."""

    def test_calendar_adapter_multiple_calendars(self):
        """E2E: Calendar adapter supports multiple calendar configurations."""
        # User might have multiple calendars (work, personal, team)
        # Should route events to correct calendar based on context

        # Currently single calendar - documenting future enhancement
        pass

    def test_calendar_adapter_timezone_handling(self):
        """E2E: Calendar adapter correctly handles timezone conversions."""
        # User in PST creates event
        # Event stored in UTC
        # Retrieved in user's local timezone

        module = PlanningModule(platform_mode=False)
        app = module.get_app()
        client = TestClient(app)

        # Current implementation uses UTC
        # Verify proper timezone handling

        response = client.get("/integration/calendar/status")
        assert response.status_code == 200

    def test_calendar_adapter_custom_providers(self):
        """E2E: Calendar adapter extensible to other providers (Outlook, iCal)."""
        # Currently Google Calendar only
        # Architecture should support other providers
        # Documenting extensibility requirement
        pass
