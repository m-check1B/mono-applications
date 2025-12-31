"""OpenAI Realtime API provider implementation.

This module implements the RealtimeEndToEndProvider protocol for OpenAI's
Realtime API, supporting both gpt-4o-mini-realtime and gpt-4o-realtime models.
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


class OpenAIRealtimeProvider(BaseProvider):
    """OpenAI Realtime API provider.

    Supports real-time audio-to-audio conversation with function calling.
    Uses WebSocket connection for bidirectional streaming.
    """

    WEBSOCKET_URL = "wss://api.openai.com/v1/realtime"
    DEFAULT_MODEL = "gpt-4o-mini-realtime-preview-2024-12-17"
    PREMIUM_MODEL = "gpt-4o-realtime-preview-2024-12-17"

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize OpenAI Realtime provider.

        Args:
            api_key: OpenAI API key
            model: Model ID (defaults to mini model)
        """
        super().__init__(api_key)
        self._model = model or self.DEFAULT_MODEL
        self._ws: Any | None = None  # WebSocket connection
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()
        self._receive_task: asyncio.Task | None = None
        self._session_id: str | None = None

        # Auto-reconnection state
        self._reconnect_attempts = 0
        self._is_reconnecting = False
        self._should_reconnect = True
        self._connection_healthy = False
        self._last_message_time: float = 0
        self._rate_limit_reset_time: float = 0

        # Circuit breaker for cascade failure protection
        self._circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                name="openai_provider",
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60
            ),
            provider_id="openai"
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        """OpenAI Realtime capabilities."""
        is_premium = "mini" not in self._model
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=True,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],
            max_session_duration=1800,  # 30 minutes
            cost_tier="premium" if is_premium else "standard",
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

            # Import websockets dynamically (will need to add to dependencies)
            try:
                import websockets
            except ImportError:
                raise ImportError(
                    "websockets library required. Install with: pip install websockets"
                )

            # Build WebSocket URL with model parameter
            url = f"{self.WEBSOCKET_URL}?model={config.model_id or self._model}"

            # Connect with OpenAI API key in headers
            self._ws = await websockets.connect(
                url,
                additional_headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "OpenAI-Beta": "realtime=v1",
                },
            )

            # Start receiving events
            self._receive_task = asyncio.create_task(self._receive_loop())

            # Wait for session.created event
            await self._wait_for_session_created()

            # Configure session
            await self._configure_session(config)

            self._state = SessionState.CONNECTED
            logger.info(f"Connected to OpenAI Realtime API with model {self._model}")

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(f"Failed to connect to OpenAI: {e}")
            raise ConnectionError(f"OpenAI connection failed: {e}") from e

    async def _wait_for_session_created(self, timeout: float = 10.0) -> None:
        """Wait for session.created event.

        Args:
            timeout: Maximum wait time in seconds

        Raises:
            TimeoutError: If session not created within timeout
        """
        try:
            async with asyncio.timeout(timeout):
                while True:
                    event = await self._event_queue.get()
                    if event.type == "session.created":
                        self._session_id = event.data.get("id")
                        logger.info(f"OpenAI session created: {self._session_id}")
                        return
                    # Re-queue other events
                    await self._event_queue.put(event)
                    await asyncio.sleep(0.01)
        except TimeoutError:
            raise TimeoutError("Timeout waiting for OpenAI session creation")

    async def _configure_session(self, config: SessionConfig) -> None:
        """Configure the OpenAI session with system prompt and tools.

        Args:
            config: Session configuration
        """
        session_config: dict[str, Any] = {
            "modalities": ["text", "audio"],
            "instructions": config.system_prompt or "",
            "voice": "alloy",  # Default voice
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200,
            },
            "temperature": config.temperature,
        }

        if config.max_tokens:
            session_config["max_response_output_tokens"] = config.max_tokens

        if config.tools:
            session_config["tools"] = config.tools
            session_config["tool_choice"] = "auto"

        await self._send_event(
            {
                "type": "session.update",
                "session": session_config,
            }
        )

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

                    # Check for rate limit errors
                    if data.get("type") == "error":
                        error_data = data.get("error", {})
                        error_code = error_data.get("code")

                        # Handle rate limit errors specially
                        if error_code == "rate_limit_exceeded":
                            logger.warning("OpenAI rate limit exceeded")
                            self._rate_limit_reset_time = time.time() + 60  # Wait 60s for rate limits

                    event = self._parse_event(data)
                    await self._event_queue.put(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse OpenAI message: {e}")
                except Exception as e:
                    logger.error(f"Error processing OpenAI event: {e}")
        except Exception as e:
            logger.error(f"WebSocket receive loop error: {e}")
            self._connection_healthy = False

            # Attempt auto-reconnection if enabled and in active state
            if self._should_reconnect and self._state in (SessionState.CONNECTED, SessionState.ACTIVE):
                await self._attempt_reconnection()
            else:
                self._state = SessionState.ERROR

    def _parse_event(self, data: dict[str, Any]) -> ProviderEvent:
        """Parse OpenAI event into unified ProviderEvent.

        Args:
            data: Raw event data from OpenAI

        Returns:
            ProviderEvent: Unified event
        """
        event_type = data.get("type", "unknown")

        # Map OpenAI events to unified events
        if event_type == "response.audio.delta":
            # Audio chunk received
            audio_b64 = data.get("delta", "")
            audio_bytes = base64.b64decode(audio_b64)
            return ProviderEvent(
                type="audio.output",
                data={
                    "audio": audio_bytes,
                    "format": "pcm16",
                    "sample_rate": 24000,
                },
            )

        elif event_type == "response.text.delta":
            # Text chunk received
            return ProviderEvent(
                type="text.output",
                data={
                    "text": data.get("delta", ""),
                    "role": "assistant",
                },
            )

        elif event_type == "response.function_call_arguments.delta":
            # Function call in progress
            return ProviderEvent(
                type="function_call.delta",
                data={
                    "call_id": data.get("call_id"),
                    "name": data.get("name"),
                    "arguments_delta": data.get("delta", ""),
                },
            )

        elif event_type == "response.function_call_arguments.done":
            # Function call complete
            return ProviderEvent(
                type="function_call",
                data={
                    "call_id": data.get("call_id"),
                    "name": data.get("name"),
                    "arguments": json.loads(data.get("arguments", "{}")),
                },
            )

        elif event_type == "input_audio_buffer.speech_started":
            return ProviderEvent(type="speech.started", data={})

        elif event_type == "input_audio_buffer.speech_stopped":
            return ProviderEvent(type="speech.stopped", data={})

        elif event_type == "conversation.item.input_audio_transcription.completed":
            return ProviderEvent(
                type="transcription",
                data={"text": data.get("transcript", "")},
            )

        elif event_type == "error":
            logger.error(f"OpenAI error event: {data}")
            return ProviderEvent(
                type="error",
                data={
                    "error": data.get("error", {}),
                    "message": data.get("error", {}).get("message", "Unknown error"),
                },
            )

        # Pass through other events
        return ProviderEvent(type=event_type, data=data)

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API."""
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
            logger.info("Disconnected from OpenAI Realtime API")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._state = SessionState.ERROR

    async def _attempt_reconnection(self) -> None:
        """Attempt to reconnect with exponential backoff.

        This method is called automatically when a connection is lost.
        It will try to reconnect up to MAX_RECONNECT_ATTEMPTS times with
        exponentially increasing delays. It also handles OpenAI rate limits.
        """
        if self._is_reconnecting:
            logger.warning("Reconnection already in progress")
            return

        self._is_reconnecting = True
        original_state = self._state

        try:
            while self._reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
                self._reconnect_attempts += 1

                # Check if we need to wait for rate limit reset
                import time
                current_time = time.time()
                if self._rate_limit_reset_time > current_time:
                    rate_limit_wait = self._rate_limit_reset_time - current_time
                    logger.info(f"Waiting {rate_limit_wait:.1f}s for rate limit reset...")
                    await asyncio.sleep(rate_limit_wait)

                backoff_delay = INITIAL_BACKOFF_DELAY * (2 ** (self._reconnect_attempts - 1))

                logger.info(
                    f"Reconnection attempt {self._reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS} "
                    f"in {backoff_delay}s..."
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
                        f"Reconnection successful after {self._reconnect_attempts} attempts"
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
                    self._rate_limit_reset_time = 0
                    return

                except Exception as e:
                    logger.warning(
                        f"Reconnection attempt {self._reconnect_attempts} failed: {e}"
                    )

                    if self._reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
                        logger.error(
                            f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached"
                        )
                        break

            # All reconnection attempts failed
            logger.error("Failed to reconnect after maximum attempts")
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
        conversation context and session configuration.

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

        # Reconnect to OpenAI
        url = f"{self.WEBSOCKET_URL}?model={self._config.model_id or self._model}"
        self._ws = await websockets.connect(
            url,
            additional_headers={
                "Authorization": f"Bearer {self._api_key}",
                "OpenAI-Beta": "realtime=v1",
            },
        )

        # Restart receive loop
        self._receive_task = asyncio.create_task(self._receive_loop())

        # Wait for new session creation
        await self._wait_for_session_created()

        # Reconfigure session with preserved configuration
        await self._configure_session(self._config)

        # Restore state
        self._state = SessionState.CONNECTED if self._state != SessionState.ACTIVE else SessionState.ACTIVE
        logger.info("OpenAI WebSocket reconnected and session restored")

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio input to OpenAI.

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

                await self._send_event(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": audio_b64,
                    }
                )

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="openai",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(f"Circuit breaker OPEN for OpenAI: {e}")
            track_ai_provider_error(
                provider="openai",
                error_type="CircuitBreakerOpen"
            )
            raise
        except Exception as e:
            track_ai_provider_error(
                provider="openai",
                error_type=type(e).__name__
            )
            raise

    async def send_text(self, message: TextMessage) -> None:
        """Send text input to OpenAI.

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
                await self._send_event(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": message.role,
                            "content": [{"type": "input_text", "text": message.content}],
                        },
                    }
                )

                # Trigger response generation
                await self._send_event({"type": "response.create"})

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="openai",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(f"Circuit breaker OPEN for OpenAI: {e}")
            track_ai_provider_error(
                provider="openai",
                error_type="CircuitBreakerOpen"
            )
            raise
        except Exception as e:
            track_ai_provider_error(
                provider="openai",
                error_type=type(e).__name__
            )
            raise

    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from OpenAI.

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

                # Check for error events
                if event.type == "error":
                    logger.error(f"OpenAI error: {event.data}")
                    self._state = SessionState.ERROR
                    break

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
        """Send function execution result back to OpenAI.

        Args:
            call_id: Function call ID from OpenAI
            result: Function execution result
        """
        if self._state != SessionState.ACTIVE:
            raise RuntimeError(f"Cannot send function result in state {self._state}")

        await self._send_event(
            {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result),
                },
            }
        )

        # Trigger response generation
        await self._send_event({"type": "response.create"})

    async def _send_event(self, event: dict[str, Any]) -> None:
        """Send event to OpenAI WebSocket.

        Args:
            event: Event dictionary to send

        Raises:
            RuntimeError: If WebSocket is not connected
        """
        if not self._ws:
            raise RuntimeError("WebSocket not connected")

        try:
            await self._ws.send(json.dumps(event))
        except Exception as e:
            logger.error(f"Failed to send event to OpenAI: {e}")
            raise


def create_openai_provider(
    api_key: str, use_premium: bool = False
) -> OpenAIRealtimeProvider:
    """Factory function to create OpenAI provider.

    Args:
        api_key: OpenAI API key
        use_premium: If True, use gpt-4o-realtime instead of mini

    Returns:
        OpenAIRealtimeProvider: Configured provider instance
    """
    model = (
        OpenAIRealtimeProvider.PREMIUM_MODEL
        if use_premium
        else OpenAIRealtimeProvider.DEFAULT_MODEL
    )
    return OpenAIRealtimeProvider(api_key=api_key, model=model)
