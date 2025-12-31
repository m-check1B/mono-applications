"""Extended tests for bot commands: /length, /language, /topicsummary, /detecttopics, /schedule, /unschedule, /periodic.

These tests verify the additional bot commands that weren't covered in the e2e tests.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Decorator to skip tests if app modules unavailable
def requires_app(cls):
    try:
        from app.services import bot
        return cls
    except ImportError:
        return pytest.mark.skip(reason="App modules not available")(cls)


@requires_app
class TestLengthCommand:
    """Tests for /length command."""

    @pytest.mark.asyncio
    async def test_length_shows_current_setting(self):
        """Length command without args shows current setting."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.get_summary_length = AsyncMock(return_value="medium")
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        response_text = message.answer.call_args[0][0]
        assert "Current" in response_text
        assert "Medium" in response_text or "medium" in response_text

    @pytest.mark.asyncio
    async def test_length_sets_short(self):
        """Length command sets short preference."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length short"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_length = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        buffer_mock.set_summary_length.assert_called_once_with(-100123456, "short")
        response_text = message.answer.call_args[0][0]
        assert "short" in response_text.lower()

    @pytest.mark.asyncio
    async def test_length_sets_medium(self):
        """Length command sets medium preference."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length medium"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_length = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        buffer_mock.set_summary_length.assert_called_once_with(-100123456, "medium")

    @pytest.mark.asyncio
    async def test_length_sets_long(self):
        """Length command sets long preference."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length long"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_length = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        buffer_mock.set_summary_length.assert_called_once_with(-100123456, "long")

    @pytest.mark.asyncio
    async def test_length_rejects_invalid(self):
        """Length command rejects invalid length."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length huge"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        # Should not call set_summary_length
        buffer_mock.set_summary_length.assert_not_called()
        response_text = message.answer.call_args[0][0]
        assert "Invalid" in response_text or "invalid" in response_text.lower()

    @pytest.mark.asyncio
    async def test_length_handles_set_failure(self):
        """Length command handles failed set operation."""
        from app.services.bot import cmd_length

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/length short"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_length = AsyncMock(return_value=False)
            analytics_mock.track_command = AsyncMock()

            await cmd_length(message)

        response_text = message.answer.call_args[0][0]
        assert "Failed" in response_text or "failed" in response_text.lower()


@requires_app
class TestLanguageCommand:
    """Tests for /language command."""

    @pytest.mark.asyncio
    async def test_language_shows_current_setting(self):
        """Language command without args shows current setting."""
        from app.services.bot import cmd_language

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/language"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.get_summary_language = AsyncMock(return_value="auto")
            buffer_mock.get_messages = AsyncMock(return_value=[])
            analytics_mock.track_command = AsyncMock()

            await cmd_language(message)

        response_text = message.answer.call_args[0][0]
        assert "Current" in response_text
        assert "Auto" in response_text or "auto" in response_text

    @pytest.mark.asyncio
    async def test_language_sets_english(self):
        """Language command sets English preference."""
        from app.services.bot import cmd_language

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/language en"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_language = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_language(message)

        buffer_mock.set_summary_language.assert_called_once_with(-100123456, "en")
        response_text = message.answer.call_args[0][0]
        assert "English" in response_text

    @pytest.mark.asyncio
    async def test_language_sets_auto(self):
        """Language command sets auto-detect preference."""
        from app.services.bot import cmd_language

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/language auto"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.set_summary_language = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_language(message)

        buffer_mock.set_summary_language.assert_called_once_with(-100123456, "auto")

    @pytest.mark.asyncio
    async def test_language_shows_list(self):
        """Language command with 'list' shows all languages."""
        from app.services.bot import cmd_language

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/language list"

        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_language(message)

        response_text = message.answer.call_args[0][0]
        assert "Supported" in response_text
        assert "en" in response_text

    @pytest.mark.asyncio
    async def test_language_rejects_invalid(self):
        """Language command rejects invalid language code."""
        from app.services.bot import cmd_language

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/language xyz"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_language(message)

        buffer_mock.set_summary_language.assert_not_called()
        response_text = message.answer.call_args[0][0]
        assert "Unknown" in response_text or "unknown" in response_text.lower()


@requires_app
class TestTopicSummaryCommand:
    """Tests for /topicsummary command."""

    @pytest.mark.asyncio
    async def test_topicsummary_requires_group(self):
        """Topic summary command only works in groups."""
        from app.services.bot import cmd_topicsummary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = 12345  # Private chat
        message.chat.type = "private"

        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_topicsummary(message)

        response_text = message.answer.call_args[0][0]
        assert "group" in response_text.lower()

    @pytest.mark.asyncio
    async def test_topicsummary_checks_admin(self):
        """Topic summary command checks admin status."""
        from app.services.bot import cmd_topicsummary

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/topicsummary"

        with patch("app.services.bot.bot") as bot_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            member_mock = MagicMock()
            member_mock.status = "member"
            bot_mock.get_chat_member = AsyncMock(return_value=member_mock)
            analytics_mock.track_command = AsyncMock()

            await cmd_topicsummary(message)

        response_text = message.answer.call_args[0][0]
        assert "admin" in response_text.lower()


@requires_app
class TestDetectTopicsCommand:
    """Tests for /detecttopics command."""

    @pytest.mark.asyncio
    async def test_detecttopics_requires_group(self):
        """Detect topics command only works in groups."""
        from app.services.bot import cmd_detecttopics

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = 12345  # Private chat
        message.chat.type = "private"

        with patch("app.services.bot.analytics") as analytics_mock:
            analytics_mock.track_command = AsyncMock()

            await cmd_detecttopics(message)

        response_text = message.answer.call_args[0][0]
        assert "group" in response_text.lower()

    @pytest.mark.asyncio
    async def test_detecttopics_requires_subscription(self):
        """Detect topics command requires Pro subscription."""
        from app.services.bot import cmd_detecttopics

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.id = 12345
        message.text = "/detecttopics"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            analytics_mock.track_command = AsyncMock()

            await cmd_detecttopics(message)

        response_text = message.answer.call_args[0][0]
        assert "Pro" in response_text or "subscribe" in response_text.lower()


@requires_app
class TestScheduleCommand:
    """Tests for /schedule command."""

    @pytest.mark.asyncio
    async def test_schedule_shows_current(self):
        """Schedule command shows current schedule."""
        from app.services.bot import cmd_schedule

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.text = "/schedule"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.get_schedule = AsyncMock(return_value=None)
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_schedule(message)

        # Should show current schedule or no schedule
        message.answer.assert_called()


@requires_app
class TestUnscheduleCommand:
    """Tests for /unschedule command."""

    @pytest.mark.asyncio
    async def test_unschedule_removes_schedule(self):
        """Unschedule command removes the schedule."""
        from app.services.bot import cmd_unschedule

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.remove_schedule = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_unschedule(message)

        buffer_mock.remove_schedule.assert_called_once_with(-100123456)

    @pytest.mark.asyncio
    async def test_unschedule_handles_no_schedule(self):
        """Unschedule command handles case when no schedule exists."""
        from app.services.bot import cmd_unschedule

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.remove_schedule = AsyncMock(return_value=False)
            analytics_mock.track_command = AsyncMock()

            await cmd_unschedule(message)

        response_text = message.answer.call_args[0][0]
        assert "no" in response_text.lower() or "not" in response_text.lower()


@requires_app
class TestPeriodicCommand:
    """Tests for /periodic command."""

    @pytest.mark.asyncio
    async def test_periodic_shows_help(self):
        """Periodic command without args shows help for subscribers."""
        from app.services.bot import cmd_periodic

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.text = "/periodic"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.get_periodic_schedule = AsyncMock(return_value=None)
            buffer_mock.get_last_digest_time = AsyncMock(return_value=None)
            buffer_mock.is_subscribed = AsyncMock(return_value=True)
            analytics_mock.track_command = AsyncMock()

            await cmd_periodic(message)

        # Should show usage or current status
        message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_periodic_requires_subscription(self):
        """Periodic command requires Pro subscription."""
        from app.services.bot import cmd_periodic

        message = MagicMock()
        message.answer = AsyncMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.text = "/periodic"

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.is_subscribed = AsyncMock(return_value=False)
            analytics_mock.track_command = AsyncMock()

            await cmd_periodic(message)

        response_text = message.answer.call_args[0][0]
        assert "Pro" in response_text or "subscribe" in response_text.lower()


@requires_app
class TestHelperFunctions:
    """Tests for helper functions in bot.py."""

    def test_is_admin_with_valid_admin(self):
        """_is_admin returns True for valid admin."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = "123, 456"

            assert _is_admin(123) is True
            assert _is_admin(456) is True

    def test_is_admin_with_non_admin(self):
        """_is_admin returns False for non-admin."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = "123, 456"

            assert _is_admin(789) is False

    def test_is_admin_with_empty_config(self):
        """_is_admin returns False when no admins configured."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = ""

            assert _is_admin(123) is False

    def test_is_admin_with_none_config(self):
        """_is_admin returns False when admin_user_ids is None."""
        from app.services.bot import _is_admin

        with patch("app.services.bot.settings") as settings_mock:
            settings_mock.admin_user_ids = None

            assert _is_admin(123) is False

    def test_format_uptime_seconds_only(self):
        """_format_uptime formats seconds correctly."""
        from app.services.bot import _format_uptime
        from datetime import datetime, timedelta, UTC

        # 30 seconds ago
        start = datetime.now(UTC) - timedelta(seconds=30)
        result = _format_uptime(start)

        # Should contain just seconds
        assert "s" in result
        assert "m" not in result or "0m" not in result

    def test_format_uptime_with_hours(self):
        """_format_uptime formats hours correctly."""
        from app.services.bot import _format_uptime
        from datetime import datetime, timedelta, UTC

        # 2 hours, 30 minutes, 45 seconds ago
        start = datetime.now(UTC) - timedelta(hours=2, minutes=30, seconds=45)
        result = _format_uptime(start)

        assert "2h" in result
        assert "30m" in result

    def test_format_uptime_with_days(self):
        """_format_uptime formats days correctly."""
        from app.services.bot import _format_uptime
        from datetime import datetime, timedelta, UTC

        # 3 days ago
        start = datetime.now(UTC) - timedelta(days=3)
        result = _format_uptime(start)

        assert "3d" in result

    def test_get_summary_mode_description_auto(self):
        """get_summary_mode_description returns correct description for auto."""
        from app.services.bot import get_summary_mode_description

        result = get_summary_mode_description("auto")
        assert "dominant" in result.lower() or "match" in result.lower()

    def test_get_summary_mode_description_specific(self):
        """get_summary_mode_description returns correct description for specific language."""
        from app.services.bot import get_summary_mode_description

        result = get_summary_mode_description("en")
        assert "English" in result


@requires_app
class TestPreCheckoutHandler:
    """Tests for pre-checkout query handler."""

    @pytest.mark.asyncio
    async def test_pre_checkout_approved(self):
        """Pre-checkout query is approved."""
        from app.services.bot import process_pre_checkout

        query = MagicMock()
        query.answer = AsyncMock()

        await process_pre_checkout(query)

        query.answer.assert_called_once_with(ok=True)


@requires_app
class TestMessageHandler:
    """Tests for general message handler."""

    @pytest.mark.asyncio
    async def test_message_buffered_in_group(self):
        """Messages in groups are buffered."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.from_user.first_name = "Test"
        message.from_user.username = "testuser"
        message.from_user.is_bot = False
        message.text = "Hello, world!"
        message.date = MagicMock()

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.add_message = AsyncMock()
            analytics_mock.track_message = AsyncMock()

            await handle_message(message)

        buffer_mock.add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_private_messages_not_buffered(self):
        """Private messages are not buffered."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = 12345
        message.chat.type = "private"
        message.from_user = MagicMock()
        message.from_user.first_name = "Test"
        message.from_user.username = "testuser"
        message.from_user.is_bot = False
        message.text = "Hello!"
        message.date = MagicMock()

        with patch("app.services.bot.buffer") as buffer_mock, \
             patch("app.services.bot.analytics") as analytics_mock:
            buffer_mock.add_message = AsyncMock()
            analytics_mock.track_message = AsyncMock()

            await handle_message(message)

        buffer_mock.add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_empty_messages_not_buffered(self):
        """Empty messages are not buffered."""
        from app.services.bot import handle_message

        message = MagicMock()
        message.chat = MagicMock()
        message.chat.id = -100123456
        message.chat.type = "supergroup"
        message.from_user = MagicMock()
        message.text = ""

        with patch("app.services.bot.buffer") as buffer_mock:
            buffer_mock.add_message = AsyncMock()

            await handle_message(message)

        buffer_mock.add_message.assert_not_called()
