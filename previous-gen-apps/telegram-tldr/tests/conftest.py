"""Test fixtures for TL;DR Bot."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.lpush = AsyncMock(return_value=1)
    redis_mock.lrange = AsyncMock(return_value=[])
    return redis_mock


@pytest.fixture
def mock_buffer(mock_redis):
    """Mock message buffer."""
    with patch("app.services.buffer.buffer") as buffer_mock:
        buffer_mock.redis = mock_redis
        buffer_mock.connect = AsyncMock()
        buffer_mock.close = AsyncMock()
        yield buffer_mock


@pytest.fixture
def mock_bot():
    """Mock Telegram bot."""
    # Import the module first to ensure it's loaded before patching
    import app.services.bot
    with patch.object(app.services.bot, "bot") as bot_mock:
        bot_mock.session = MagicMock()
        bot_mock.session.close = AsyncMock()
        bot_mock.delete_webhook = AsyncMock()
        bot_mock.set_webhook = AsyncMock()
        yield bot_mock


@pytest.fixture
def mock_settings():
    """Mock settings for tests - include all required settings attributes."""
    with patch("app.main.settings") as settings_mock:
        # Webhook settings
        settings_mock.telegram_webhook_secret = "test-secret-token"
        settings_mock.telegram_webhook_url = ""  # Disable webhook setup in tests

        # App settings
        settings_mock.app_name = "TL;DR Bot"
        settings_mock.debug = False

        # Payment settings (required by lifespan validation)
        settings_mock.subscription_price_stars = 250
        settings_mock.newsletter_price_stars = 250

        yield settings_mock


@pytest.fixture
def mock_analytics(mock_redis):
    """Mock analytics service."""
    with patch("app.main.analytics") as analytics_mock:
        analytics_mock.redis = mock_redis
        analytics_mock.connect = AsyncMock()
        analytics_mock.close = AsyncMock()
        analytics_mock.get_dashboard_data = AsyncMock(return_value={
            "generated_at": "2025-12-26T00:00:00+00:00",
            "all_time": {
                "messages_processed": 1000,
                "summaries_generated": 50,
                "messages_summarized": 5000,
                "errors_total": 5,
                "subscriptions_total": 10,
                "unique_users": 100,
                "unique_chats": 20,
            },
            "today": {
                "date": "2025-12-26",
                "messages_processed": 100,
                "summaries_generated": 5,
                "messages_summarized": 500,
                "errors": 0,
                "new_subscriptions": 1,
                "active_users": 20,
                "active_chats": 5,
            },
            "commands": {
                "start": 50,
                "summary": 100,
                "help": 30,
                "status": 20,
                "subscribe": 10,
                "health": 5,
                "stats": 2,
            },
            "trends_7d": [
                {"date": "2025-12-20", "messages_processed": 80, "summaries_generated": 4, "active_users": 15, "active_chats": 4},
                {"date": "2025-12-21", "messages_processed": 90, "summaries_generated": 5, "active_users": 18, "active_chats": 5},
                {"date": "2025-12-22", "messages_processed": 85, "summaries_generated": 4, "active_users": 16, "active_chats": 4},
                {"date": "2025-12-23", "messages_processed": 95, "summaries_generated": 6, "active_users": 19, "active_chats": 5},
                {"date": "2025-12-24", "messages_processed": 70, "summaries_generated": 3, "active_users": 14, "active_chats": 3},
                {"date": "2025-12-25", "messages_processed": 60, "summaries_generated": 2, "active_users": 12, "active_chats": 3},
                {"date": "2025-12-26", "messages_processed": 100, "summaries_generated": 5, "active_users": 20, "active_chats": 5},
            ],
            "trends_30d": [],
            "recent_errors": [],
        })
        yield analytics_mock


@pytest.fixture
def client(mock_buffer, mock_bot, mock_settings, mock_analytics):
    """Create test client with mocked dependencies."""
    from fastapi.testclient import TestClient

    # Patch the lifespan to skip actual connections
    with patch("app.main.buffer", mock_buffer), \
         patch("app.main.bot", mock_bot), \
         patch("app.main.analytics", mock_analytics), \
         patch("app.main.setup_webhook", AsyncMock()), \
         patch("app.main.remove_webhook", AsyncMock()):
        from app.main import app
        with TestClient(app) as c:
            yield c
