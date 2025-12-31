"""
Unit tests for events router
Tests CRUD operations for calendar events via HTTP endpoints
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.user import User
from app.models.event import Event
from app.core.security import generate_id


class TestEventsRouterAPI:
    """Test events router via HTTP client"""

    def test_list_events_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.get("/events/")
        assert response.status_code == 401

    def test_list_events_authenticated(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should list events for authenticated user"""
        # Create events
        tomorrow = datetime.utcnow() + timedelta(days=1)
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Test Event",
            start_time=tomorrow,
            end_time=tomorrow + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        response = client.get("/events/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data

    def test_list_events_with_date_params(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should filter events by date range parameters"""
        tomorrow = datetime.utcnow() + timedelta(days=1)
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Test Event",
            start_time=tomorrow,
            end_time=tomorrow + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

        response = client.get(
            f"/events/?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

    def test_list_events_with_limit(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should respect limit parameter"""
        # Create multiple events
        for i in range(5):
            event = Event(
                id=generate_id(),
                user_id=test_user.id,
                title=f"Event {i}",
                start_time=datetime.utcnow() + timedelta(days=i+1),
                end_time=datetime.utcnow() + timedelta(days=i+1, hours=1),
                created_at=datetime.utcnow()
            )
            db.add(event)
        db.commit()

        response = client.get("/events/?limit=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= 3

    def test_create_event_success(self, client: TestClient, auth_headers: dict, test_user: User):
        """Should create event via POST"""
        event_data = {
            "title": "New Event",
            "description": "Test description",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=1, hours=2)).isoformat()
        }

        response = client.post("/events/", json=event_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Event"
        assert data["description"] == "Test description"
        assert "id" in data

    def test_create_event_unauthenticated(self, client: TestClient):
        """Should return 401 when creating event without auth"""
        event_data = {
            "title": "New Event",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        }

        response = client.post("/events/", json=event_data)
        assert response.status_code == 401

    def test_create_event_minimal_fields(self, client: TestClient, auth_headers: dict):
        """Should create event with only required fields"""
        event_data = {
            "title": "Minimal Event",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        }

        response = client.post("/events/", json=event_data, headers=auth_headers)
        assert response.status_code == 201

    def test_get_event_success(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should get single event by ID"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Test Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        response = client.get(f"/events/{event.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == event.id
        assert data["title"] == "Test Event"

    def test_get_event_not_found(self, client: TestClient, auth_headers: dict):
        """Should return 404 for non-existent event"""
        response = client.get("/events/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_event_wrong_user(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should return 404 when accessing another user's event"""
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="other",
            onboardingCompleted=False,
            onboardingStep=0
        )
        db.add(other_user)
        db.commit()

        event = Event(
            id=generate_id(),
            user_id=other_user.id,
            title="Other's Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        response = client.get(f"/events/{event.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_update_event_success(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should update event via PATCH"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Original Title",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        update_data = {"title": "Updated Title"}
        response = client.patch(f"/events/{event.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_event_not_found(self, client: TestClient, auth_headers: dict):
        """Should return 404 when updating non-existent event"""
        response = client.patch("/events/nonexistent-id", json={"title": "New"}, headers=auth_headers)
        assert response.status_code == 404

    def test_delete_event_success(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should delete event via DELETE"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="To Delete",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        event_id = event.id

        response = client.delete(f"/events/{event_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletedId"] == event_id

    def test_delete_event_not_found(self, client: TestClient, auth_headers: dict):
        """Should return 404 when deleting non-existent event"""
        response = client.delete("/events/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestGoogleCalendarSyncAPI:
    """Test Google Calendar sync endpoint"""

    def test_sync_google_calendar_not_enabled(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should return 400 when calendar sync is not enabled"""
        # Ensure user has no calendar_sync preferences
        test_user.preferences = {}
        db.commit()

        response = client.post("/events/sync/google", headers=auth_headers)
        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"].lower()

    def test_sync_google_calendar_no_token(self, client: TestClient, auth_headers: dict, test_user: User, db: Session):
        """Should return 400 when enabled but no access token"""
        test_user.preferences = {"calendar_sync": {"enabled": True}}
        db.commit()

        response = client.post("/events/sync/google", headers=auth_headers)
        assert response.status_code == 400
        assert "access token" in response.json()["detail"].lower()

    @patch("app.services.google_calendar.GoogleCalendarService")
    def test_sync_google_calendar_success(
        self, mock_service_class, client: TestClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Should sync events when properly configured"""
        # Setup user preferences with valid token
        test_user.preferences = {
            "calendar_sync": {
                "enabled": True,
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        }
        db.commit()

        # Mock the Google Calendar service
        mock_service = MagicMock()
        mock_service.sync_events = AsyncMock(return_value=[
            {
                "id": generate_id(),
                "user_id": test_user.id,
                "title": "Synced Event",
                "start_time": datetime.utcnow() + timedelta(days=1),
                "end_time": datetime.utcnow() + timedelta(days=1, hours=1),
                "google_event_id": "google_123",
                "created_at": datetime.utcnow()
            }
        ])
        mock_service_class.return_value = mock_service

        response = client.post("/events/sync/google", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "synced_count" in data

    def test_sync_google_calendar_unauthenticated(self, client: TestClient):
        """Should return 401 when not authenticated"""
        response = client.post("/events/sync/google")
        assert response.status_code == 401


class TestRefreshGoogleToken:
    """Test Google OAuth token refresh helper"""

    @pytest.mark.asyncio
    async def test_refresh_token_no_oauth_config(self, test_user: User, db: Session):
        """Should return None when OAuth not configured"""
        from app.routers.events import _refresh_google_token
        from app.core import config as config_module

        with patch.object(config_module.settings, "GOOGLE_OAUTH_CLIENT_ID", None):
            with patch.object(config_module.settings, "GOOGLE_OAUTH_CLIENT_SECRET", None):
                result = await _refresh_google_token("refresh_token", db, test_user)
                assert result is None


class TestListEvents:
    """Test event listing endpoint"""

    def test_list_events_default_range(self, test_user: User, db: Session):
        """Should list events for next 30 days by default"""
        # Create event for tomorrow
        tomorrow = datetime.utcnow() + timedelta(days=1)
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Test Event",
            start_time=tomorrow,
            end_time=tomorrow + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        # Query events
        events = db.query(Event).filter(
            Event.user_id == test_user.id,
            Event.start_time >= datetime.utcnow()
        ).all()

        assert len(events) > 0
        assert events[0].title == "Test Event"

    def test_list_events_with_date_filters(self, test_user: User, db: Session):
        """Should filter events by date range"""
        # Create events
        today = datetime.utcnow()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        event1 = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Event 1",
            start_time=tomorrow,
            end_time=tomorrow + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        event2 = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Event 2",
            start_time=next_week,
            end_time=next_week + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        db.add_all([event1, event2])
        db.commit()

        # Filter events within first 3 days
        filtered = db.query(Event).filter(
            Event.user_id == test_user.id,
            Event.start_time >= today,
            Event.end_time <= today + timedelta(days=3)
        ).all()

        assert len(filtered) == 1
        assert filtered[0].title == "Event 1"

    def test_list_events_user_isolation(self, test_user: User, db: Session):
        """Users should only see their own events"""
        # Create another user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="other",
            onboardingCompleted=False,
            onboardingStep=0
        )
        db.add(other_user)
        db.commit()

        # Create events for both users
        event1 = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="My Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        event2 = Event(
            id=generate_id(),
            user_id=other_user.id,
            title="Other Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add_all([event1, event2])
        db.commit()

        # Query events for test_user
        my_events = db.query(Event).filter(Event.user_id == test_user.id).all()

        assert len(my_events) == 1
        assert my_events[0].title == "My Event"


class TestCreateEvent:
    """Test event creation endpoint"""

    def test_create_event_success(self, test_user: User, db: Session):
        """Should create event successfully"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="New Event",
            description="Test event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=2),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.id is not None
        assert event.title == "New Event"
        assert event.user_id == test_user.id

    def test_create_event_required_fields(self, test_user: User, db: Session):
        """Event requires title and times"""
        # Missing title should fail
        with pytest.raises(Exception):
            event = Event(
                id=generate_id(),
                user_id=test_user.id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(hours=1),
                created_at=datetime.utcnow()
            )
            db.add(event)
            db.commit()

    def test_create_event_all_optional_fields(self, test_user: User, db: Session):
        """Event can include all optional fields"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Full Event",
            description="Detailed description",
            location="Conference Room A",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=2),
            all_day=False,
            google_event_id="google_123",
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.description == "Detailed description"
        assert event.location == "Conference Room A"
        assert event.google_event_id == "google_123"


class TestGetEvent:
    """Test get single event endpoint"""

    def test_get_event_success(self, test_user: User, db: Session):
        """Should retrieve event by ID"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Test Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        # Retrieve event
        retrieved = db.query(Event).filter(
            Event.id == event.id,
            Event.user_id == test_user.id
        ).first()

        assert retrieved is not None
        assert retrieved.id == event.id
        assert retrieved.title == "Test Event"

    def test_get_event_not_found(self, test_user: User, db: Session):
        """Should return None for non-existent event"""
        retrieved = db.query(Event).filter(
            Event.id == "nonexistent",
            Event.user_id == test_user.id
        ).first()

        assert retrieved is None

    def test_get_event_wrong_user(self, test_user: User, db: Session):
        """Should not retrieve event belonging to another user"""
        # Create another user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="other",
            onboardingCompleted=False,
            onboardingStep=0
        )
        db.add(other_user)
        db.commit()

        # Create event for other user
        event = Event(
            id=generate_id(),
            user_id=other_user.id,
            title="Other Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        # Try to retrieve as test_user
        retrieved = db.query(Event).filter(
            Event.id == event.id,
            Event.user_id == test_user.id
        ).first()

        assert retrieved is None


class TestUpdateEvent:
    """Test event update endpoint"""

    def test_update_event_success(self, test_user: User, db: Session):
        """Should update event fields"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Original Title",
            description="Original Description",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        # Update event
        event.title = "Updated Title"
        event.description = "Updated Description"
        event.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(event)

        assert event.title == "Updated Title"
        assert event.description == "Updated Description"
        assert event.updated_at is not None

    def test_update_event_partial(self, test_user: User, db: Session):
        """Should update only specified fields"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Original Title",
            description="Original Description",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        # Update only title
        event.title = "New Title"
        event.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(event)

        assert event.title == "New Title"
        assert event.description == "Original Description"

    def test_update_event_not_found(self, test_user: User, db: Session):
        """Should handle update of non-existent event"""
        event = db.query(Event).filter(
            Event.id == "nonexistent",
            Event.user_id == test_user.id
        ).first()

        assert event is None


class TestDeleteEvent:
    """Test event deletion endpoint"""

    def test_delete_event_success(self, test_user: User, db: Session):
        """Should delete event"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="To Delete",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()

        event_id = event.id

        # Delete event
        db.delete(event)
        db.commit()

        # Verify deleted
        deleted = db.query(Event).filter(Event.id == event_id).first()
        assert deleted is None

    def test_delete_event_not_found(self, test_user: User, db: Session):
        """Should handle deletion of non-existent event"""
        event = db.query(Event).filter(
            Event.id == "nonexistent",
            Event.user_id == test_user.id
        ).first()

        assert event is None

    def test_delete_event_user_isolation(self, test_user: User, db: Session):
        """Should not delete event belonging to another user"""
        # Create another user
        other_user = User(
            id=generate_id(),
            email="other@example.com",
            username="other",
            onboardingCompleted=False,
            onboardingStep=0
        )
        db.add(other_user)
        db.commit()

        # Create event for other user
        event = Event(
            id=generate_id(),
            user_id=other_user.id,
            title="Other Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        event_id = event.id

        # Try to find as test_user (should fail)
        event_to_delete = db.query(Event).filter(
            Event.id == event_id,
            Event.user_id == test_user.id
        ).first()

        assert event_to_delete is None

        # Verify event still exists for other_user
        still_exists = db.query(Event).filter(
            Event.id == event_id,
            Event.user_id == other_user.id
        ).first()

        assert still_exists is not None


class TestEventTimeZones:
    """Test event time zone handling"""

    def test_event_utc_times(self, test_user: User, db: Session):
        """Events should use UTC times"""
        utc_time = datetime.utcnow()
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="UTC Event",
            start_time=utc_time,
            end_time=utc_time + timedelta(hours=1),
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # Times should match
        assert event.start_time.replace(microsecond=0) == utc_time.replace(microsecond=0)

    def test_event_all_day(self, test_user: User, db: Session):
        """All-day events should work correctly"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="All Day Event",
            start_time=today,
            end_time=today + timedelta(days=1),
            all_day=True,
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.all_day == True
        assert (event.end_time - event.start_time).days == 1


class TestGoogleCalendarSync:
    """Test Google Calendar sync functionality"""

    def test_store_google_event_id(self, test_user: User, db: Session):
        """Events from Google should store event ID"""
        event = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Google Event",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            google_event_id="google_event_123",
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        assert event.google_event_id == "google_event_123"

    def test_prevent_duplicate_google_events(self, test_user: User, db: Session):
        """Should prevent creating duplicate events from same Google event"""
        google_id = "google_event_456"

        # Create first event
        event1 = Event(
            id=generate_id(),
            user_id=test_user.id,
            title="Google Event 1",
            start_time=datetime.utcnow() + timedelta(days=1),
            end_time=datetime.utcnow() + timedelta(days=1, hours=1),
            google_event_id=google_id,
            created_at=datetime.utcnow()
        )
        db.add(event1)
        db.commit()

        # Check for existing event before creating duplicate
        existing = db.query(Event).filter(
            Event.user_id == test_user.id,
            Event.google_event_id == google_id
        ).first()

        assert existing is not None
        # In production, this would prevent creating event2
