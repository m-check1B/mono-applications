"""Tests for language detection and multi-language support."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestLanguageDetection:
    """Tests for language detection functions."""

    def test_detect_language_english(self):
        """Test detecting English text."""
        from app.services.language import detect_language

        text = "Hello, this is a test message in English. How are you today?"
        result = detect_language(text)
        assert result == "en"

    def test_detect_language_german(self):
        """Test detecting German text."""
        from app.services.language import detect_language

        text = "Guten Tag, das ist eine Testnachricht auf Deutsch. Wie geht es Ihnen?"
        result = detect_language(text)
        assert result == "de"

    def test_detect_language_spanish(self):
        """Test detecting Spanish text."""
        from app.services.language import detect_language

        text = "Hola, este es un mensaje de prueba en español. ¿Cómo estás?"
        result = detect_language(text)
        assert result == "es"

    def test_detect_language_french(self):
        """Test detecting French text."""
        from app.services.language import detect_language

        text = "Bonjour, ceci est un message test en français. Comment allez-vous?"
        result = detect_language(text)
        assert result == "fr"

    def test_detect_language_russian(self):
        """Test detecting Russian text."""
        from app.services.language import detect_language

        text = "Привет, это тестовое сообщение на русском языке. Как дела?"
        result = detect_language(text)
        assert result == "ru"

    def test_detect_language_czech(self):
        """Test detecting Czech text."""
        from app.services.language import detect_language

        text = "Dobrý den, toto je testovací zpráva v češtině. Jak se máte?"
        result = detect_language(text)
        assert result == "cs"

    def test_detect_language_short_text(self):
        """Test that short text returns None."""
        from app.services.language import detect_language

        text = "Hi"
        result = detect_language(text)
        assert result is None

    def test_detect_language_empty_text(self):
        """Test that empty text returns None."""
        from app.services.language import detect_language

        result = detect_language("")
        assert result is None

    def test_detect_language_none_text(self):
        """Test that None text returns None."""
        from app.services.language import detect_language

        result = detect_language(None)
        assert result is None


class TestLanguageWithConfidence:
    """Tests for language detection with confidence scores."""

    def test_detect_language_with_confidence(self):
        """Test language detection returns confidence scores."""
        from app.services.language import detect_language_with_confidence

        text = "Hello, this is a test message in English. How are you today?"
        results = detect_language_with_confidence(text)

        assert len(results) >= 1
        # First result should be the most likely language
        lang, prob = results[0]
        assert isinstance(lang, str)
        assert 0 <= prob <= 1

    def test_detect_language_with_confidence_short_text(self):
        """Test that short text returns empty list."""
        from app.services.language import detect_language_with_confidence

        text = "Hi"
        results = detect_language_with_confidence(text)
        assert results == []


class TestDominantLanguage:
    """Tests for dominant language detection across multiple messages."""

    def test_detect_dominant_language_english(self):
        """Test detecting dominant English messages."""
        from app.services.language import detect_dominant_language

        messages = [
            {"text": "Hello, how are you doing today?"},
            {"text": "I'm fine, thanks for asking!"},
            {"text": "That's great to hear!"},
            {"text": "See you later!"},
        ]

        result = detect_dominant_language(messages)
        assert result == "en"

    def test_detect_dominant_language_mixed(self):
        """Test detecting dominant language in mixed messages."""
        from app.services.language import detect_dominant_language

        messages = [
            {"text": "Guten Tag, wie geht es Ihnen heute?"},
            {"text": "Es geht mir gut, danke der Nachfrage!"},
            {"text": "Hello, how are you?"},
            {"text": "Das ist sehr gut zu hören!"},
            {"text": "Auf Wiedersehen!"},
        ]

        result = detect_dominant_language(messages)
        # German should dominate (4 German, 1 English)
        assert result == "de"

    def test_detect_dominant_language_empty(self):
        """Test empty message list returns default."""
        from app.services.language import detect_dominant_language, DEFAULT_LANGUAGE

        result = detect_dominant_language([])
        assert result == DEFAULT_LANGUAGE

    def test_detect_dominant_language_short_messages(self):
        """Test with only short messages returns default."""
        from app.services.language import detect_dominant_language, DEFAULT_LANGUAGE

        messages = [
            {"text": "Hi"},
            {"text": "OK"},
            {"text": "👍"},
        ]

        result = detect_dominant_language(messages)
        assert result == DEFAULT_LANGUAGE


class TestLanguageDistribution:
    """Tests for language distribution calculation."""

    def test_get_language_distribution(self):
        """Test getting language distribution."""
        from app.services.language import get_language_distribution

        messages = [
            {"text": "Hello, this is an English message. Nice to meet you."},
            {"text": "Guten Tag, das ist eine deutsche Nachricht."},
            {"text": "Another English message here for testing purposes."},
            {"text": "Hi"},  # Too short
        ]

        result = get_language_distribution(messages)

        assert "en" in result
        assert result["en"] >= 1
        assert "de" in result
        assert result["de"] >= 1
        assert "short" in result

    def test_get_language_distribution_empty(self):
        """Test empty message list."""
        from app.services.language import get_language_distribution

        result = get_language_distribution([])
        assert result == {}


class TestLanguageSupport:
    """Tests for language support utilities."""

    def test_get_language_name_english(self):
        """Test getting language name for English."""
        from app.services.language import get_language_name

        assert get_language_name("en") == "English"

    def test_get_language_name_czech(self):
        """Test getting language name for Czech."""
        from app.services.language import get_language_name

        assert get_language_name("cs") == "Czech"

    def test_get_language_name_auto(self):
        """Test getting language name for auto-detect."""
        from app.services.language import get_language_name

        assert get_language_name("auto") == "Auto-detect"

    def test_get_language_name_unknown(self):
        """Test getting language name for unknown code."""
        from app.services.language import get_language_name

        # Should return uppercase code for unknown languages
        result = get_language_name("xyz")
        assert result == "XYZ"

    def test_is_supported_language_true(self):
        """Test checking supported language."""
        from app.services.language import is_supported_language

        assert is_supported_language("en") is True
        assert is_supported_language("de") is True
        assert is_supported_language("cs") is True
        assert is_supported_language("auto") is True

    def test_is_supported_language_false(self):
        """Test checking unsupported language."""
        from app.services.language import is_supported_language

        assert is_supported_language("xyz") is False
        assert is_supported_language("invalid") is False


class TestLanguagePrompt:
    """Tests for language prompt generation."""

    def test_get_summary_language_prompt_auto(self):
        """Test prompt for auto-detect."""
        from app.services.language import get_summary_language_prompt

        result = get_summary_language_prompt("auto")
        assert "same language as the majority" in result

    def test_get_summary_language_prompt_specific(self):
        """Test prompt for specific language."""
        from app.services.language import get_summary_language_prompt

        result = get_summary_language_prompt("de")
        assert "German" in result

    def test_get_summary_language_prompt_english(self):
        """Test prompt for English."""
        from app.services.language import get_summary_language_prompt

        result = get_summary_language_prompt("en")
        assert "English" in result


class TestBufferLanguagePreference:
    """Tests for buffer language preference storage."""

    @pytest.mark.asyncio
    async def test_set_summary_language(self):
        """Test setting language preference."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = MagicMock()
        buffer.redis.set = AsyncMock(return_value=True)

        result = await buffer.set_summary_language(123456, "de")

        assert result is True
        buffer.redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_summary_language_set(self):
        """Test getting set language preference."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = MagicMock()
        buffer.redis.get = AsyncMock(return_value="de")

        result = await buffer.get_summary_language(123456)

        assert result == "de"

    @pytest.mark.asyncio
    async def test_get_summary_language_default(self):
        """Test getting default language preference."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = MagicMock()
        buffer.redis.get = AsyncMock(return_value=None)

        result = await buffer.get_summary_language(123456)

        assert result == "auto"

    @pytest.mark.asyncio
    async def test_get_summary_language_no_redis(self):
        """Test getting language preference without Redis."""
        from app.services.buffer import MessageBuffer

        buffer = MessageBuffer()
        buffer.redis = None

        result = await buffer.get_summary_language(123456)

        assert result == "auto"


class TestSummarizerLanguageSupport:
    """Tests for summarizer language support."""

    def test_summarize_messages_signature(self):
        """Test that summarize_messages accepts language parameter."""
        import inspect
        from app.services.summarizer import summarize_messages

        sig = inspect.signature(summarize_messages)
        params = list(sig.parameters.keys())

        assert "language" in params
        assert sig.parameters["language"].default == "auto"

    def test_summary_prompt_has_language_instruction(self):
        """Test that summary prompt includes language instruction."""
        from app.services.summarizer import SUMMARY_PROMPT_TEMPLATE

        assert "{language_instruction}" in SUMMARY_PROMPT_TEMPLATE
