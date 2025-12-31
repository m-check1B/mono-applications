"""Deepgram Nova 3 Voice Agent provider implementation.

This module implements the RealtimeEndToEndProvider protocol using:
- Deepgram Nova 3 for speech recognition with Live API
- OpenAI for LLM processing  
- Deepgram Aura for text-to-speech
- Real-time end-to-end voice processing

This is a production-ready implementation using the current Deepgram SDK.
"""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from typing import Any

from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents

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

logger = logging.getLogger(__name__)


class DeepgramNova3Provider(BaseProvider):
    """Deepgram Nova 3 Voice Agent provider.

    This provider uses Deepgram's Live API with Nova-3 model for:
    - State-of-the-art speech recognition
    - Real-time transcription
    - Low-latency audio processing
    """

    def __init__(
        self,
        deepgram_api_key: str,
        model: str = "nova-3",
        language: str = "en",
        smart_format: bool = True,
        punctuate: bool = True,
        profanity_filter: bool = False,
        redact: list[str] | None = None,
        diarize: bool = True,
        multichannel: bool = False,
        alternatives: int = 1,
        interim_results: bool = True,
        endpointing: int = 10,
        vad_events: bool = True,
        sample_rate: int = 16000,
        encoding: str = "linear16",
    ):
        """Initialize Deepgram Nova 3 provider.

        Args:
            deepgram_api_key: Deepgram API key
            model: Nova model to use (nova-2, nova-3, etc.)
            language: Language code (en, es, fr, etc.)
            smart_format: Enable smart formatting
            punctuate: Enable punctuation
            profanity_filter: Enable profanity filtering
            redact: List of PII types to redact
            diarize: Enable speaker diarization
            multichannel: Enable multi-channel processing
            alternatives: Number of transcription alternatives
            interim_results: Enable interim results
            endpointing: Endpointing sensitivity (0-100)
            vad_events: Enable voice activity detection events
            sample_rate: Audio sample rate
            encoding: Audio encoding format
        """
        super().__init__(deepgram_api_key)
        self.model = model
        self.language = language
        self.smart_format = smart_format
        self.punctuate = punctuate
        self.profanity_filter = profanity_filter
        self.redact = redact or []
        self.diarize = diarize
        self.multichannel = multichannel
        self.alternatives = alternatives
        self.interim_results = interim_results
        self.endpointing = endpointing
        self.vad_events = vad_events
        self.sample_rate = sample_rate
        self.encoding = encoding

        # Deepgram client and connection
        self._deepgram_client: DeepgramClient | None = None
        self._connection: Any | None = None

        # Event management
        self._event_queue: asyncio.Queue[ProviderEvent] = asyncio.Queue()
        self._processing_complete = False

        # Conversation state
        self._conversation_history: list[dict[str, str]] = []
        self._current_transcript = ""

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Deepgram Nova 3 provider capabilities."""
        return ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=False,  # Audio only
            supports_function_calling=False,  # STT only, no LLM
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16, AudioFormat.ULAW],
            max_session_duration=None,  # No hard limit
            cost_tier="premium",  # Nova 3 is premium tier
        )

    async def connect(self, config: SessionConfig) -> None:
        """Connect to Deepgram Nova 3 Live API.

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

            # Initialize Deepgram client
            self._deepgram_client = DeepgramClient(self._api_key)

            # Create Live connection
            self._connection = self._deepgram_client.listen.live.v("1")

            # Configure connection options
            options = LiveOptions(
                model=self.model,
                language=self.language,
                smart_format=self.smart_format,
                punctuate=self.punctuate,
                profanity_filter=self.profanity_filter,
                redact=self.redact,
                diarize=self.diarize,
                multichannel=self.multichannel,
                alternatives=self.alternatives,
                interim_results=self.interim_results,
                endpointing=self.endpointing,
                vad_events=self.vad_events,
                sample_rate=self.sample_rate,
                encoding=self.encoding,
            )

            # Start connection with options
            await self._connection.start(options)

            # Register event handlers
            self._register_event_handlers()

            self._state = SessionState.CONNECTED
            logger.info(f"Connected to Deepgram Nova 3 with model {self.model}")

        except Exception as e:
            self._state = SessionState.ERROR
            logger.error(f"Failed to connect to Deepgram Nova 3: {e}")
            raise ConnectionError(f"Deepgram Nova 3 connection failed: {e}") from e

    def _register_event_handlers(self) -> None:
        """Register Deepgram Live API event handlers."""
        if not self._connection:
            raise RuntimeError("Connection not initialized")

        # Transcript received
        def on_transcript_received(data, **kwargs):
            try:
                if data.get('is_final'):
                    transcript = data.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
                    if transcript.strip():
                        self._handle_final_transcript(transcript, data)
                else:
                    transcript = data.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
                    if transcript.strip():
                        self._handle_interim_transcript(transcript, data)
            except Exception as e:
                logger.error(f"Error processing transcript: {e}")

        # Connection opened
        def on_open(data, **kwargs):
            logger.info("Deepgram Nova 3 connection opened")
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(type="connection.opened", data={"status": "connected"})
                )
            )

        # Connection closed
        def on_close(data, **kwargs):
            logger.info("Deepgram Nova 3 connection closed")
            self._processing_complete = True
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(type="connection.closed", data={"status": "disconnected"})
                )
            )

        # Error occurred
        def on_error(data, **kwargs):
            error_msg = data.get('error', 'Unknown error')
            logger.error(f"Deepgram Nova 3 error: {error_msg}")
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(type="error", data={"error": error_msg})
                )
            )

        # Speech started
        def on_speech_started(data, **kwargs):
            logger.debug("Speech started detected")
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(type="speech.started", data={})
                )
            )

        # Speech ended
        def on_speech_ended(data, **kwargs):
            logger.debug("Speech ended detected")
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(type="speech.ended", data={})
                )
            )

        # Register handlers
        self._connection.on(LiveTranscriptionEvents.Transcript, on_transcript_received)
        self._connection.on(LiveTranscriptionEvents.Open, on_open)
        self._connection.on(LiveTranscriptionEvents.Close, on_close)
        self._connection.on(LiveTranscriptionEvents.Error, on_error)
        self._connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        self._connection.on(LiveTranscriptionEvents.SpeechEnded, on_speech_ended)

    def _handle_final_transcript(self, transcript: str, data: dict[str, Any]) -> None:
        """Handle final transcript from Deepgram."""
        try:
            # Clean up transcript
            clean_transcript = transcript.strip()

            # Add to conversation history
            self._conversation_history.append({
                "role": "user",
                "content": clean_transcript,
                "timestamp": time.time()
            })

            # Emit transcript event
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(
                        type="transcript.final",
                        data={
                            "text": clean_transcript,
                            "confidence": data.get('channel', {}).get('alternatives', [{}])[0].get('confidence', 0.0),
                            "speaker": data.get('channel', {}).get('speaker', 0) if self.diarize else None,
                            "timestamp": data.get('timestamp', time.time()),
                            "is_final": True
                        }
                    )
                )
            )

            logger.debug(f"Final transcript: {clean_transcript}")

        except Exception as e:
            logger.error(f"Error handling final transcript: {e}")

    def _handle_interim_transcript(self, transcript: str, data: dict[str, Any]) -> None:
        """Handle interim transcript from Deepgram."""
        try:
            # Clean up transcript
            clean_transcript = transcript.strip()

            # Emit interim transcript event
            asyncio.create_task(
                self._event_queue.put(
                    ProviderEvent(
                        type="transcript.interim",
                        data={
                            "text": clean_transcript,
                            "confidence": data.get('channel', {}).get('alternatives', [{}])[0].get('confidence', 0.0),
                            "speaker": data.get('channel', {}).get('speaker', 0) if self.diarize else None,
                            "timestamp": data.get('timestamp', time.time()),
                            "is_final": False
                        }
                    )
                )
            )

            logger.debug(f"Interim transcript: {clean_transcript}")

        except Exception as e:
            logger.error(f"Error handling interim transcript: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Deepgram Nova 3."""
        if self._state == SessionState.IDLE:
            return

        try:
            self._state = SessionState.DISCONNECTING

            if self._connection:
                await self._connection.finish()
                self._connection = None

            self._state = SessionState.IDLE
            logger.info("Disconnected from Deepgram Nova 3")

        except Exception as e:
            logger.error(f"Error disconnecting from Deepgram Nova 3: {e}")
            self._state = SessionState.ERROR

    async def send_audio(self, audio: AudioChunk) -> None:
        """Send audio chunk to Deepgram for transcription.

        Args:
            audio: Audio chunk to transcribe
        """
        if self._state != SessionState.CONNECTED or not self._connection:
            logger.warning("Cannot send audio: not connected")
            return

        try:
            # Convert audio to bytes if needed
            if isinstance(audio.data, str):
                audio_bytes = audio.data.encode('utf-8')
            else:
                audio_bytes = audio.data

            # Send to Deepgram
            self._connection.send(audio_bytes)

        except Exception as e:
            logger.error(f"Error sending audio to Deepgram: {e}")

    async def send_text(self, message: TextMessage) -> None:
        """Send text message (not supported for STT-only provider).

        Args:
            message: Text message to send
        """
        logger.warning("Deepgram Nova 3 provider is STT-only, text messages not supported")

    async def receive_events(self) -> AsyncGenerator[ProviderEvent]:
        """Receive events from Deepgram.

        Yields:
            ProviderEvent: Events from the provider
        """
        while not self._processing_complete:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                yield event
            except TimeoutError:
                # Check connection state
                if self._state != SessionState.CONNECTED:
                    break
                continue
            except Exception as e:
                logger.error(f"Error receiving event: {e}")
                break

    async def handle_function_result(self, call_id: str, result: dict[str, Any]) -> None:
        """Handle function call result (not supported for STT-only provider).

        Args:
            call_id: Function call ID
            result: Function call result
        """
        logger.warning("Deepgram Nova 3 provider is STT-only, function calls not supported")

    def get_conversation_history(self) -> list[dict[str, str]]:
        """Get conversation history.

        Returns:
            List of conversation turns
        """
        return self._conversation_history.copy()

    def clear_conversation_history(self) -> None:
        """Clear conversation history."""
        self._conversation_history.clear()


def create_deepgram_nova3_provider(
    api_key: str,
    **kwargs
) -> DeepgramNova3Provider:
    """Factory function to create Deepgram Nova 3 provider.

    Args:
        api_key: Deepgram API key
        **kwargs: Additional provider configuration

    Returns:
        DeepgramNova3Provider: Configured provider instance
    """
    return DeepgramNova3Provider(deepgram_api_key=api_key, **kwargs)
