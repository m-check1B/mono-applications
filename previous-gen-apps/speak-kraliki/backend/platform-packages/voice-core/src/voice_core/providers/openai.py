"""OpenAI Realtime API provider using raw WebSocket.

This module implements the RealtimeEndToEndProvider protocol for OpenAI's
Realtime API with native audio streaming support.

Uses raw WebSocket (SDK Realtime support is still beta).
Kept as secondary/hedge option - primary is Gemini Live.
"""

import asyncio
import base64
import json
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

# OpenAI Realtime WebSocket URL
WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"
DEFAULT_MODEL = "gpt-4o-realtime-preview"


class OpenAIRealtimeProvider(BaseProvider):
    """OpenAI Realtime API provider.

    Secondary voice provider - use as hedge if Gemini has issues.
    Uses raw WebSocket connection for bidirectional audio streaming.
    """

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize OpenAI Realtime provider.

        Args:
            api_key: OpenAI API key
            model: Model ID (defaults to gpt-4o-realtime-preview)
        """
        super().__init__(api_key)
        self._model = model or DEFAULT_MODEL
        self._ws: Any = None
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()
        self._receive_task: asyncio.Task | None = None

    @property
    def capabilities(self) -> ProviderCapabilities:
        """OpenAI Realtime capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=False,  # Audio only, no images
            supports_function_calling=True,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],
            max_session_duration=3600,  # 60 minutes
            cost_tier="premium",  # OpenAI is more expensive
        )

    async def connect(self, config: SessionConfig) -> None:
        """Establish WebSocket connection to OpenAI Realtime API.

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

            # Import websockets
            try:
                import websockets
            except ImportError:
                raise ImportError(
                    "websockets library required. Install with: pip install websockets"
                )

            # Build URL with model
            model_id = config.model_id or self._model
            url = f"{WEBSOCKET_URL}?model={model_id}"

            # Connect with auth header
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "OpenAI-Beta": "realtime=v1",
            }
            self._ws = await websockets.connect(url, extra_headers=headers)

            # Start receiving events
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Send session configuration
            await self._setup_session(config)

            self._state = SessionState.CONNECTED
            logger.info(f"Connected to OpenAI Realtime API (model={model_id})")

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(f"Failed to connect to OpenAI: {e}")
            raise ConnectionError(f"OpenAI connection failed: {e}") from e

    async def _setup_session(self, config: SessionConfig) -> None:
        """Send session configuration to OpenAI."""
        session_config: dict[str, Any] = {
            "modalities": ["text", "audio"],
            "voice": "alloy",  # Default voice
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
            },
        }

        if config.system_prompt:
            session_config["instructions"] = config.system_prompt

        if config.temperature:
            session_config["temperature"] = config.temperature

        if config.tools:
            session_config["tools"] = config.tools

        await self._send_message({
            "type": "session.update",
            "session": session_config,
        })

    async def _receive_loop(self) -> None:
        """Background task to receive WebSocket messages."""
        if not self._ws:
            return

        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    event = self._parse_message(data)
                    if event:
                        await self._event_queue.put(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse OpenAI message: {e}")
                except Exception as e:
                    logger.error(f"Error processing OpenAI event: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"WebSocket receive loop error: {e}")
            self._state = SessionState.ERROR

    def _parse_message(self, data: dict[str, Any]) -> ProviderEvent | None:
        """Parse OpenAI message into unified ProviderEvent."""
        event_type = data.get("type", "")

        # Session created
        if event_type == "session.created":
            return ProviderEvent(type="session.created", data={"status": "ready"})

        # Audio response
        if event_type == "response.audio.delta":
            audio_b64 = data.get("delta", "")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                return ProviderEvent(
                    type="audio.output",
                    data={
                        "audio": audio_bytes,
                        "format": "pcm16",
                        "sample_rate": 24000,
                    },
                )

        # Text/transcript
        if event_type == "response.audio_transcript.delta":
            return ProviderEvent(
                type="text.output",
                data={
                    "text": data.get("delta", ""),
                    "role": "assistant",
                },
            )

        # User transcript
        if event_type == "conversation.item.input_audio_transcription.completed":
            return ProviderEvent(
                type="text.output",
                data={
                    "text": data.get("transcript", ""),
                    "role": "user",
                },
            )

        # Function call
        if event_type == "response.function_call_arguments.done":
            return ProviderEvent(
                type="function_call",
                data={
                    "call_id": data.get("call_id", ""),
                    "name": data.get("name", ""),
                    "arguments": json.loads(data.get("arguments", "{}")),
                },
            )

        # Response started/completed
        if event_type == "response.created":
            return ProviderEvent(type="turn.started", data={})

        if event_type == "response.done":
            return ProviderEvent(type="turn.completed", data={})

        # Error
        if event_type == "error":
            logger.error(f"OpenAI error: {data.get('error', {})}")
            return ProviderEvent(type="error", data=data.get("error", {}))

        return None

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API."""
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

            # Close WebSocket
            if self._ws:
                await self._ws.close()
                self._ws = None

            self._state = SessionState.DISCONNECTED
            logger.info("Disconnected from OpenAI Realtime API")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._state = SessionState.ERROR

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to OpenAI.

        Args:
            audio: Audio chunk (must be PCM16 format)

        Raises:
            RuntimeError: If not connected
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot send audio in state {self._state}")

        self._validate_audio_format(audio.format)
        self._state = SessionState.ACTIVE

        # Encode to base64
        audio_b64 = base64.b64encode(audio.data).decode("utf-8")

        await self._send_message({
            "type": "input_audio_buffer.append",
            "audio": audio_b64,
        })

    async def send_text(self, message: TextMessage) -> None:
        """Send text input to OpenAI.

        Args:
            message: Text message to send

        Raises:
            RuntimeError: If not connected
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot send text in state {self._state}")

        self._state = SessionState.ACTIVE

        # Add conversation item
        await self._send_message({
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": message.content}],
            },
        })

        # Trigger response
        await self._send_message({"type": "response.create"})

    async def receive_events(self) -> AsyncGenerator[ProviderEvent, None]:
        """Receive events from OpenAI.

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
        """Send function execution result back to OpenAI.

        Args:
            call_id: Function call ID
            result: Function execution result
        """
        if self._state != SessionState.ACTIVE:
            raise RuntimeError(f"Cannot send function result in state {self._state}")

        # Add function output
        await self._send_message({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result),
            },
        })

        # Trigger response
        await self._send_message({"type": "response.create"})

    async def _send_message(self, message: dict[str, Any]) -> None:
        """Send message to OpenAI WebSocket."""
        if not self._ws:
            raise RuntimeError("WebSocket not connected")

        try:
            await self._ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to OpenAI: {e}")
            raise


def create_openai_provider(api_key: str, model: str | None = None) -> OpenAIRealtimeProvider:
    """Factory function to create OpenAI Realtime provider.

    Args:
        api_key: OpenAI API key
        model: Optional model override

    Returns:
        OpenAIRealtimeProvider: Configured provider instance
    """
    return OpenAIRealtimeProvider(api_key=api_key, model=model)
