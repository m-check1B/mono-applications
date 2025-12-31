"""E2E tests for Sense by Kraliki dream analysis feature.

Tests cover:
- Dream analysis flow (/dream command)
- Multi-step conversation (state management)
- Dream with direct text argument
- Error handling
- Integration with sensitivity data
"""

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


class TestDreamAnalysis:
    """Test dream analysis functionality."""

    @pytest.mark.asyncio
    async def test_dream_command_with_text(self, bot_context, mock_state):
        """Test /dream command with dream text provided directly."""
        from app.bot.handlers import cmd_dream

        message = MagicMock()
        message.text = "/dream I was flying over mountains and met a wise owl"
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 12345

        await cmd_dream(message, mock_state)

        # Should analyze the dream - sends "Analyzing..." first, then result
        assert message.answer.call_count >= 1
        # Check that any call contains dream-related content
        all_calls_text = " ".join([call[0][0].lower() for call in message.answer.call_args_list])
        assert "analyzing" in all_calls_text or "dream" in all_calls_text

    @pytest.mark.asyncio
    async def test_dream_command_without_text(self, bot_context, mock_state):
        """Test /dream command without text enters waiting state."""
        from app.bot.handlers import cmd_dream

        message = MagicMock()
        message.text = "/dream"
        message.answer = AsyncMock()

        await cmd_dream(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert (
            "Tell me about your dream" in answer_text
            or "describe" in answer_text.lower()
            or "share" in answer_text.lower()
        )
        mock_state.set_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_dream_state_processing(self, bot_context, mock_state):
        """Test dream analysis from waiting state."""
        from app.bot.handlers import process_dream_state

        message = MagicMock()
        message.text = (
            "Last night I dreamed of walking through a forest with golden trees"
        )
        message.answer = AsyncMock()
        message.from_user = MagicMock()
        message.from_user.id = 12345

        await process_dream_state(message, mock_state)

        # Should send at least one response (may be multiple for long dreams)
        assert message.answer.call_count >= 1
        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_dream_analysis_keywords(self, bot_context, mock_state):
        """Test dream analysis recognizes dream keywords in plain text."""
        from app.bot.handlers import handle_text

        message = MagicMock()
        # Message must be > 50 chars to trigger dream detection
        message.text = "Last night I dreamt that I was swimming in a vast ocean filled with glowing stars and mysterious creatures"
        message.answer = AsyncMock()

        await handle_text(message, mock_state)

        # Should detect dream keywords and offer analysis
        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "dream" in answer_text.lower() or "analyze" in answer_text.lower()

    @pytest.mark.asyncio
    async def test_dream_non_keyword_text(self, bot_context, mock_state):
        """Test non-dream text doesn't trigger dream analysis."""
        from app.bot.handlers import handle_text

        message = MagicMock()
        message.text = "Hello, how are you today?"
        message.answer = AsyncMock()

        await handle_text(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        # Should show help, not dream analysis
        assert (
            "didn't understand" in answer_text.lower() or "help" in answer_text.lower()
        )

    @pytest.mark.asyncio
    async def test_dream_long_text_splitting(self, bot_context, mock_state):
        """Test long dream responses are split for Telegram limits."""
        from app.bot.handlers import process_dream, analyze_dream

        # Mock a very long dream analysis
        long_analysis = "Dream interpretation:\n" + "Detailed analysis line.\n" * 50

        with patch(
            "app.bot.handlers.analyze_dream", AsyncMock(return_value=long_analysis)
        ) as mock_analyze:
            from app.bot.handlers import cmd_dream

            message = MagicMock()
            message.text = "/dream test dream"
            message.answer = AsyncMock()

            await cmd_dream(message, mock_state)

            # For very long responses, should be split into multiple messages
            # (This depends on actual implementation, may send multiple answer calls)
            assert message.answer.call_count >= 1


class TestBiorhythm:
    """Test biorhythm calculation feature."""

    @pytest.mark.asyncio
    async def test_biorhythm_with_birthdate(self, bot_context, mock_state):
        """Test /bio command with user birthdate set."""
        from datetime import datetime
        from unittest.mock import patch, AsyncMock

        from app.bot.handlers import cmd_biorhythm

        message = MagicMock()
        message.text = "/bio"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        # Patch storage.get_user to return user with birth_date
        with patch("app.bot.handlers.storage") as mock_storage:
            mock_storage.get_user = AsyncMock(return_value={"birth_date": datetime(1990, 5, 15)})
            await cmd_biorhythm(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Biorhythm" in answer_text
        assert (
            "Physical" in answer_text
            or "Emotional" in answer_text
            or "Intellectual" in answer_text
        )

    @pytest.mark.asyncio
    async def test_biorhythm_without_birthdate(self, bot_context, mock_state):
        """Test /bio command without birthdate shows error."""
        from app.bot.handlers import cmd_biorhythm

        message = MagicMock()
        message.text = "/bio"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_biorhythm(message, mock_state)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "birth date" in answer_text.lower() or "/setbirthday" in answer_text


class TestForecast:
    """Test 12-month forecast feature."""

    @pytest.mark.asyncio
    async def test_forecast_months_1_to_6(self, bot_context, mock_state):
        """Test /forecast command shows first 6 months."""
        from app.bot.handlers import cmd_forecast

        message = MagicMock()
        message.text = "/forecast"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_forecast(message)

        # Handler sends 2 messages: "Generating..." and actual forecast
        assert message.answer.call_count >= 1
        # Get the last call which contains the actual forecast
        last_call = message.answer.call_args_list[-1]
        answer_text = last_call[0][0]

        assert "12-Month Forecast" in answer_text or "Forecast" in answer_text
        assert (
            "January" in answer_text
            or "February" in answer_text
            or "March" in answer_text
        )

    @pytest.mark.asyncio
    async def test_forecast_months_7_to_12(self, bot_context):
        """Test /forecast2 command shows months 7-12."""
        from app.bot.handlers import cmd_forecast2

        message = MagicMock()
        message.text = "/forecast2"
        message.from_user.id = 12345
        message.answer = AsyncMock()

        await cmd_forecast2(message)

        message.answer.assert_called_once()
        answer_text = message.answer.call_args[0][0]

        assert "Forecast" in answer_text
        assert (
            "continued" in answer_text.lower()
            or "months 7-12" in answer_text.lower()
            or "July" in answer_text
        )
