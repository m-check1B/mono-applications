"""Google Gemini Live API provider using official google-genai SDK.

This module implements the RealtimeEndToEndProvider protocol for Google's
Gemini Live API with native audio streaming support.

Uses the official google-genai SDK for simplified connection management.
"""

import asyncio
import logging
from typing import Any, AsyncGenerator

from voice_core.base import (
    AudioChunk,
    AudioFormat,
    BaseProvider,
    ProviderCapabilities,
    ProviderEvent,
    SessionConfig,
    SessionState,
    TextMessage,
)

logger = logging.getLogger(__name__)

# Gemini Live 2.5 Flash Native Audio - December 2025 GA release
# See: https://ai.google.dev/gemini-api/docs/models
DEFAULT_MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"


class GeminiLiveProvider(BaseProvider):
    """Google Gemini Live API provider using official SDK.

    Supports real-time multimodal conversation with native audio streaming.
    """

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Gemini Live provider.

        Args:
            api_key: Google AI API key
            model: Model ID (defaults to Gemini 2.5 Flash native audio)
        """
        super().__init__(api_key)
        self._model = model or DEFAULT_MODEL
        self._session: Any = None
        self._client: Any = None
        self._receive_task: asyncio.Task | None = None
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Gemini Live capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=True,
            supports_function_calling=True,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],
            max_session_duration=3600,  # 60 minutes
            cost_tier="standard",
        )

    async def connect(self, config: SessionConfig) -> None:
        """Establish connection to Gemini Live API.

        Args:
            config: Session configuration

        Raises:
            ConnectionError: If connection fails
        """
        if self._state != SessionState.IDLE:
            raise RuntimeError(f"Cannot connect from state {self._state}")

        try:
            self._state = SessionState.CONNECTING
            self._config = config
            self._validate_audio_format(config.audio_format)

            # Import google-genai SDK
            try:
                from google import genai
            except ImportError:
                raise ImportError(
                    "google-genai library required. Install with: pip install google-genai"
                )

            # Create client
            self._client = genai.Client(api_key=self._api_key)

            # Build Live API config
            live_config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {"voice_name": "Aoede"}
                    }
                },
            }

            if config.system_prompt:
                live_config["system_instruction"] = config.system_prompt

            if config.tools:
                live_config["tools"] = self._convert_tools(config.tools)

            # Connect to Live API
            model_id = config.model_id or self._model
            self._session = await self._client.aio.live.connect(
                model=model_id,
                config=live_config,
            )

            # Start receiving events
            self._receive_task = asyncio.create_task(self._receive_loop())

            self._state = SessionState.CONNECTED
            logger.info(f"Connected to Gemini Live API (model={model_id})")

            # Emit session created event
            await self._event_queue.put(
                ProviderEvent(type="session.created", data={"status": "ready"})
            )

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(f"Failed to connect to Gemini: {e}")
            raise ConnectionError(f"Gemini connection failed: {e}") from e

    def _convert_tools(self, openai_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI-style tools to Gemini function declarations."""
        gemini_tools = []
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                gemini_tools.append({
                    "function_declarations": [{
                        "name": func.get("name"),
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {}),
                    }]
                })
        return gemini_tools

    async def _receive_loop(self) -> None:
        """Background task to receive events from Gemini."""
        if not self._session:
            return

        try:
            async for response in self._session.receive():
                try:
                    event = self._parse_response(response)
                    if event:
                        await self._event_queue.put(event)
                except Exception as e:
                    logger.error(f"Error processing Gemini response: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Gemini receive loop error: {e}")
            self._state = SessionState.ERROR

    def _parse_response(self, response: Any) -> ProviderEvent | None:
        """Parse Gemini response into unified ProviderEvent."""
        # Handle server content
        if hasattr(response, "server_content") and response.server_content:
            content = response.server_content

            # Check turn status
            if hasattr(content, "turn_complete"):
                if content.turn_complete:
                    return ProviderEvent(type="turn.completed", data={})

            # Extract model turn parts
            if hasattr(content, "model_turn") and content.model_turn:
                parts = getattr(content.model_turn, "parts", [])

                for part in parts:
                    # Audio output
                    if hasattr(part, "inline_data") and part.inline_data:
                        data = part.inline_data
                        if hasattr(data, "data") and isinstance(data.data, bytes):
                            return ProviderEvent(
                                type="audio.output",
                                data={
                                    "audio": data.data,
                                    "format": "pcm16",
                                    "sample_rate": 24000,
                                },
                            )

                    # Text output
                    if hasattr(part, "text") and part.text:
                        return ProviderEvent(
                            type="text.output",
                            data={"text": part.text, "role": "assistant"},
                        )

                    # Function call
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        return ProviderEvent(
                            type="function_call",
                            data={
                                "call_id": getattr(fc, "id", ""),
                                "name": getattr(fc, "name", ""),
                                "arguments": getattr(fc, "args", {}),
                            },
                        )

        # Handle tool call cancellation
        if hasattr(response, "tool_call_cancellation"):
            return ProviderEvent(
                type="function_call.cancelled",
                data=response.tool_call_cancellation,
            )

        return None

    async def disconnect(self) -> None:
        """Disconnect from Gemini Live API."""
        if self._state == SessionState.DISCONNECTED:
            return

        self._state = SessionState.DISCONNECTING

        try:
            # Cancel receive task
            if self._receive_task:
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass

            # Close session
            if self._session:
                await self._session.close()
                self._session = None

            self._state = SessionState.DISCONNECTED
            logger.info("Disconnected from Gemini Live API")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._state = SessionState.ERROR

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to Gemini.

        Args:
            audio: Audio chunk (must be PCM16 format)

        Raises:
            RuntimeError: If not connected
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot send audio in state {self._state}")

        if not self._session:
            raise RuntimeError("No active session")

        self._validate_audio_format(audio.format)
        self._state = SessionState.ACTIVE

        # Send audio using SDK
        await self._session.send_realtime_input(audio=audio.data)

    async def send_text(self, message: TextMessage) -> None:
        """Send text input to Gemini.

        Args:
            message: Text message to send

        Raises:
            RuntimeError: If not connected
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot send text in state {self._state}")

        if not self._session:
            raise RuntimeError("No active session")

        self._state = SessionState.ACTIVE

        # Send text using SDK
        await self._session.send_client_content(
            turns=[{"role": "user", "parts": [{"text": message.content}]}],
            turn_complete=True,
        )

    async def receive_events(self) -> AsyncGenerator[ProviderEvent, None]:
        """Receive events from Gemini.

        Yields:
            ProviderEvent: Audio, text, function call, or other events
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot receive events in state {self._state}")

        self._state = SessionState.ACTIVE

        while self._state == SessionState.ACTIVE:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(), timeout=0.1
                )
                yield event

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error receiving event: {e}")
                self._state = SessionState.ERROR
                break

    async def handle_function_result(
        self, call_id: str, result: dict[str, Any]
    ) -> None:
        """Send function execution result back to Gemini.

        Args:
            call_id: Function call ID
            result: Function execution result
        """
        if self._state != SessionState.ACTIVE:
            raise RuntimeError(f"Cannot send function result in state {self._state}")

        if not self._session:
            raise RuntimeError("No active session")

        # Send function response using SDK
        await self._session.send_tool_response(
            function_responses=[{"id": call_id, "response": result}]
        )


def create_gemini_provider(api_key: str, model: str | None = None) -> GeminiLiveProvider:
    """Factory function to create Gemini provider.

    Args:
        api_key: Google AI API key
        model: Optional model override

    Returns:
        GeminiLiveProvider: Configured provider instance
    """
    return GeminiLiveProvider(api_key=api_key, model=model)
