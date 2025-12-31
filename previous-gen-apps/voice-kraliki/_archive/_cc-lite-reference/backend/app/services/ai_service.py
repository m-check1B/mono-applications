"""AI service - OpenAI, Anthropic, and Deepgram integration"""

from typing import Optional, AsyncGenerator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from deepgram import DeepgramClient

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """Service for AI operations (LLMs and voice)"""

    def __init__(self):
        """Initialize AI clients"""
        self.openai_client = None
        self.anthropic_client = None
        self.deepgram_client = None

        # Initialize OpenAI if configured
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")

        # Initialize Anthropic if configured
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic client initialized")

        # Initialize Deepgram if configured
        if settings.DEEPGRAM_API_KEY:
            self.deepgram_client = DeepgramClient(settings.DEEPGRAM_API_KEY)
            logger.info("Deepgram client initialized")

    # OpenAI Methods
    async def openai_chat_completion(
        self,
        messages: list[dict],
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat completion using OpenAI

        Args:
            messages: List of message dicts with role and content
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response text

        Raises:
            ValueError: If OpenAI not configured
        """
        if not self.openai_client:
            raise ValueError("OpenAI not configured")

        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI chat completion error: {e}")
            raise

    async def openai_stream_completion(
        self,
        messages: list[dict],
        model: str = "gpt-4",
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion using OpenAI

        Args:
            messages: List of message dicts
            model: Model to use
            temperature: Sampling temperature

        Yields:
            Response chunks

        Raises:
            ValueError: If OpenAI not configured
        """
        if not self.openai_client:
            raise ValueError("OpenAI not configured")

        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI stream error: {e}")
            raise

    # Anthropic Methods
    async def anthropic_chat_completion(
        self,
        messages: list[dict],
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Generate chat completion using Anthropic

        Args:
            messages: List of message dicts
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature

        Returns:
            Generated response text

        Raises:
            ValueError: If Anthropic not configured
        """
        if not self.anthropic_client:
            raise ValueError("Anthropic not configured")

        try:
            response = await self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise

    # Deepgram Methods
    async def deepgram_transcribe(
        self,
        audio_url: str,
        language: str = "en"
    ) -> dict:
        """
        Transcribe audio using Deepgram

        Args:
            audio_url: URL to audio file
            language: Language code

        Returns:
            Transcription result

        Raises:
            ValueError: If Deepgram not configured
        """
        if not self.deepgram_client:
            raise ValueError("Deepgram not configured")

        try:
            options = {
                "punctuate": True,
                "diarize": True,
                "language": language,
                "model": "nova-2"
            }

            response = await self.deepgram_client.transcription.prerecorded(
                {"url": audio_url},
                options
            )

            transcript = response["results"]["channels"][0]["alternatives"][0]

            return {
                "transcript": transcript["transcript"],
                "confidence": transcript["confidence"],
                "words": transcript.get("words", [])
            }

        except Exception as e:
            logger.error(f"Deepgram transcription error: {e}")
            raise

    def get_available_providers(self) -> dict:
        """
        Get list of available AI providers

        Returns:
            Dict of provider availability
        """
        return {
            "openai": self.openai_client is not None,
            "anthropic": self.anthropic_client is not None,
            "deepgram": self.deepgram_client is not None
        }


# Singleton instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """Expose the shared AI service instance."""
    return ai_service
