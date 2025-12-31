"""E2E tests for Sense by Kraliki bot commands.

Tests cover:
- All slash commands (/start, /help, /sense, /astro, /bio, etc.)
- User data setup (/setbirthday, /setlocation)
- Error handling
- Subscription status checks
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Module availability check
try:
    from app.bot import handlers

    _app_available = True
except ImportError:
    _app_available = False

# Skip all tests if app modules unavailable
pytestmark = pytest.mark.skipif(not _app_available, reason="App modules not available")


class TestBotCommands:
    """Test all bot commands."""

    @pytest.mark.asyncio
    async def test_start_command(self, bot_context, update_factory):
        """Test /start command sends welcome message."""
        bot = bot_context["bot"]
        update = update_factory.create_command_update("start")

        from app.bot.handlers import cmd_start

        message = MagicMock()
        message.text = "/start"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_start(message)

        # Verify welcome message was sent
        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        # New users see onboarding message, returning users see command list
        assert "Welcome" in answer_text or "Sense by Kraliki" in answer_text
        # Onboarding includes setup prompts
        assert ("Setup" in answer_text or "birth" in answer_text.lower() or
                "/sense" in answer_text or "Sensitivity" in answer_text)

    @pytest.mark.asyncio
    async def test_help_command(self, bot_context, update_factory):
        """Test /help command sends help information."""
        bot = bot_context["bot"]

        from app.bot.handlers import cmd_help

        message = MagicMock()
        message.text = "/help"
        message.answer = AsyncMock()

        await cmd_help(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        # Verify all command categories are listed
        assert "Daily Check:" in answer_text
        assert "/sense" in answer_text
        assert "/astro" in answer_text
        assert "/bio" in answer_text
        assert "Dream Work:" in answer_text
        assert "/dream" in answer_text

    @pytest.mark.asyncio
    async def test_sense_command(self, bot_context, update_factory):
        """Test /sense command calculates sensitivity score."""
        from app.bot.handlers import cmd_sense

        message = MagicMock()
        message.text = "/sense"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_sense(message)

        # Verify two messages: "Calculating..." and report
        assert message.answer.call_count == 2

        final_answer = message.answer.call_args_list[1][0][0]
        assert "Sensitivity Score:" in final_answer or "Calculat" in final_answer

    @pytest.mark.asyncio
    async def test_astro_command(self, bot_context, update_factory):
        """Test /astro command shows astrological data."""
        from app.bot.handlers import cmd_astro

        message = MagicMock()
        message.text = "/astro"
        message.answer = AsyncMock()

        await cmd_astro(message)

        assert message.answer.call_count >= 1
        answer_text = message.answer.call_args[0][0]

        assert "Astrological Influences" in answer_text or "Calculating" in answer_text

    @pytest.mark.asyncio
    async def test_remedies_command_default(self, bot_context, update_factory):
        """Test /remedies without arguments shows default remedies."""
        from app.bot.handlers import cmd_remedies

        message = MagicMock()
        message.text = "/remedies"
        message.answer = AsyncMock()

        await cmd_remedies(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert (
            "Recommended Remedies:" in answer_text or "remedies" in answer_text.lower()
        )

    @pytest.mark.asyncio
    async def test_remedies_command_sleep(self, bot_context, update_factory):
        """Test /remedies sleep shows sleep remedies."""
        from app.bot.handlers import cmd_remedies

        message = MagicMock()
        message.text = "/remedies sleep"
        message.answer = AsyncMock()

        await cmd_remedies(message)

        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_remedies_command_focus(self, bot_context, update_factory):
        """Test /remedies focus shows focus remedies."""
        from app.bot.handlers import cmd_remedies

        message = MagicMock()
        message.text = "/remedies focus"
        message.answer = AsyncMock()

        await cmd_remedies(message)

        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_remedies_command_emotional(self, bot_context, update_factory):
        """Test /remedies emotional shows emotional remedies."""
        from app.bot.handlers import cmd_remedies

        message = MagicMock()
        message.text = "/remedies emotional"
        message.answer = AsyncMock()

        await cmd_remedies(message)

        message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_setbirthday_valid_date(self, bot_context, update_factory, mock_state):
        """Test /setbirthday with valid date format."""
        user_data = bot_context["user_data"]

        from app.bot.handlers import cmd_set_birthday

        message = MagicMock()
        message.text = "/setbirthday 1990-05-15"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_set_birthday(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Birth date set" in answer_text or "set to" in answer_text.lower() or "saved" in answer_text.lower()

    @pytest.mark.asyncio
    async def test_setbirthday_invalid_date(self, bot_context, update_factory, mock_state):
        """Test /setbirthday with invalid date format."""
        from app.bot.handlers import cmd_set_birthday

        message = MagicMock()
        message.text = "/setbirthday invalid-date"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_set_birthday(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Invalid" in answer_text or "format" in answer_text.lower() or "YYYY-MM-DD" in answer_text

    @pytest.mark.asyncio
    async def test_setlocation_valid_coordinates(self, bot_context, update_factory, mock_state):
        """Test /setlocation with valid coordinates."""
        from app.bot.handlers import cmd_set_location

        message = MagicMock()
        message.text = "/setlocation 50.0755, 14.4378"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_set_location(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Location set" in answer_text or "set to" in answer_text.lower() or "saved" in answer_text.lower()

    @pytest.mark.asyncio
    async def test_setlocation_invalid_coordinates(self, bot_context, update_factory, mock_state):
        """Test /setlocation with invalid coordinates."""
        from app.bot.handlers import cmd_set_location

        message = MagicMock()
        message.text = "/setlocation invalid"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_set_location(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Please provide" in answer_text or "coordinates" in answer_text.lower() or "latitude" in answer_text.lower()

    @pytest.mark.asyncio
    async def test_status_command_free(self, bot_context, update_factory):
        """Test /status command for free tier user."""
        user_data = bot_context["user_data"]
        user_data[12345] = {}

        from app.bot.handlers import cmd_status

        message = MagicMock()
        message.text = "/status"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_status(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Free" in answer_text or "Premium" in answer_text

    @pytest.mark.asyncio
    async def test_status_command_premium(self, bot_context, update_factory):
        """Test /status command for premium user."""
        user_data = bot_context["user_data"]
        user_data[12345] = {"premium": True}

        from app.bot.handlers import cmd_status

        message = MagicMock()
        message.text = "/status"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_status(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Premium" in answer_text

    @pytest.mark.asyncio
    async def test_subscribe_command(self, bot_context, update_factory):
        """Test /subscribe command shows subscription options."""
        from app.bot.handlers import cmd_subscribe

        message = MagicMock()
        message.text = "/subscribe"
        message.answer = AsyncMock()

        await cmd_subscribe(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Premium" in answer_text
        assert (
            "Sensitive" in answer_text
            or "Empath" in answer_text
            or "Stars" in answer_text
        )

    @pytest.mark.asyncio
    async def test_unknown_command(self, bot_context, update_factory):
        """Test unknown command shows help message."""
        from app.bot.handlers import handle_text

        message = MagicMock()
        message.text = "/unknowncommand"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        state = MagicMock()
        state.get_state = AsyncMock(return_value=None)

        await handle_text(message, state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert (
            "didn't understand" in answer_text.lower() or "help" in answer_text.lower()
        )
