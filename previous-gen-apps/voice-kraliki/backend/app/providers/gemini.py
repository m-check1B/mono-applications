"""Google Gemini Live API provider implementation.

This module implements the RealtimeEndToEndProvider protocol for Google's
Gemini Live API with native audio streaming support.
"""

import asyncio
import base64
import json
import time
from collections.abc import AsyncGenerator
from typing import Any

from app.logging.structured_logger import get_logger
from app.monitoring.prometheus_metrics import (
    track_ai_provider_error,
    track_ai_provider_request,
)
from app.patterns.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
)
from app.providers.base import (
    AudioChunk,
    AudioFormat,
    BaseProvider,
    ProviderCapabilities,
    ProviderEvent,
    SessionConfig,
    SessionState,
    TextMessage,
)

logger = get_logger(__name__)

# Auto-reconnection constants
MAX_RECONNECT_ATTEMPTS = 5
INITIAL_BACKOFF_DELAY = 1.0  # seconds


class GeminiLiveProvider(BaseProvider):
    """Google Gemini Live API provider.

    Supports real-time multimodal conversation with native audio streaming.
    Uses WebSocket connection for bidirectional streaming.
    """

    # Gemini Live WebSocket endpoint for bidirectional content generation
    WEBSOCKET_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"
    # Gemini 2.5 Flash Native Audio - supports real-time voice with native audio processing
    # Available via Google AI API (preview) as of December 2025
    # Features: Low latency, emotional intelligence, 30+ voices, 24+ languages
    DEFAULT_MODEL = "models/gemini-2.5-flash-preview-native-audio-dialog"
    # Fallback model for standard API keys without native audio access
    FALLBACK_MODEL = "models/gemini-2.0-flash-exp"

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Gemini Live provider.

        Args:
            api_key: Google AI API key
            model: Model ID (defaults to Gemini 2.5 Flash)
        """
        super().__init__(api_key)
        self._model = model or self.DEFAULT_MODEL
        self._ws: Any | None = None
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()
        self._receive_task: asyncio.Task | None = None
        self._session_id: str | None = None

        # Auto-reconnection state
        self._reconnect_attempts = 0
        self._is_reconnecting = False
        self._should_reconnect = True
        self._connection_healthy = False
        self._last_message_time: float = 0

        # Circuit breaker for cascade failure protection
        self._circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                name="gemini_provider",
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60
            ),
            provider_id="gemini"
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Gemini Live capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=True,  # Gemini supports images too
            supports_function_calling=True,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],
            max_session_duration=3600,  # 60 minutes
            cost_tier="standard",
        )

    async def connect(self, config: SessionConfig) -> None:
        """Establish WebSocket connection to Gemini Live API.

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

            # Build WebSocket URL with API key
            url = f"{self.WEBSOCKET_URL}?key={self._api_key}"

            # Connect to Gemini
            self._ws = await websockets.connect(url)

            # Start receiving events
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Send initial setup message
            await self._setup_session(config)

            self._state = SessionState.CONNECTED
            logger.info(
                "Connected to Gemini Live API",
                event_type="connection.established",
                provider="gemini",
                model=self._model,
                session_id=str(self._session_id) if self._session_id else None
            )

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(
                "Failed to connect to Gemini",
                event_type="connection.failed",
                provider="gemini",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise ConnectionError(f"Gemini connection failed: {e}") from e

    async def _setup_session(self, config: SessionConfig) -> None:
        """Send initial setup configuration to Gemini.

        Args:
            config: Session configuration
        """
        setup_msg = {
            "setup": {
                "model": config.model_id or self._model,
                "generation_config": {
                    "temperature": config.temperature,
                    "response_modalities": ["AUDIO"],
                    "speech_config": {
                        "voice_config": {"prebuilt_voice_config": {"voice_name": "Aoede"}}
                    },
                },
            }
        }

        if config.system_prompt:
            setup_msg["setup"]["system_instruction"] = {
                "parts": [{"text": config.system_prompt}]
            }

        if config.tools:
            # Convert OpenAI-style tools to Gemini format
            setup_msg["setup"]["tools"] = self._convert_tools(config.tools)

        await self._send_message(setup_msg)

    def _convert_tools(self, openai_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI-style tools to Gemini function declarations.

        Args:
            openai_tools: OpenAI tool definitions

        Returns:
            list: Gemini function declarations
        """
        gemini_tools = []
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                gemini_tools.append(
                    {
                        "function_declarations": [
                            {
                                "name": func.get("name"),
                                "description": func.get("description", ""),
                                "parameters": func.get("parameters", {}),
                            }
                        ]
                    }
                )
        return gemini_tools

    async def _receive_loop(self) -> None:
        """Background task to receive and queue WebSocket messages."""
        if not self._ws:
            return

        try:
            async for message in self._ws:
                try:
                    # Update connection health tracking
                    import time
                    self._last_message_time = time.time()
                    self._connection_healthy = True

                    data = json.loads(message)
                    event = self._parse_message(data)
                    if event:
                        await self._event_queue.put(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini message: {e}")
                except Exception as e:
                    logger.error(f"Error processing Gemini event: {e}")
        except Exception as e:
            logger.error(f"WebSocket receive loop error: {e}")
            self._connection_healthy = False

            # Attempt auto-reconnection if enabled and in active state
            if self._should_reconnect and self._state in (SessionState.CONNECTED, SessionState.ACTIVE):
                await self._attempt_reconnection()
            else:
                self._state = SessionState.ERROR

    def _parse_message(self, data: dict[str, Any]) -> ProviderEvent | None:
        """Parse Gemini message into unified ProviderEvent.

        Args:
            data: Raw message data from Gemini

        Returns:
            ProviderEvent or None: Unified event
        """
        # Handle setup complete
        if "setupComplete" in data:
            return ProviderEvent(type="session.created", data={"status": "ready"})

        # Handle server content (responses)
        if "serverContent" in data:
            content = data["serverContent"]

            # Check if model is processing (turn in progress)
            if content.get("turnComplete") is False:
                return ProviderEvent(type="turn.started", data={})

            if content.get("turnComplete") is True:
                return ProviderEvent(type="turn.completed", data={})

            # Extract parts from the content
            model_turn = content.get("modelTurn", {})
            parts = model_turn.get("parts", [])

            for part in parts:
                # Audio response
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    mime_type = inline_data.get("mimeType", "")
                    if "audio" in mime_type:
                        audio_b64 = inline_data.get("data", "")
                        audio_bytes = base64.b64decode(audio_b64)
                        return ProviderEvent(
                            type="audio.output",
                            data={
                                "audio": audio_bytes,
                                "format": "pcm16",
                                "sample_rate": 24000,
                            },
                        )

                # Text response
                if "text" in part:
                    return ProviderEvent(
                        type="text.output",
                        data={
                            "text": part["text"],
                            "role": "assistant",
                        },
                    )

                # Function call
                if "functionCall" in part:
                    func_call = part["functionCall"]
                    return ProviderEvent(
                        type="function_call",
                        data={
                            "call_id": func_call.get("id", ""),
                            "name": func_call.get("name", ""),
                            "arguments": func_call.get("args", {}),
                        },
                    )

        # Handle tool call cancellation
        if "toolCallCancellation" in data:
            return ProviderEvent(
                type="function_call.cancelled",
                data=data["toolCallCancellation"],
            )

        return None

    async def disconnect(self) -> None:
        """Disconnect from Gemini Live API."""
        if self._state == SessionState.DISCONNECTED:
            return

        # Disable auto-reconnection when explicitly disconnecting
        self._should_reconnect = False
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
            self._connection_healthy = False
            logger.info("Disconnected from Gemini Live API")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._state = SessionState.ERROR

    async def _attempt_reconnection(self) -> None:
        """Attempt to reconnect with exponential backoff.

        This method is called automatically when a connection is lost.
        It will try to reconnect up to MAX_RECONNECT_ATTEMPTS times with
        exponentially increasing delays.
        """
        if self._is_reconnecting:
            logger.warning("Reconnection already in progress")
            return

        self._is_reconnecting = True
        original_state = self._state

        try:
            while self._reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
                self._reconnect_attempts += 1
                backoff_delay = INITIAL_BACKOFF_DELAY * (2 ** (self._reconnect_attempts - 1))

                logger.info(
                    "Reconnection attempt starting",
                    event_type="reconnection.attempt",
                    provider="gemini",
                    attempt=self._reconnect_attempts,
                    max_attempts=MAX_RECONNECT_ATTEMPTS,
                    backoff_delay=backoff_delay
                )

                # Emit reconnection attempt event
                await self._event_queue.put(
                    ProviderEvent(
                        type="connection.reconnecting",
                        data={
                            "attempt": self._reconnect_attempts,
                            "max_attempts": MAX_RECONNECT_ATTEMPTS,
                            "backoff_delay": backoff_delay,
                        },
                    )
                )

                # Wait for backoff delay
                await asyncio.sleep(backoff_delay)

                # Attempt reconnection
                try:
                    await self._reconnect()

                    # Success!
                    logger.info(
                        "Reconnection successful",
                        event_type="reconnection.success",
                        provider="gemini",
                        attempts=self._reconnect_attempts
                    )

                    # Emit reconnection success event
                    await self._event_queue.put(
                        ProviderEvent(
                            type="connection.reconnected",
                            data={"attempts": self._reconnect_attempts},
                        )
                    )

                    # Reset reconnection state
                    self._reconnect_attempts = 0
                    self._is_reconnecting = False
                    self._connection_healthy = True
                    return

                except Exception as e:
                    logger.warning(
                        "Reconnection attempt failed",
                        event_type="reconnection.attempt_failed",
                        provider="gemini",
                        attempt=self._reconnect_attempts,
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )

                    if self._reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
                        logger.error(
                            f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached"
                        )
                        break

            # All reconnection attempts failed
            logger.error(
                "Failed to reconnect after maximum attempts",
                event_type="reconnection.failed",
                provider="gemini",
                total_attempts=self._reconnect_attempts
            )
            await self._event_queue.put(
                ProviderEvent(
                    type="connection.failed",
                    data={
                        "attempts": self._reconnect_attempts,
                        "reason": "Max reconnection attempts exceeded",
                    },
                )
            )
            self._state = SessionState.ERROR

        finally:
            self._is_reconnecting = False

    async def _reconnect(self) -> None:
        """Perform actual reconnection.

        This method handles the low-level reconnection logic while preserving
        session state and configuration.

        Raises:
            Exception: If reconnection fails
        """
        if not self._config:
            raise RuntimeError("Cannot reconnect: no configuration saved")

        # Clean up existing connection
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None

        # Import websockets
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets library required. Install with: pip install websockets"
            )

        # Reconnect to Gemini
        url = f"{self.WEBSOCKET_URL}?key={self._api_key}"
        self._ws = await websockets.connect(url)

        # Restart receive loop
        self._receive_task = asyncio.create_task(self._receive_loop())

        # Re-send session setup with preserved configuration
        await self._setup_session(self._config)

        # Restore state
        self._state = SessionState.CONNECTED if self._state != SessionState.ACTIVE else SessionState.ACTIVE
        logger.info(
            "Gemini WebSocket reconnected and session restored",
            event_type="session.restored",
            provider="gemini"
        )

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to Gemini.

        Args:
            audio: Audio chunk (must be PCM16 format)

        Raises:
            RuntimeError: If not connected
            ValueError: If audio format is not supported
            CircuitBreakerOpenError: If circuit breaker is open
        """
        if self._state != SessionState.CONNECTED:
            raise RuntimeError(f"Cannot send audio in state {self._state}")

        self._validate_audio_format(audio.format)

        start_time = time.time()
        try:
            async with self._circuit_breaker:
                # Encode audio to base64
                audio_b64 = base64.b64encode(audio.data).decode("utf-8")

                # Send as realtime input
                await self._send_message(
                    {
                        "realtimeInput": {
                            "mediaChunks": [
                                {
                                    "mimeType": "audio/pcm",
                                    "data": audio_b64,
                                }
                            ]
                        }
                    }
                )

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="gemini",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(
                "Circuit breaker OPEN for Gemini",
                event_type="circuit_breaker.open",
                provider="gemini",
                error_type="CircuitBreakerOpen",
                error_message=str(e)
            )
            track_ai_provider_error(
                provider="gemini",
                error_type="CircuitBreakerOpen"
            )
            raise
        except Exception as e:
            track_ai_provider_error(
                provider="gemini",
                error_type=type(e).__name__
            )
            raise

    async def send_text(self, message: TextMessage) -> None:
        """Send text input to Gemini.

        Args:
            message: Text message to send

        Raises:
            RuntimeError: If not connected
            CircuitBreakerOpenError: If circuit breaker is open
        """
        if self._state != SessionState.CONNECTED:
            raise RuntimeError(f"Cannot send text in state {self._state}")

        start_time = time.time()
        try:
            async with self._circuit_breaker:
                # Send as client content
                await self._send_message(
                    {
                        "clientContent": {
                            "turns": [
                                {
                                    "role": "user",
                                    "parts": [{"text": message.content}],
                                }
                            ],
                            "turnComplete": True,
                        }
                    }
                )

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="gemini",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(
                "Circuit breaker OPEN for Gemini",
                event_type="circuit_breaker.open",
                provider="gemini",
                error_type="CircuitBreakerOpen",
                error_message=str(e)
            )
            track_ai_provider_error(
                provider="gemini",
                error_type="CircuitBreakerOpen"
            )
            raise
        except Exception as e:
            track_ai_provider_error(
                provider="gemini",
                error_type=type(e).__name__
            )
            raise

    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from Gemini.

        Yields:
            ProviderEvent: Audio, text, function call, or other events

        Raises:
            RuntimeError: If not connected
        """
        if self._state not in (SessionState.CONNECTED, SessionState.ACTIVE):
            raise RuntimeError(f"Cannot receive events in state {self._state}")

        self._state = SessionState.ACTIVE

        while self._state == SessionState.ACTIVE:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self._event_queue.get(), timeout=0.1
                )
                yield event

            except TimeoutError:
                # No events available, continue
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
            call_id: Function call ID from Gemini
            result: Function execution result
        """
        if self._state != SessionState.ACTIVE:
            raise RuntimeError(f"Cannot send function result in state {self._state}")

        # Send function response
        await self._send_message(
            {
                "toolResponse": {
                    "functionResponses": [
                        {
                            "id": call_id,
                            "response": result,
                        }
                    ]
                }
            }
        )

    async def _send_message(self, message: dict[str, Any]) -> None:
        """Send message to Gemini WebSocket.

        Args:
            message: Message dictionary to send

        Raises:
            RuntimeError: If WebSocket is not connected
        """
        if not self._ws:
            raise RuntimeError("WebSocket not connected")

        try:
            await self._ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to Gemini: {e}")
            raise


def create_gemini_provider(api_key: str) -> GeminiLiveProvider:
    """Factory function to create Gemini provider.

    Args:
        api_key: Google AI API key

    Returns:
        GeminiLiveProvider: Configured provider instance
    """
    return GeminiLiveProvider(api_key=api_key)
