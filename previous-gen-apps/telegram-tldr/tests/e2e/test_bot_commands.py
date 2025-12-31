"""E2E tests for bot commands: /start, /help, /summary, /health, /stats.

These tests verify that:
1. Commands are parsed correctly
2. Appropriate responses are generated
3. Admin-only commands are properly restricted
4. Error handling works as expected

Note: All tests skip gracefully when the bot app modules are unavailable.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.e2e import requires_app


@requires_app
class TestStartCommand:
    """Tests for /start command."""

    @pytest.mark.asyncio
    async def test_start_command_sends_welcome_message(self, update_factory, bot_context):
        """Start command should send welcome message with setup instructions."""
        from app.services.bot import cmd_start

        # Create mock message
        message = MagicMock()
        message.answer = AsyncMock()

        # Call handler
        await cmd_start(message)

        # Verify response
        message.answer.assert_called_once()
        call_args = message.answer.call_args
        response_text = call_args[0][0]

        # Check key elements in response
        assert "Sumarium" in response_text
        assert "Add me to your group" in response_text
        assert "/summary" in response_text
        assert "free" in response_text.lower()

    @pytest.mark.asyncio
    async def test_start_command_tracks_analytics(self, update_factory, bot_context):
        """Start command should track analytics."""
        from app.services.bot import cmd_start

        message = MagicMock()
        message.answer = AsyncMock()

        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_start(message)

            # Verify analytics tracking
            analytics_mock.track_command.assert_called_with("start")


@requires_app
class TestHelpCommand:
    """Tests for /help command."""

    @pytest.mark.asyncio
    async def test_help_command_shows_commands(self, update_factory, bot_context):
        """Help command should list available commands."""
        from app.services.bot import cmd_help

        message = MagicMock()
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 12345

        await cmd_help(message)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]

        # Check that main commands are listed
        assert "/summary" in response_text
        assert "/status" in response_text
        assert "/subscribe" in response_text
        assert "/health" in response_text

    @pytest.mark.asyncio
    async def test_help_command_shows_admin_commands_for_admin(self, update_factory, bot_context):
        """Help command should show admin commands for bot admins."""
        from app.services.bot import cmd_help

        message = MagicMock()
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 999  # Admin ID

        # Patch admin check
        with patch("app.services.bot._is_admin", return_value=True):
            await cmd_help(message)

        response_text = message.answer.call_args[0][0]
        assert "/stats" in response_text
        assert "Admin" in response_text

    @pytest.mark.asyncio
    async def test_help_command_hides_admin_commands_for_regular_users(
        self, update_factory, bot_context
    ):
        """Help command should hide admin commands for regular users."""
        from app.services.bot import cmd_help

        message = MagicMock()
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 12345

        with patch("app.services.bot._is_admin", return_value=False):
            await cmd_help(message)

        response_text = message.answer.call_args[0][0]
        # Admin section should not be present
        assert "Admin Commands" not in response_text


@requires_app
class TestHealthCommand:
    """Tests for /health command."""

    @pytest.mark.asyncio
    async def test_health_command_shows_status(self, update_factory, bot_context):
        """Health command should show bot status."""
        from app.services.bot import cmd_health

        message = MagicMock()
        message.answer = AsyncMock()

        # Mock buffer.redis.ping
        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.redis = MagicMock()
            buffer_mock.redis.ping = AsyncMock(return_value=True)

            await cmd_health(message)

        message.answer.assert_called_once()
        response_text = message.answer.call_args[0][0]

        assert "Bot Health Status" in response_text
        assert "Status" in response_text
        assert "Uptime" in response_text

    @pytest.mark.asyncio
    async def test_health_command_shows_redis_status(self, update_factory, bot_context):
        """Health command should show Redis connection status."""
        from app.services.bot import cmd_health

        message = MagicMock()
        message.answer = AsyncMock()

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.redis = MagicMock()
            buffer_mock.redis.ping = AsyncMock(return_value=True)

            await cmd_health(message)

        response_text = message.answer.call_args[0][0]
        assert "Redis" in response_text
        assert "connected" in response_text


@requires_app
class TestStatsCommand:
    """Tests for /stats command (admin only)."""

    @pytest.mark.asyncio
    async def test_stats_command_denied_for_non_admin(self, update_factory, bot_context):
        """Stats command should deny access to non-admins."""
        from app.services.bot import cmd_stats

        message = MagicMock()
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 12345

        with patch("app.services.bot._is_admin", return_value=False):
            await cmd_stats(message)

        response_text = message.answer.call_args[0][0]
        assert "administrators" in response_text.lower() or "admin" in response_text.lower()

    @pytest.mark.asyncio
    async def test_stats_command_shows_analytics_for_admin(self, update_factory, bot_context):
        """Stats command should show analytics for admins."""
        from app.services.bot import cmd_stats

        message = MagicMock()
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 999

        with patch("app.services.bot._is_admin", return_value=True), \
             patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.get_stats = AsyncMock(return_value={
                "messages_processed": 1000,
                "summaries_generated": 50,
            })
            analytics_mock.get_daily_stats = AsyncMock(return_value={
                "date": "2025-12-21",
                "messages_processed": 100,
            })
            analytics_mock.get_command_stats = AsyncMock(return_value={
                "start": 10,
                "summary": 5,
            })
            analytics_mock.format_stats_message = MagicMock(
                return_value="**Analytics Report**\nTest stats..."
            )
            analytics_mock.track_command = AsyncMock()

            await cmd_stats(message)

        message.answer.assert_called()


@requires_app
class TestStatusCommand:
    """Tests for /status command."""

    @pytest.mark.asyncio
    async def test_status_command_shows_free_tier(self, update_factory, bot_context):
        """Status command should show free tier status."""
        from app.services.bot import cmd_status

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.get_usage_count = AsyncMock(return_value=1)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            await cmd_status(message)

        response_text = message.answer.call_args[0][0]
        assert "Free" in response_text or "free" in response_text
        assert "remaining" in response_text.lower() or "left" in response_text.lower()

    @pytest.mark.asyncio
    async def test_status_command_shows_pro_subscription(self, update_factory, bot_context):
        """Status command should show Pro status for subscribers."""
        from app.services.bot import cmd_status

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            buffer_mock.get_usage_count = AsyncMock(return_value=10)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            await cmd_status(message)

        response_text = message.answer.call_args[0][0]
        assert "Pro" in response_text
        assert "Unlimited" in response_text


@requires_app
class TestSummaryCommand:
    """Tests for /summary command."""

    @pytest.mark.asyncio
    async def test_summary_command_requires_group(self, update_factory, bot_context):
        """Summary command should only work in groups."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = 12345  # Private chat ID (positive)
        message.chat.type = "private"
        message.from_user = MagicMock()
        message.from_user.id = 12345

        await cmd_summary(message)

        response_text = message.answer.call_args[0][0]
        assert "group" in response_text.lower()

    @pytest.mark.asyncio
    async def test_summary_command_checks_admin_status(self, update_factory, bot_context):
        """Summary command should check if user is group admin."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with patch("app.services.bot.bot") as bot_mock:
            # User is not an admin
            member_mock = MagicMock()
            member_mock.status = "member"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            await cmd_summary(message)

        response_text = message.answer.call_args[0][0]
        assert "admin" in response_text.lower()

    @pytest.mark.asyncio
    async def test_summary_command_checks_usage_limits(self, update_factory, bot_context):
        """Summary command should check usage limits."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock:
            # User is admin
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            # Usage limit reached
            buffer_mock.can_summarize = AsyncMock(return_value=(False, "limit_reached"))

            await cmd_summary(message)

        # Should prompt to subscribe
        response_text = message.answer.call_args[0][0]
        assert "subscribe" in response_text.lower() or "trial" in response_text.lower()

    @pytest.mark.asyncio
    async def test_summary_command_parses_hours_argument(self, update_factory, bot_context):
        """Summary command should parse hours argument."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary 6"  # Request 6 hours

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.summarize_messages"):
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=[])
            buffer_mock.is_subscribed = AsyncMock(return_value=False)

            await cmd_summary(message)

            # Should call get_messages with hours=6
            buffer_mock.get_messages.assert_called_once()
            call_kwargs = buffer_mock.get_messages.call_args[1]
            assert call_kwargs.get("hours") == 6

    @pytest.mark.asyncio
    async def test_summary_command_caps_hours_at_24(self, update_factory, bot_context):
        """Summary command should cap hours at 24."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary 48"  # Request 48 hours (should cap at 24)

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock:
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=[])
            buffer_mock.is_subscribed = AsyncMock(return_value=False)

            await cmd_summary(message)

            # Should call get_messages with hours=24 (capped)
            call_kwargs = buffer_mock.get_messages.call_args[1]
            assert call_kwargs.get("hours") == 24

    @pytest.mark.asyncio
    async def test_summary_command_handles_no_messages(self, update_factory, bot_context):
        """Summary command should handle empty message buffer."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock:
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=[])

            await cmd_summary(message)

        # Find the "no messages" response
        calls = message.answer.call_args_list
        no_messages_found = any(
            "no messages" in str(call).lower()
            for call in calls
        )
        assert no_messages_found

    @pytest.mark.asyncio
    async def test_summary_command_generates_summary(self, update_factory, bot_context):
        """Summary command should generate and return summary."""
        from app.services.bot import cmd_summary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/summary"

        mock_messages = [
            {"user": "user1", "text": "Hello everyone", "ts": "2025-12-21T10:00:00"},
            {"user": "user2", "text": "Hi there!", "ts": "2025-12-21T10:01:00"},
        ]

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.summarize_messages") as summarize_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            member_mock = MagicMock()
            member_mock.status = "administrator"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)

            buffer_mock.can_summarize = AsyncMock(return_value=(True, "free_tier:3"))
            buffer_mock.get_messages = AsyncMock(return_value=mock_messages)
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            buffer_mock.increment_usage = AsyncMock(return_value=1)
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            buffer_mock.get_summary_language = AsyncMock(return_value="en")

            summarize_mock.return_value = "**Topics Discussed:**\n- Greetings"
            analytics_mock.track_command = AsyncMock()
            analytics_mock.track_summary = AsyncMock()

            await cmd_summary(message)

        # Last answer should contain the summary
        last_call = message.answer.call_args_list[-1]
        response_text = last_call[0][0]
        assert "Topics" in response_text


@requires_app
class TestSubscribeCommand:
    """Tests for /subscribe command."""

    @pytest.mark.asyncio
    async def test_subscribe_command_sends_invoice(self, update_factory, bot_context):
        """Subscribe command should send Telegram Stars invoice."""
        from app.services.bot import cmd_subscribe

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.bot") as bot_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            bot_mock.send_invoice = AsyncMock()

            await cmd_subscribe(message)

        bot_mock.send_invoice.assert_called_once()
        call_kwargs = bot_mock.send_invoice.call_args[1]
        assert call_kwargs["currency"] == "XTR"  # Telegram Stars
        assert "Pro" in call_kwargs["title"]

    @pytest.mark.asyncio
    async def test_subscribe_command_skips_if_already_subscribed(
        self, update_factory, bot_context
    ):
        """Subscribe command should skip invoice if already subscribed."""
        from app.services.bot import cmd_subscribe

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.bot") as bot_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            bot_mock.send_invoice = AsyncMock()

            await cmd_subscribe(message)

        # Should not send invoice
        bot_mock.send_invoice.assert_not_called()
        # Should inform user they're already subscribed
        response_text = message.answer.call_args[0][0]
        assert "already" in response_text.lower()
