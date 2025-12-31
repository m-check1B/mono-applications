"""E2E test fixtures for Telegram TL;DR Bot.

Provides mocked Telegram updates, bot instances, and Redis for
testing the complete bot flow without external API calls.

Environment Resilience:
All fixtures skip gracefully when the bot application modules are unavailable,
allowing the test suite to pass in CI environments where the bot isn't deployed.
"""
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from tests.e2e import _app_available, _app_unavailable_reason

# ============================================================
# TELEGRAM UPDATE FACTORY
# ============================================================

class TelegramUpdateFactory:
    """Factory for creating mock Telegram update payloads."""

    def __init__(self, user_id: int = 12345, chat_id: int = -100123456):
        self.user_id = user_id
        self.chat_id = chat_id
        self.update_id_counter = 1

    def _get_update_id(self) -> int:
        """Get next update ID."""
        self.update_id_counter += 1
        return self.update_id_counter

    def create_message_update(
        self,
        text: str,
        chat_type: str = "supergroup",
        username: str = "testuser",
        first_name: str = "Test",
        is_bot: bool = False,
    ) -> dict[str, Any]:
        """Create a message update payload."""
        return {
            "update_id": self._get_update_id(),
            "message": {
                "message_id": self._get_update_id(),
                "date": int(datetime.now(UTC).timestamp()),
                "chat": {
                    "id": self.chat_id,
                    "type": chat_type,
                    "title": "Test Group" if chat_type != "private" else None,
                },
                "from": {
                    "id": self.user_id,
                    "is_bot": is_bot,
                    "first_name": first_name,
                    "username": username,
                },
                "text": text,
            },
        }

    def create_command_update(
        self,
        command: str,
        args: str = "",
        chat_type: str = "supergroup",
    ) -> dict[str, Any]:
        """Create a command message update."""
        text = f"/{command}" + (f" {args}" if args else "")
        return self.create_message_update(text=text, chat_type=chat_type)

    def create_private_message_update(
        self,
        text: str,
        username: str = "testuser",
    ) -> dict[str, Any]:
        """Create a private message update."""
        return self.create_message_update(
            text=text,
            chat_type="private",
            username=username,
        )

    def create_callback_query_update(
        self,
        callback_data: str,
    ) -> dict[str, Any]:
        """Create a callback query update (button press)."""
        return {
            "update_id": self._get_update_id(),
            "callback_query": {
                "id": str(self._get_update_id()),
                "from": {
                    "id": self.user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                },
                "chat_instance": "12345",
                "data": callback_data,
                "message": {
                    "message_id": self._get_update_id(),
                    "date": int(datetime.now(UTC).timestamp()),
                    "chat": {
                        "id": self.chat_id,
                        "type": "supergroup",
                    },
                },
            },
        }

    def create_pre_checkout_query(
        self,
        invoice_payload: str,
        total_amount: int = 250,
    ) -> dict[str, Any]:
        """Create a pre-checkout query update."""
        return {
            "update_id": self._get_update_id(),
            "pre_checkout_query": {
                "id": str(self._get_update_id()),
                "from": {
                    "id": self.user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                },
                "currency": "XTR",
                "total_amount": total_amount,
                "invoice_payload": invoice_payload,
            },
        }

    def create_successful_payment_update(
        self,
        invoice_payload: str,
        total_amount: int = 250,
    ) -> dict[str, Any]:
        """Create a successful payment message update."""
        return {
            "update_id": self._get_update_id(),
            "message": {
                "message_id": self._get_update_id(),
                "date": int(datetime.now(UTC).timestamp()),
                "chat": {
                    "id": self.chat_id,
                    "type": "supergroup",
                },
                "from": {
                    "id": self.user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                },
                "successful_payment": {
                    "currency": "XTR",
                    "total_amount": total_amount,
                    "invoice_payload": invoice_payload,
                    "telegram_payment_charge_id": "test_charge_123",
                    "provider_payment_charge_id": "test_provider_123",
                },
            },
        }


@pytest.fixture
def update_factory():
    """Create a Telegram update factory."""
    return TelegramUpdateFactory()


# ============================================================
# MOCK REDIS
# ============================================================

class MockRedis:
    """In-memory Redis mock for testing."""

    def __init__(self):
        self.data: dict[str, Any] = {}
        self.sorted_sets: dict[str, dict[str, float]] = {}
        self.sets: dict[str, set] = {}
        self.expiry: dict[str, int] = {}

    async def ping(self):
        return True

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value: Any, ex: int = None):
        self.data[key] = str(value) if value is not None else None
        if ex:
            self.expiry[key] = ex
        return True

    async def incr(self, key: str):
        current = int(self.data.get(key, 0))
        self.data[key] = str(current + 1)
        return current + 1

    async def incrby(self, key: str, amount: int):
        current = int(self.data.get(key, 0))
        self.data[key] = str(current + amount)
        return current + amount

    async def expire(self, key: str, seconds: int):
        self.expiry[key] = seconds
        return True

    async def exists(self, key: str):
        return 1 if key in self.data or key in self.sorted_sets or key in self.sets else 0

    async def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                count += 1
        return count

    # Sorted set operations
    async def zadd(self, key: str, mapping: dict[str, float]):
        if key not in self.sorted_sets:
            self.sorted_sets[key] = {}
        self.sorted_sets[key].update(mapping)
        return len(mapping)

    async def zrangebyscore(self, key: str, min_score: float, max_score: str):
        if key not in self.sorted_sets:
            return []
        items = self.sorted_sets[key]
        result = []
        for member, score in sorted(items.items(), key=lambda x: x[1]):
            if score >= min_score:
                result.append(member)
        return result

    async def zremrangebyrank(self, key: str, start: int, stop: int):
        # Simplified: just keep the set as is for testing
        return 0

    # Set operations
    async def sadd(self, key: str, *members):
        if key not in self.sets:
            self.sets[key] = set()
        for member in members:
            self.sets[key].add(member)
        return len(members)

    async def scard(self, key: str):
        return len(self.sets.get(key, set()))

    # List operations
    async def lpush(self, key: str, *values):
        if key not in self.data:
            self.data[key] = []
        for value in values:
            self.data[key].insert(0, value)
        return len(self.data[key])

    async def ltrim(self, key: str, start: int, stop: int):
        if key in self.data and isinstance(self.data[key], list):
            self.data[key] = self.data[key][start:stop + 1]
        return True

    async def lrange(self, key: str, start: int, stop: int):
        if key not in self.data:
            return []
        data = self.data[key]
        if isinstance(data, list):
            return data[start:stop + 1 if stop != -1 else None]
        return []

    def pipeline(self):
        """Return a pipeline mock."""
        return MockRedisPipeline(self)

    async def close(self):
        pass


class MockRedisPipeline:
    """Mock Redis pipeline for batch operations."""

    def __init__(self, redis: MockRedis):
        self.redis = redis
        self.operations: list[tuple[str, tuple]] = []

    def get(self, key: str):
        self.operations.append(("get", (key,)))
        return self

    def set(self, key: str, value: Any):
        self.operations.append(("set", (key, value)))
        return self

    def incr(self, key: str):
        self.operations.append(("incr", (key,)))
        return self

    def incrby(self, key: str, amount: int):
        self.operations.append(("incrby", (key, amount)))
        return self

    def expire(self, key: str, seconds: int):
        self.operations.append(("expire", (key, seconds)))
        return self

    def sadd(self, key: str, *members):
        self.operations.append(("sadd", (key,) + members))
        return self

    def scard(self, key: str):
        self.operations.append(("scard", (key,)))
        return self

    def lpush(self, key: str, *values):
        self.operations.append(("lpush", (key,) + values))
        return self

    def ltrim(self, key: str, start: int, stop: int):
        self.operations.append(("ltrim", (key, start, stop)))
        return self

    async def execute(self):
        results = []
        for op, args in self.operations:
            method = getattr(self.redis, op)
            result = await method(*args)
            results.append(result)
        self.operations = []
        return results


@pytest.fixture
def mock_redis():
    """Create an in-memory Redis mock."""
    return MockRedis()


# ============================================================
# MOCK BOT AND SERVICES
# ============================================================

@pytest.fixture
def mock_bot():
    """Create a mock Telegram bot."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.send_invoice = AsyncMock()
    bot.get_chat_member = AsyncMock(return_value=MagicMock(status="administrator"))
    bot.delete_webhook = AsyncMock()
    bot.set_webhook = AsyncMock()
    bot.session = MagicMock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def mock_summarizer():
    """Create a mock summarizer that returns predefined summaries."""
    async def mock_summarize(messages: list[dict]) -> str:
        if not messages:
            return "No messages to summarize."
        return (
            "**Topics Discussed:**\n"
            "- Test topic 1\n"
            "- Test topic 2\n\n"
            "**Key Points:**\n"
            "- Important point 1\n"
            "- Important point 2\n\n"
            "**Links Shared:**\n"
            "- None\n\n"
            "**Unanswered Questions:**\n"
            "- None\n\n"
            f"**Activity:** {len(messages)} messages from test users\n\n"
            f"_Summarized {len(messages)} messages from 1 users_"
        )
    return mock_summarize


# ============================================================
# INTEGRATION FIXTURES
# ============================================================

@pytest_asyncio.fixture
async def bot_context(mock_redis, mock_bot, mock_summarizer):
    """Set up the bot with all mocked dependencies.

    Skips if the app modules are not available.
    """
    if not _app_available:
        pytest.skip(_app_unavailable_reason)

    with patch("app.services.buffer.buffer") as buffer_patch, \
         patch("app.services.analytics.analytics") as analytics_patch, \
         patch("app.services.bot.bot", mock_bot), \
         patch("app.services.summarizer.summarize_messages", mock_summarizer):

        # Set up buffer mock
        buffer_patch.redis = mock_redis
        buffer_patch.connect = AsyncMock()
        buffer_patch.close = AsyncMock()
        buffer_patch.add_message = AsyncMock()
        buffer_patch.get_messages = AsyncMock(return_value=[])
        buffer_patch.get_usage_count = AsyncMock(return_value=0)
        buffer_patch.increment_usage = AsyncMock(return_value=1)
        buffer_patch.is_subscribed = AsyncMock(return_value=False)
        buffer_patch.set_subscribed = AsyncMock()
        buffer_patch.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))

        # Set up analytics mock
        analytics_patch.redis = mock_redis
        analytics_patch.connect = AsyncMock()
        analytics_patch.close = AsyncMock()
        analytics_patch.track_command = AsyncMock()
        analytics_patch.track_message = AsyncMock()
        analytics_patch.track_summary = AsyncMock()
        analytics_patch.track_error = AsyncMock()
        analytics_patch.track_subscription = AsyncMock()
        analytics_patch.get_stats = AsyncMock(return_value={})
        analytics_patch.get_daily_stats = AsyncMock(return_value={})
        analytics_patch.get_command_stats = AsyncMock(return_value={})

        yield {
            "bot": mock_bot,
            "buffer": buffer_patch,
            "analytics": analytics_patch,
            "redis": mock_redis,
        }
