"""Test fixtures for Sense by Kraliki Bot."""
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_gemini():
    """Mock Gemini AI client."""
    # Create mock module and add to sys.modules
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(
        return_value=MagicMock(text="AI generated response")
    )
    mock_genai.GenerativeModel.return_value = mock_model

    # Insert into sys.modules to make import work
    sys.modules['google.generativeai'] = mock_genai

    yield mock_genai

    # Cleanup
    if 'google.generativeai' in sys.modules:
        del sys.modules['google.generativeai']


@pytest.fixture
def mock_message():
    """Create mock Telegram message."""
    message = MagicMock()
    message.text = "/start"
    message.chat = MagicMock()
    message.chat.id = 12345
    message.chat.type = "private"
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    return message


@pytest.fixture
def mock_callback():
    """Create mock callback query."""
    callback = MagicMock()
    callback.data = "test_callback"
    callback.from_user = MagicMock()
    callback.from_user.id = 12345
    callback.message = MagicMock()
    callback.message.chat = MagicMock()
    callback.message.chat.id = 12345
    callback.answer = AsyncMock()
    callback.message.edit_text = AsyncMock()
    return callback
