"""Tests for chat AI service integration."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.services.chat_ai_service import AIChatService, AIProvider


class TestAIChatService:
    """Test cases for AI Chat Service."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings."""
        settings = Mock()
        settings.openai_api_key = "test_openai_key"
        settings.gemini_api_key = "test_gemini_key"
        settings.validate_api_keys.return_value = {
            "openai": True,
            "gemini": True,
            "deepgram": False,
        }
        return settings

    @pytest.fixture
    def chat_service(self, mock_settings):
        """Create chat service with mocked settings."""
        with patch("app.services.chat_ai_service.get_settings", return_value=mock_settings):
            service = AIChatService()
            return service

    @pytest.mark.asyncio
    async def test_provider_availability(self, chat_service):
        """Test checking provider availability."""
        assert chat_service.is_provider_available("openai") is True
        assert chat_service.is_provider_available("gemini") is True
        assert chat_service.is_provider_available("unknown") is False

    def test_get_available_providers(self, chat_service):
        """Test getting available providers list."""
        providers = chat_service.get_available_providers()
        assert "openai" in providers
        assert "gemini" in providers

    @pytest.mark.asyncio
    async def test_generate_response_openai(self, chat_service, mock_settings):
        """Test generating response with OpenAI."""
        messages = [{"role": "user", "content": "Hello"}]

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Hi there!"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(chat_service, "_openai_client", mock_client):
            response = await chat_service.generate_response(messages=messages, provider="openai")

            assert response["content"] == "Hi there!"
            assert response["provider"] == "openai"
            assert response["usage"]["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_no_providers_fallback(self, chat_service):
        """Test fallback when no providers available."""
        chat_service._openai_client = None
        chat_service._gemini_client = None

        response = await chat_service.generate_response(
            messages=[{"role": "user", "content": "Hello"}]
        )

        assert response["provider"] == "none"
        assert "unavailable" in response["content"].lower()

    @pytest.mark.asyncio
    async def test_intent_sentiment_analysis(self, chat_service):
        """Test intent and sentiment analysis."""
        message = "I need help with my order"

        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(
                    content='{"intent": "help_request", "sentiment": "neutral", "confidence": 0.95}'
                )
            )
        ]

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(chat_service, "_openai_client", mock_client):
            result = await chat_service.analyze_intent_and_sentiment(message)

            assert result["intent"] == "help_request"
            assert result["sentiment"] == "neutral"
            assert result["confidence"] == 0.95

    def test_global_chat_service_singleton(self):
        """Test that get_chat_service returns singleton."""
        with patch("app.services.chat_ai_service.get_settings"):
            from app.services.chat_ai_service import get_chat_service

            service1 = get_chat_service()
            service2 = get_chat_service()

            assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
