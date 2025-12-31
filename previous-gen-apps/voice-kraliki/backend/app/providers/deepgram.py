"""Deepgram segmented voice pipeline provider implementation.

This module implements the SegmentedVoiceProvider protocol using:
- Deepgram Live API for STT (Speech-to-Text)
- Google Gemini for text processing
- Deepgram TTS for speech synthesis

This is a traditional pipeline approach where components are separate.
"""

import asyncio
import json
import time
from collections import deque
from collections.abc import AsyncGenerator
from typing import Any

import httpx

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
AUDIO_BUFFER_SIZE = 100  # Max audio chunks to buffer during reconnection


class DeepgramSegmentedProvider(BaseProvider):
    """Deepgram + Gemini segmented voice pipeline.

    This provider coordinates three separate components:
    1. Deepgram Live (STT) - transcribes audio to text
    2. Gemini Flash (LLM) - processes text and generates responses
    3. Deepgram TTS - synthesizes speech from text
    """

    DEEPGRAM_STT_URL = "wss://api.deepgram.com/v1/listen"
    DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        deepgram_api_key: str,
        gemini_api_key: str,
        stt_model: str = "nova-2",
        tts_voice: str = "aura-asteria-en",
        llm_model: str = "gemini-2.5-flash",
    ):
        """Initialize Deepgram segmented provider.

        Args:
            deepgram_api_key: Deepgram API key
            gemini_api_key: Google AI API key
            stt_model: Deepgram STT model (nova-2, whisper, etc.)
            tts_voice: Deepgram TTS voice
            llm_model: Gemini model for text processing
        """
        super().__init__(deepgram_api_key)
        self._gemini_api_key = gemini_api_key
        self._stt_model = stt_model
        self._tts_voice = tts_voice
        self._llm_model = llm_model

        # Component connections
        self._stt_ws: Any | None = None  # Deepgram STT WebSocket
        self._stt_task: asyncio.Task | None = None

        # Event queues
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()
        self._transcript_queue: asyncio.Queue[str] = asyncio.Queue()

        # HTTP client for Gemini and TTS
        self._http_client: httpx.AsyncClient | None = None

        # Conversation history for Gemini
        self._conversation_history: list[dict[str, str]] = []

        # Auto-reconnection state
        self._reconnect_attempts = 0
        self._is_reconnecting = False
        self._should_reconnect = True
        self._stt_connection_healthy = False
        self._last_stt_message_time: float = 0

        # Audio buffering for brief disconnections
        self._audio_buffer: deque[AudioChunk] = deque(maxlen=AUDIO_BUFFER_SIZE)

        # Circuit breaker for cascade failure protection
        self._circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                name="deepgram_provider",
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60
            ),
            provider_id="deepgram"
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Deepgram segmented pipeline capabilities."""
        return ProviderCapabilities(
            supports_realtime=False,  # Segmented, not true realtime
            supports_text=True,
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=False,  # Can be added via Gemini
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16, AudioFormat.ULAW],
            max_session_duration=None,  # No hard limit
            cost_tier="standard",
        )

    async def connect(self, config: SessionConfig) -> None:
        """Connect to all pipeline components.

        Args:
            config: Session configuration

        Raises:
            ConnectionError: If any component fails to connect
        """
        if self._state != SessionState.IDLE:
            raise RuntimeError(f"Cannot connect from state {self._state}")

        try:
            self._state = SessionState.CONNECTING
            self._config = config
            self._validate_audio_format(config.audio_format)

            # Initialize HTTP client
            self._http_client = httpx.AsyncClient(timeout=30.0)

            # Connect to Deepgram STT
            await self._connect_stt(config)

            # Initialize conversation with system prompt
            if config.system_prompt:
                self._conversation_history.append(
                    {"role": "system", "content": config.system_prompt}
                )

            self._state = SessionState.CONNECTED
            logger.info("Connected to Deepgram segmented pipeline")

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(f"Failed to connect pipeline: {e}")
            raise ConnectionError(f"Pipeline connection failed: {e}") from e

    async def _connect_stt(self, config: SessionConfig) -> None:
        """Connect to Deepgram STT WebSocket.

        Args:
            config: Session configuration
        """
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets library required. Install with: pip install websockets"
            )

        # Build Deepgram STT URL
        params = {
            "model": self._stt_model,
            "punctuate": "true",
            "interim_results": "false",
            "utterance_end_ms": "1000",
            "vad_events": "true",
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.DEEPGRAM_STT_URL}?{query_string}"

        # Connect with Deepgram API key
        self._stt_ws = await websockets.connect(
            url,
            additional_headers={"Authorization": f"Token {self._api_key}"},
        )

        # Start receiving STT events
        self._stt_task = asyncio.create_task(self._receive_stt_loop())
        logger.info(f"Connected to Deepgram STT with model {self._stt_model}")

    async def _receive_stt_loop(self) -> None:
        """Background task to receive STT transcriptions."""
        if not self._stt_ws:
            return

        try:
            async for message in self._stt_ws:
                try:
                    # Update connection health tracking
                    import time
                    self._last_stt_message_time = time.time()
                    self._stt_connection_healthy = True

                    data = json.loads(message)
                    await self._handle_stt_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Deepgram STT message: {e}")
                except Exception as e:
                    logger.error(f"Error processing STT event: {e}")
        except Exception as e:
            logger.error(f"STT receive loop error: {e}")
            self._stt_connection_healthy = False

            # Attempt auto-reconnection if enabled and in active state
            if self._should_reconnect and self._state in (SessionState.CONNECTED, SessionState.ACTIVE):
                await self._attempt_stt_reconnection()
            else:
                self._state = SessionState.ERROR

    async def _handle_stt_message(self, data: dict[str, Any]) -> None:
        """Handle incoming STT message from Deepgram.

        Args:
            data: STT message data
        """
        # Handle speech started event
        if data.get("type") == "SpeechStarted":
            await self._event_queue.put(
                ProviderEvent(type="speech.started", data={})
            )
            return

        # Handle transcription results
        if data.get("type") == "Results":
            channel = data.get("channel", {})
            alternatives = channel.get("alternatives", [])
            if alternatives:
                transcript = alternatives[0].get("transcript", "").strip()
                if transcript:
                    # Emit transcription event
                    await self._event_queue.put(
                        ProviderEvent(
                            type="transcription",
                            data={"text": transcript},
                        )
                    )
                    # Queue for LLM processing
                    await self._transcript_queue.put(transcript)
                    # Process with LLM
                    asyncio.create_task(self._process_with_llm(transcript))

        # Handle utterance end
        if data.get("type") == "UtteranceEnd":
            await self._event_queue.put(
                ProviderEvent(type="speech.stopped", data={})
            )

    async def _process_with_llm(self, user_input: str) -> None:
        """Process user input with Gemini LLM.

        Args:
            user_input: Transcribed user speech
        """
        try:
            # Add user message to history
            self._conversation_history.append(
                {"role": "user", "content": user_input}
            )

            # Call Gemini API
            response_text = await self._call_gemini(user_input)

            # Add assistant response to history
            self._conversation_history.append(
                {"role": "assistant", "content": response_text}
            )

            # Emit text response event
            await self._event_queue.put(
                ProviderEvent(
                    type="text.output",
                    data={"text": response_text, "role": "assistant"},
                )
            )

            # Generate TTS audio
            await self._generate_tts(response_text)

        except Exception as e:
            logger.error(f"Error processing with LLM: {e}")
            await self._event_queue.put(
                ProviderEvent(
                    type="error",
                    data={"message": f"LLM processing error: {e}"},
                )
            )

    async def _call_gemini(self, user_input: str) -> str:
        """Call Gemini API for text processing.

        Args:
            user_input: User message

        Returns:
            str: Gemini response text
        """
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        url = f"{self.GEMINI_API_URL}/{self._llm_model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": self._gemini_api_key}

        # Build request with conversation history
        contents = []
        for msg in self._conversation_history[-10:]:  # Keep last 10 messages
            if msg["role"] != "system":
                contents.append(
                    {
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [{"text": msg["content"]}],
                    }
                )

        body = {"contents": contents}

        # Add system instruction if available
        if self._config and self._config.system_prompt:
            body["systemInstruction"] = {
                "parts": [{"text": self._config.system_prompt}]
            }

        response = await self._http_client.post(
            url, headers=headers, params=params, json=body
        )
        response.raise_for_status()

        data = response.json()
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")

        return "I'm sorry, I couldn't generate a response."

    async def _generate_tts(self, text: str) -> None:
        """Generate speech audio from text using Deepgram TTS.

        Args:
            text: Text to synthesize
        """
        try:
            if not self._http_client:
                raise RuntimeError("HTTP client not initialized")

            url = f"{self.DEEPGRAM_TTS_URL}?model={self._tts_voice}"
            headers = {
                "Authorization": f"Token {self._api_key}",
                "Content-Type": "application/json",
            }
            body = {"text": text}

            response = await self._http_client.post(
                url, headers=headers, json=body
            )
            response.raise_for_status()

            # Get audio bytes
            audio_bytes = response.content

            # Emit audio output event
            await self._event_queue.put(
                ProviderEvent(
                    type="audio.output",
                    data={
                        "audio": audio_bytes,
                        "format": "pcm16",  # Deepgram TTS returns PCM16
                        "sample_rate": 24000,
                    },
                )
            )

        except Exception as e:
            logger.error(f"Error generating TTS: {e}")
            await self._event_queue.put(
                ProviderEvent(
                    type="error",
                    data={"message": f"TTS generation error: {e}"},
                )
            )

    async def disconnect(self) -> None:
        """Disconnect from all pipeline components."""
        if self._state == SessionState.DISCONNECTED:
            return

        # Disable auto-reconnection when explicitly disconnecting
        self._should_reconnect = False
        self._state = SessionState.DISCONNECTING

        try:
            # Cancel STT task
            if self._stt_task:
                self._stt_task.cancel()
                try:
                    await self._stt_task
                except asyncio.CancelledError:
                    pass

            # Close STT WebSocket
            if self._stt_ws:
                await self._stt_ws.close()
                self._stt_ws = None

            # Close HTTP client
            if self._http_client:
                await self._http_client.aclose()
                self._http_client = None

            self._state = SessionState.DISCONNECTED
            self._stt_connection_healthy = False
            logger.info("Disconnected from Deepgram pipeline")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            self._state = SessionState.ERROR

    async def _attempt_stt_reconnection(self) -> None:
        """Attempt to reconnect STT WebSocket with exponential backoff.

        This method is called automatically when the STT connection is lost.
        It will try to reconnect up to MAX_RECONNECT_ATTEMPTS times with
        exponentially increasing delays. Buffered audio is replayed after reconnection.
        """
        if self._is_reconnecting:
            logger.warning("STT reconnection already in progress")
            return

        self._is_reconnecting = True

        try:
            while self._reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
                self._reconnect_attempts += 1
                backoff_delay = INITIAL_BACKOFF_DELAY * (2 ** (self._reconnect_attempts - 1))

                logger.info(
                    f"STT reconnection attempt {self._reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS} "
                    f"in {backoff_delay}s..."
                )

                # Emit reconnection attempt event
                await self._event_queue.put(
                    ProviderEvent(
                        type="connection.reconnecting",
                        data={
                            "component": "stt",
                            "attempt": self._reconnect_attempts,
                            "max_attempts": MAX_RECONNECT_ATTEMPTS,
                            "backoff_delay": backoff_delay,
                            "buffered_audio_chunks": len(self._audio_buffer),
                        },
                    )
                )

                # Wait for backoff delay
                await asyncio.sleep(backoff_delay)

                # Attempt reconnection
                try:
                    await self._reconnect_stt()

                    # Success!
                    logger.info(
                        f"STT reconnection successful after {self._reconnect_attempts} attempts"
                    )

                    # Emit reconnection success event
                    await self._event_queue.put(
                        ProviderEvent(
                            type="connection.reconnected",
                            data={
                                "component": "stt",
                                "attempts": self._reconnect_attempts,
                            },
                        )
                    )

                    # Replay buffered audio
                    if self._audio_buffer:
                        logger.info(f"Replaying {len(self._audio_buffer)} buffered audio chunks")
                        await self._replay_buffered_audio()

                    # Reset reconnection state
                    self._reconnect_attempts = 0
                    self._is_reconnecting = False
                    self._stt_connection_healthy = True
                    return

                except Exception as e:
                    logger.warning(
                        f"STT reconnection attempt {self._reconnect_attempts} failed: {e}"
                    )

                    if self._reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
                        logger.error(
                            f"Max STT reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached"
                        )
                        break

            # All reconnection attempts failed
            logger.error("Failed to reconnect STT after maximum attempts")
            await self._event_queue.put(
                ProviderEvent(
                    type="connection.failed",
                    data={
                        "component": "stt",
                        "attempts": self._reconnect_attempts,
                        "reason": "Max reconnection attempts exceeded",
                    },
                )
            )
            self._state = SessionState.ERROR

        finally:
            self._is_reconnecting = False

    async def _reconnect_stt(self) -> None:
        """Perform actual STT reconnection.

        This method handles the low-level STT reconnection logic while preserving
        configuration.

        Raises:
            Exception: If reconnection fails
        """
        if not self._config:
            raise RuntimeError("Cannot reconnect: no configuration saved")

        # Clean up existing STT connection
        if self._stt_task:
            self._stt_task.cancel()
            try:
                await self._stt_task
            except asyncio.CancelledError:
                pass

        if self._stt_ws:
            try:
                await self._stt_ws.close()
            except Exception:
                pass
            self._stt_ws = None

        # Reconnect STT WebSocket
        await self._connect_stt(self._config)

        logger.info("Deepgram STT WebSocket reconnected")

    async def _replay_buffered_audio(self) -> None:
        """Replay buffered audio chunks after reconnection."""
        if not self._stt_ws:
            logger.warning("Cannot replay audio: STT WebSocket not connected")
            return

        buffered_count = len(self._audio_buffer)
        replayed_count = 0

        try:
            while self._audio_buffer:
                audio_chunk = self._audio_buffer.popleft()
                await self._stt_ws.send(audio_chunk.data)
                replayed_count += 1

            logger.info(f"Successfully replayed {replayed_count}/{buffered_count} buffered audio chunks")

        except Exception as e:
            logger.error(f"Error replaying buffered audio: {e} (replayed {replayed_count}/{buffered_count})")
            raise

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio to STT component.

        Args:
            audio: Audio chunk to transcribe

        Raises:
            RuntimeError: If not connected
            CircuitBreakerOpenError: If circuit breaker is open
        """
        if self._state != SessionState.CONNECTED:
            raise RuntimeError(f"Cannot send audio in state {self._state}")

        self._validate_audio_format(audio.format)

        # If reconnecting, buffer audio for later replay
        if self._is_reconnecting:
            logger.debug("Buffering audio during STT reconnection")
            self._audio_buffer.append(audio)
            return

        if not self._stt_ws:
            logger.warning("STT WebSocket not connected, buffering audio")
            self._audio_buffer.append(audio)
            return

        start_time = time.time()
        try:
            async with self._circuit_breaker:
                # Send raw audio bytes to Deepgram STT
                await self._stt_ws.send(audio.data)

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="deepgram",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(f"Circuit breaker OPEN for Deepgram: {e}")
            track_ai_provider_error(
                provider="deepgram",
                error_type="CircuitBreakerOpen"
            )
            # Buffer this chunk for retry
            self._audio_buffer.append(audio)
            raise
        except Exception as e:
            logger.error(f"Failed to send audio to STT: {e}")
            track_ai_provider_error(
                provider="deepgram",
                error_type=type(e).__name__
            )
            # Buffer this chunk for retry
            self._audio_buffer.append(audio)
            raise

    async def send_text(self, message: TextMessage) -> None:
        """Send text directly to LLM (bypass STT).

        Args:
            message: Text message to process

        Raises:
            RuntimeError: If not connected
            CircuitBreakerOpenError: If circuit breaker is open
        """
        if self._state != SessionState.CONNECTED:
            raise RuntimeError(f"Cannot send text in state {self._state}")

        start_time = time.time()
        try:
            async with self._circuit_breaker:
                # Process directly with LLM
                asyncio.create_task(self._process_with_llm(message.content))

            # Track successful request
            latency = time.time() - start_time
            track_ai_provider_request(
                provider="deepgram",
                status="success",
                latency=latency
            )

        except CircuitBreakerOpenError as e:
            logger.error(f"Circuit breaker OPEN for Deepgram: {e}")
            track_ai_provider_error(
                provider="deepgram",
                error_type="CircuitBreakerOpen"
            )
            raise
        except Exception as e:
            track_ai_provider_error(
                provider="deepgram",
                error_type=type(e).__name__
            )
            raise

    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from the pipeline.

        Yields:
            ProviderEvent: Transcription, text, audio, or error events

        Raises:
            RuntimeError: If not connected
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

                # Check for error events
                if event.type == "error":
                    logger.error(f"Pipeline error: {event.data}")

            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error receiving event: {e}")
                self._state = SessionState.ERROR
                break


def create_deepgram_provider(
    deepgram_api_key: str,
    gemini_api_key: str,
    stt_model: str = "nova-2",
    tts_voice: str = "aura-asteria-en",
) -> DeepgramSegmentedProvider:
    """Factory function to create Deepgram segmented provider.

    Args:
        deepgram_api_key: Deepgram API key
        gemini_api_key: Google AI API key
        stt_model: STT model (nova-2, whisper, etc.)
        tts_voice: TTS voice

    Returns:
        DeepgramSegmentedProvider: Configured provider instance
    """
    return DeepgramSegmentedProvider(
        deepgram_api_key=deepgram_api_key,
        gemini_api_key=gemini_api_key,
        stt_model=stt_model,
        tts_voice=tts_voice,
    )
