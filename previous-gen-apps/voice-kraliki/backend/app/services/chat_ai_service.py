"""Simple AI Chat Service - Text-based AI provider integration.

This module provides a simplified interface for browser-based text chat
using OpenAI and Google Generative AI SDKs for text completions.
"""

import asyncio
import json
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    AsyncOpenAI = None
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available - install with: pip install openai")

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False
    logger.warning(
        "Google Generative AI SDK not available - install with: pip install google-generativeai"
    )


class AIProvider(str, Enum):
    """Supported AI providers for text chat."""

    OPENAI = "openai"
    GEMINI = "gemini"


class ChatMessage(BaseModel):
    """Chat message structure."""

    role: str
    content: str


class AIChatService:
    """Simple AI chat service using OpenAI and Gemini SDKs."""

    def __init__(self, default_provider: str = "openai"):
        """Initialize AI chat service.

        Args:
            default_provider: Default provider to use ("openai" or "gemini")
        """
        self.settings = get_settings()
        self.default_provider = default_provider
        self._openai_client: Any | None = None
        self._gemini_client: Any | None = None

        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize AI clients based on available API keys."""
        api_key_status = self.settings.validate_api_keys()

        if OPENAI_AVAILABLE and api_key_status["openai"] and self.settings.openai_api_key:
            try:
                self._openai_client = AsyncOpenAI(api_key=self.settings.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self._openai_client = None

        if GEMINI_AVAILABLE and api_key_status["gemini"] and self.settings.gemini_api_key:
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self._gemini_client = genai.GenerativeModel("gemini-2.0-flash-exp")
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._gemini_client = None

        if not self._openai_client and not self._gemini_client:
            logger.warning("No AI provider configured - chat will return placeholder responses")

    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available.

        Args:
            provider: Provider to check

        Returns:
            True if provider is available
        """
        if provider == "openai":
            return self._openai_client is not None
        elif provider == "gemini":
            return self._gemini_client is not None
        return False

    def get_available_providers(self) -> list[str]:
        """Get list of available providers.

        Returns:
            List of available providers
        """
        providers = []
        if self._openai_client:
            providers.append("openai")
        if self._gemini_client:
            providers.append("gemini")
        return providers

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict[str, Any]:
        """Generate AI response for chat messages.

        Args:
            messages: List of chat messages with 'role' and 'content'
            provider: Provider to use (defaults to configured default)
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary with response content and metadata
        """
        selected_provider = provider or self.default_provider

        if not self.is_provider_available(selected_provider):
            available = self.get_available_providers()
            if available:
                selected_provider = available[0]
                logger.info(f"Preferred provider unavailable, using {selected_provider}")
            else:
                logger.warning("No AI providers available - returning placeholder response")
                return {
                    "content": "I'm sorry, but AI services are currently unavailable. Please check your API key configuration.",
                    "provider": "none",
                    "model": "placeholder",
                    "usage": None,
                    "error": "No AI providers configured",
                }

        try:
            if selected_provider == "openai":
                return await self._generate_openai_response(messages, temperature, max_tokens)
            elif selected_provider == "gemini":
                return await self._generate_gemini_response(messages, temperature, max_tokens)
            else:
                logger.error(f"Unknown provider: {selected_provider}")
                return {
                    "content": "Unknown AI provider configured.",
                    "provider": selected_provider,
                    "model": "error",
                    "usage": None,
                    "error": "Unknown provider",
                }
        except Exception as e:
            logger.error(f"Error generating response with {selected_provider}: {e}")
            return {
                "content": f"I encountered an error: {str(e)}. Please try again.",
                "provider": selected_provider,
                "model": "error",
                "usage": None,
                "error": str(e),
            }

    async def _generate_openai_response(
        self, messages: list[dict[str, str]], temperature: float, max_tokens: int
    ) -> dict[str, Any]:
        """Generate response using OpenAI.

        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Response dictionary
        """
        if not self._openai_client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            response = await self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return {
                "content": response.choices[0].message.content,
                "provider": "openai",
                "model": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _generate_gemini_response(
        self, messages: list[dict[str, str]], temperature: float, max_tokens: int
    ) -> dict[str, Any]:
        """Generate response using Google Gemini.

        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Response dictionary
        """
        if not self._gemini_client:
            raise RuntimeError("Gemini client not initialized")

        try:
            if genai:
                genai.configure(api_key=self.settings.gemini_api_key)

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            chat_history = [
                {"role": msg["role"], "parts": [msg["content"]]} for msg in messages[:-1]
            ]

            chat = self._gemini_client.start_chat(history=chat_history)

            response = await asyncio.to_thread(
                chat.send_message, messages[-1]["content"], generation_config=generation_config
            )

            return {
                "content": response.text,
                "provider": "gemini",
                "model": "gemini-2.0-flash-exp",
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                },
                "finish_reason": response.candidates[0].finish_reason.name
                if response.candidates
                else None,
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def analyze_intent_and_sentiment(self, message: str) -> dict[str, Any]:
        """Analyze intent and sentiment of a message.

        Args:
            message: User message

        Returns:
            Dictionary with intent, sentiment, and confidence
        """
        analysis_prompt = f"""Analyze the following user message and return a JSON response with these fields:
- intent: One of [inquiry, question, help_request, support, complaint, greeting, farewell, unknown]
- sentiment: One of [positive, negative, neutral]
- confidence: A number between 0.0 and 1.0

User message: "{message}"

Return only valid JSON."""

        try:
            response = await self.generate_response(
                messages=[{"role": "user", "content": analysis_prompt}], temperature=0.3
            )

            try:
                result = json.loads(response["content"])
                return {
                    "intent": result.get("intent", "inquiry"),
                    "sentiment": result.get("sentiment", "neutral"),
                    "confidence": float(result.get("confidence", 0.5)),
                }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI analysis as JSON: {response['content']}")
                return {"intent": "inquiry", "sentiment": "neutral", "confidence": 0.5}
        except Exception as e:
            logger.error(f"Error in intent/sentiment analysis: {e}")
            return {"intent": "inquiry", "sentiment": "neutral", "confidence": 0.5}


# Global instance
_chat_service: AIChatService | None = None


def get_chat_service() -> AIChatService:
    """Get global chat service instance.

    Returns:
        AIChatService instance
    """
    global _chat_service
    if _chat_service is None:
        _chat_service = AIChatService()
    return _chat_service
