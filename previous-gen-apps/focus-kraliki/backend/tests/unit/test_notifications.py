"""
Push Notifications Router Tests
VD-384: Tests for Web Push subscription management and notification preferences.
"""

import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.models.user import User


class TestVapidKey:
    """Tests for VAPID key endpoint."""

    @pytest.mark.asyncio
    async def test_get_vapid_key_success(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Test getting VAPID public key."""
        response = await async_client.get(
            "/notifications/vapid-key",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "publicKey" in data
        assert len(data["publicKey"]) > 0


class TestPushSubscription:
    """Tests for push subscription management."""

    @pytest.mark.asyncio
    async def test_subscribe_success(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test subscribing to push notifications."""
        subscription_data = {
            "endpoint": "https://push.example.com/endpoint123",
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }

        response = await async_client.post(
            "/notifications/subscribe",
            json=subscription_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Subscribed" in data["message"]

        # Verify subscription is stored in user preferences
        db.refresh(test_user)
        prefs = test_user.preferences or {}
        assert "pushSubscription" in prefs
        assert prefs["pushSubscription"]["endpoint"] == subscription_data["endpoint"]

    @pytest.mark.asyncio
    async def test_subscribe_initializes_notification_prefs(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test that subscribe initializes notification preferences."""
        # Clear any existing preferences
        test_user.preferences = {}
        db.commit()

        subscription_data = {
            "endpoint": "https://push.example.com/endpoint456",
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }

        response = await async_client.post(
            "/notifications/subscribe",
            json=subscription_data,
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify notification preferences are initialized
        db.refresh(test_user)
        prefs = test_user.preferences or {}
        assert "notifications" in prefs
        assert prefs["notifications"]["enabled"] is True
        assert prefs["notifications"]["taskReminders"] is True

    @pytest.mark.asyncio
    async def test_unsubscribe_success(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test unsubscribing from push notifications."""
        # First subscribe
        test_user.preferences = {
            "pushSubscription": {
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            },
            "notifications": {"enabled": True}
        }
        db.commit()

        response = await async_client.delete(
            "/notifications/subscribe",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Unsubscribed" in data["message"]

        # Verify subscription is removed
        db.refresh(test_user)
        prefs = test_user.preferences or {}
        assert "pushSubscription" not in prefs
        assert prefs.get("notifications", {}).get("enabled") is False

    @pytest.mark.asyncio
    async def test_subscribe_without_auth_fails(self, async_client: AsyncClient):
        """Test that subscribe requires authentication."""
        response = await async_client.post(
            "/notifications/subscribe",
            json={
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            }
        )

        assert response.status_code == 401


class TestNotificationPreferences:
    """Tests for notification preferences management."""

    @pytest.mark.asyncio
    async def test_get_preferences_default(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test getting default notification preferences."""
        # Clear preferences
        test_user.preferences = {}
        db.commit()

        response = await async_client.get(
            "/notifications/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check default values
        assert data["taskReminders"] is True
        assert data["dailyDigest"] is True
        assert data["pomodoroAlerts"] is True
        assert data["projectUpdates"] is False

    @pytest.mark.asyncio
    async def test_get_preferences_custom(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test getting custom notification preferences."""
        test_user.preferences = {
            "notifications": {
                "taskReminders": False,
                "dailyDigest": True,
                "pomodoroAlerts": False,
                "projectUpdates": True
            }
        }
        db.commit()

        response = await async_client.get(
            "/notifications/preferences",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["taskReminders"] is False
        assert data["dailyDigest"] is True
        assert data["pomodoroAlerts"] is False
        assert data["projectUpdates"] is True

    @pytest.mark.asyncio
    async def test_update_preferences_success(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test updating notification preferences."""
        response = await async_client.patch(
            "/notifications/preferences",
            json={
                "taskReminders": False,
                "projectUpdates": True
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify preferences are updated
        db.refresh(test_user)
        prefs = test_user.preferences or {}
        notif_prefs = prefs.get("notifications", {})
        assert notif_prefs.get("taskReminders") is False
        assert notif_prefs.get("projectUpdates") is True

    @pytest.mark.asyncio
    async def test_update_preferences_partial(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test partial update of preferences preserves other values."""
        # Set initial preferences
        test_user.preferences = {
            "notifications": {
                "enabled": True,
                "taskReminders": True,
                "dailyDigest": False,
                "pomodoroAlerts": True,
                "projectUpdates": False
            }
        }
        db.commit()

        # Update only one preference
        response = await async_client.patch(
            "/notifications/preferences",
            json={"dailyDigest": True},
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify other preferences are preserved
        db.refresh(test_user)
        prefs = test_user.preferences.get("notifications", {})
        assert prefs.get("taskReminders") is True  # Preserved
        assert prefs.get("dailyDigest") is True  # Updated
        assert prefs.get("pomodoroAlerts") is True  # Preserved


class TestTestNotification:
    """Tests for test notification endpoint."""

    @pytest.mark.asyncio
    async def test_test_notification_no_subscription(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test that test notification fails without subscription."""
        # Clear subscription
        test_user.preferences = {}
        db.commit()

        response = await async_client.post(
            "/notifications/test",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "No push subscription found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_test_notification_dev_mode(
        self, async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test notification in dev mode (no VAPID private key)."""
        # Add subscription
        test_user.preferences = {
            "pushSubscription": {
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            }
        }
        db.commit()

        # VAPID_PRIVATE_KEY is not set in test environment
        response = await async_client.post(
            "/notifications/test",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "VAPID not configured" in data["message"]

    @pytest.mark.asyncio
    @patch("app.routers.notifications.VAPID_PRIVATE_KEY", "test_private_key")
    @patch("app.routers.notifications.webpush")
    async def test_test_notification_success(
        self, mock_webpush: MagicMock,
        async_client: AsyncClient, auth_headers: dict, test_user: User, db: Session
    ):
        """Test successful notification sending with mocked webpush."""
        # Add subscription
        test_user.preferences = {
            "pushSubscription": {
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            }
        }
        db.commit()

        response = await async_client.post(
            "/notifications/test",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Test notification sent" in data["message"]

        # Verify webpush was called
        mock_webpush.assert_called_once()


class TestSendPushNotification:
    """Tests for the utility function to send push notifications."""

    @pytest.mark.asyncio
    @patch("app.routers.notifications.VAPID_PRIVATE_KEY", "test_private_key")
    @patch("app.routers.notifications.webpush")
    async def test_send_push_notification_success(
        self, mock_webpush: MagicMock, test_user: User, db: Session
    ):
        """Test successful push notification sending."""
        from app.routers.notifications import send_push_notification

        # Add subscription
        test_user.preferences = {
            "pushSubscription": {
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            },
            "notifications": {"enabled": True}
        }
        db.commit()

        result = await send_push_notification(
            user_id=test_user.id,
            title="Test Title",
            body="Test Body",
            url="/test",
            tag="test",
            db=db
        )

        assert result is True
        mock_webpush.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_push_notification_no_vapid(self, test_user: User, db: Session):
        """Test that notification fails without VAPID key."""
        from app.routers.notifications import send_push_notification

        result = await send_push_notification(
            user_id=test_user.id,
            title="Test",
            body="Test",
            db=db
        )

        assert result is False

    @pytest.mark.asyncio
    @patch("app.routers.notifications.VAPID_PRIVATE_KEY", "test_private_key")
    async def test_send_push_notification_no_subscription(
        self, test_user: User, db: Session
    ):
        """Test that notification fails without subscription."""
        from app.routers.notifications import send_push_notification

        # No subscription
        test_user.preferences = {}
        db.commit()

        result = await send_push_notification(
            user_id=test_user.id,
            title="Test",
            body="Test",
            db=db
        )

        assert result is False

    @pytest.mark.asyncio
    @patch("app.routers.notifications.VAPID_PRIVATE_KEY", "test_private_key")
    async def test_send_push_notification_disabled(
        self, test_user: User, db: Session
    ):
        """Test that notification respects user preference."""
        from app.routers.notifications import send_push_notification

        # Subscription exists but notifications disabled
        test_user.preferences = {
            "pushSubscription": {
                "endpoint": "https://push.example.com/endpoint",
                "keys": {"p256dh": "test", "auth": "test"}
            },
            "notifications": {"enabled": False}
        }
        db.commit()

        result = await send_push_notification(
            user_id=test_user.id,
            title="Test",
            body="Test",
            db=db
        )

        assert result is False


class TestHelperFunctions:
    """Tests for notification helper functions."""

    @pytest.mark.asyncio
    @patch("app.routers.notifications.send_push_notification")
    async def test_send_task_reminder(
        self, mock_send: MagicMock, test_user: User, db: Session
    ):
        """Test task reminder notification."""
        from app.routers.notifications import send_task_reminder

        mock_send.return_value = True

        result = await send_task_reminder(
            user_id=test_user.id,
            task_title="Complete project",
            due_date="today",
            db=db
        )

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "Task Reminder" in call_args.kwargs["title"]
        assert "Complete project" in call_args.kwargs["body"]

    @pytest.mark.asyncio
    @patch("app.routers.notifications.send_push_notification")
    async def test_send_pomodoro_alert(
        self, mock_send: MagicMock, test_user: User, db: Session
    ):
        """Test pomodoro alert notification."""
        from app.routers.notifications import send_pomodoro_alert

        mock_send.return_value = True

        result = await send_pomodoro_alert(
            user_id=test_user.id,
            message="Time for a break!",
            db=db
        )

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "Pomodoro Timer" in call_args.kwargs["title"]
        assert "Time for a break!" in call_args.kwargs["body"]

    @pytest.mark.asyncio
    @patch("app.routers.notifications.send_push_notification")
    async def test_send_daily_digest(
        self, mock_send: MagicMock, test_user: User, db: Session
    ):
        """Test daily digest notification."""
        from app.routers.notifications import send_daily_digest

        mock_send.return_value = True

        result = await send_daily_digest(
            user_id=test_user.id,
            task_count=5,
            top_priority="Finish report",
            db=db
        )

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert "Daily Focus" in call_args.kwargs["title"]
        assert "5 tasks" in call_args.kwargs["body"]
        assert "Finish report" in call_args.kwargs["body"]
