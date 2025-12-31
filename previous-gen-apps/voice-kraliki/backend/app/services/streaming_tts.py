"""Streaming TTS Service

Provides chunked text-to-speech synthesis for sub-second playback:
- Non-blocking audio chunking
- Sub-second playback start times
- Multiple provider support
- Real-time audio streaming
"""

import asyncio
import io
import logging
import os
import time
from collections.abc import AsyncIterator

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AudioChunk(BaseModel):
    """Individual audio chunk for streaming."""

    data: bytes
    format: str
    sample_rate: int
    chunk_index: int
    total_chunks: int
    is_final: bool = False
    duration_ms: float | None = None


class StreamingTTSConfig(BaseModel):
    """Configuration for streaming TTS."""

    chunk_size_bytes: int = 4096  # 4KB chunks
    target_chunk_duration_ms: float = 200.0  # 200ms chunks
    max_buffer_size_chunks: int = 10
    preload_chunks: int = 2
    enable_progressive_loading: bool = True


class StreamingTTSProvider:
    """Base class for streaming TTS providers."""

    def __init__(self, api_key: str, config: StreamingTTSConfig = StreamingTTSConfig()):
        """Initialize streaming TTS provider.
        
        Args:
            api_key: Provider API key
            config: Streaming configuration
        """
        self.api_key = api_key
        self.config = config
        self._http_client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._http_client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._http_client:
            await self._http_client.aclose()

    async def synthesize_stream(
        self,
        text: str,
        voice: str,
        **kwargs
    ) -> AsyncIterator[AudioChunk]:
        """Synthesize speech with streaming chunks.
        
        Args:
            text: Text to synthesize
            voice: Voice model to use
            **kwargs: Additional provider-specific parameters
            
        Yields:
            AudioChunk: Audio data chunks
        """
        raise NotImplementedError("Subclasses must implement synthesize_stream")


class DeepgramStreamingTTS(StreamingTTSProvider):
    """Deepgram Aura streaming TTS provider."""

    DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"

    async def synthesize_stream(
        self,
        text: str,
        voice: str = "aura-asteria-en",
        **kwargs
    ) -> AsyncIterator[AudioChunk]:
        """Synthesize speech using Deepgram Aura with streaming.
        
        Args:
            text: Text to synthesize
            voice: Aura voice model
            **kwargs: Additional parameters (model, encoding, etc.)
            
        Yields:
            AudioChunk: Streaming audio chunks
        """
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        start_time = time.time()

        try:
            # Prepare request
            url = f"{self.DEEPGRAM_TTS_URL}?model={voice}"
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            }
            body = {"text": text}

            # Make streaming request
            async with self._http_client.stream(
                "POST", url, headers=headers, json=body
            ) as response:
                response.raise_for_status()

                # Get content info
                content_length = response.headers.get("content-length")
                total_size = int(content_length) if content_length else None

                # Stream audio data in chunks
                chunk_index = 0
                buffer = io.BytesIO()

                async for chunk_data in response.aiter_bytes(chunk_size=self.config.chunk_size_bytes):
                    buffer.write(chunk_data)

                    # Check if we have enough data for a chunk
                    if buffer.tell() >= self.config.chunk_size_bytes:
                        chunk_bytes = buffer.getvalue()
                        buffer.seek(0)
                        buffer.truncate(0)

                        # Calculate estimated duration (rough approximation)
                        # Deepgram TTS typically returns 24kHz PCM16
                        # 24kHz * 2 bytes per sample * 0.2s = 9600 bytes per 200ms chunk
                        estimated_duration_ms = (len(chunk_bytes) / (24000 * 2)) * 1000

                        # Determine if this might be the final chunk
                        is_final = (
                            total_size and
                            (chunk_index + 1) * self.config.chunk_size_bytes >= total_size
                        )

                        yield AudioChunk(
                            data=chunk_bytes,
                            format="pcm16",
                            sample_rate=24000,
                            chunk_index=chunk_index,
                            total_chunks=-1,  # Unknown until stream ends
                            is_final=is_final,
                            duration_ms=estimated_duration_ms
                        )

                        chunk_index += 1

                # Handle remaining data
                remaining_data = buffer.getvalue()
                if remaining_data:
                    estimated_duration_ms = (len(remaining_data) / (24000 * 2)) * 1000

                    yield AudioChunk(
                        data=remaining_data,
                        format="pcm16",
                        sample_rate=24000,
                        chunk_index=chunk_index,
                        total_chunks=chunk_index + 1,
                        is_final=True,
                        duration_ms=estimated_duration_ms
                    )

                total_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Deepgram streaming TTS completed: {len(text)} chars -> "
                    f"{chunk_index + 1} chunks in {total_time:.1f}ms"
                )

        except Exception as e:
            logger.error(f"Deepgram streaming TTS error: {e}")
            raise


class OpenAIStreamingTTS(StreamingTTSProvider):
    """OpenAI streaming TTS provider."""

    OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"

    async def synthesize_stream(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        **kwargs
    ) -> AsyncIterator[AudioChunk]:
        """Synthesize speech using OpenAI TTS with streaming.
        
        Args:
            text: Text to synthesize
            voice: OpenAI voice model
            model: TTS model (tts-1 or tts-1-hd)
            **kwargs: Additional parameters
            
        Yields:
            AudioChunk: Streaming audio chunks
        """
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        start_time = time.time()

        try:
            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": "pcm",  # PCM for streaming
            }

            # Make streaming request
            async with self._http_client.stream(
                "POST", self.OPENAI_TTS_URL, headers=headers, json=body
            ) as response:
                response.raise_for_status()

                # Stream audio data in chunks
                chunk_index = 0
                buffer = io.BytesIO()

                async for chunk_data in response.aiter_bytes(chunk_size=self.config.chunk_size_bytes):
                    buffer.write(chunk_data)

                    # Check if we have enough data for a chunk
                    if buffer.tell() >= self.config.chunk_size_bytes:
                        chunk_bytes = buffer.getvalue()
                        buffer.seek(0)
                        buffer.truncate(0)

                        # OpenAI TTS typically returns 24kHz PCM16
                        estimated_duration_ms = (len(chunk_bytes) / (24000 * 2)) * 1000

                        yield AudioChunk(
                            data=chunk_bytes,
                            format="pcm16",
                            sample_rate=24000,
                            chunk_index=chunk_index,
                            total_chunks=-1,  # Unknown until stream ends
                            is_final=False,
                            duration_ms=estimated_duration_ms
                        )

                        chunk_index += 1

                # Handle remaining data
                remaining_data = buffer.getvalue()
                if remaining_data:
                    estimated_duration_ms = (len(remaining_data) / (24000 * 2)) * 1000

                    yield AudioChunk(
                        data=remaining_data,
                        format="pcm16",
                        sample_rate=24000,
                        chunk_index=chunk_index,
                        total_chunks=chunk_index + 1,
                        is_final=True,
                        duration_ms=estimated_duration_ms
                    )

                total_time = (time.time() - start_time) * 1000
                logger.info(
                    f"OpenAI streaming TTS completed: {len(text)} chars -> "
                    f"{chunk_index + 1} chunks in {total_time:.1f}ms"
                )

        except Exception as e:
            logger.error(f"OpenAI streaming TTS error: {e}")
            raise


class ElevenLabsStreamingTTS(StreamingTTSProvider):
    """ElevenLabs streaming TTS provider."""

    ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    async def synthesize_stream(
        self,
        text: str,
        voice: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel
        model: str = "eleven_monolingual_v1",
        **kwargs
    ) -> AsyncIterator[AudioChunk]:
        """Synthesize speech using ElevenLabs with streaming.
        
        Args:
            text: Text to synthesize
            voice: ElevenLabs voice ID
            model: ElevenLabs model ID
            **kwargs: Additional parameters (stability, similarity_boost, etc.)
            
        Yields:
            AudioChunk: Streaming audio chunks
        """
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        start_time = time.time()

        try:
            # Prepare request
            url = f"{self.ELEVENLABS_TTS_URL}/{voice}/stream"
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            }
            body = {
                "text": text,
                "model_id": model,
                "voice_settings": {
                    "stability": kwargs.get("stability", 0.5),
                    "similarity_boost": kwargs.get("similarity_boost", 0.75),
                }
            }

            # Make streaming request
            async with self._http_client.stream(
                "POST", url, headers=headers, json=body
            ) as response:
                response.raise_for_status()

                # Stream audio data in chunks
                chunk_index = 0
                buffer = io.BytesIO()

                async for chunk_data in response.aiter_bytes(chunk_size=self.config.chunk_size_bytes):
                    buffer.write(chunk_data)

                    # Check if we have enough data for a chunk
                    if buffer.tell() >= self.config.chunk_size_bytes:
                        chunk_bytes = buffer.getvalue()
                        buffer.seek(0)
                        buffer.truncate(0)

                        # ElevenLabs returns mp3, duration is harder to estimate without decoding
                        # We use a rough estimate for 128kbps mp3
                        estimated_duration_ms = (len(chunk_bytes) * 8 / 128000) * 1000

                        yield AudioChunk(
                            data=chunk_bytes,
                            format="mp3",
                            sample_rate=44100,
                            chunk_index=chunk_index,
                            total_chunks=-1,
                            is_final=False,
                            duration_ms=estimated_duration_ms
                        )

                        chunk_index += 1

                # Handle remaining data
                remaining_data = buffer.getvalue()
                if remaining_data:
                    estimated_duration_ms = (len(remaining_data) * 8 / 128000) * 1000

                    yield AudioChunk(
                        data=remaining_data,
                        format="mp3",
                        sample_rate=44100,
                        chunk_index=chunk_index,
                        total_chunks=chunk_index + 1,
                        is_final=True,
                        duration_ms=estimated_duration_ms
                    )

                total_time = (time.time() - start_time) * 1000
                logger.info(
                    f"ElevenLabs streaming TTS completed: {len(text)} chars -> "
                    f"{chunk_index + 1} chunks in {total_time:.1f}ms"
                )

        except Exception as e:
            logger.error(f"ElevenLabs streaming TTS error: {e}")
            raise


class StreamingTTSManager:
    """Manager for streaming TTS operations with buffering and timing."""

    def __init__(self, config: StreamingTTSConfig = StreamingTTSConfig()):
        """Initialize streaming TTS manager.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        self._active_streams: dict[str, asyncio.Queue] = {}
        self._providers: dict[str, StreamingTTSProvider] = {}

    def register_provider(self, name: str, provider: StreamingTTSProvider) -> None:
        """Register a TTS provider.
        
        Args:
            name: Provider name
            provider: Provider instance
        """
        self._providers[name] = provider
        logger.info(f"Registered TTS provider: {name}")

    async def generate_speech(
        self,
        text: str,
        voice: str = "default",
        provider_name: str | None = None,
        **kwargs
    ) -> bytes:
        """Generate full speech audio from text (non-streaming).
        
        Args:
            text: Text to convert
            voice: Voice model
            provider_name: Specific provider to use
            **kwargs: Additional parameters
            
        Returns:
            bytes: Full audio data
        """
        provider = None
        if provider_name:
            provider = self._providers.get(provider_name)
        elif self._providers:
            # Use first registered provider
            provider = next(iter(self._providers.values()))

        if not provider:
            raise RuntimeError("No TTS provider available")

        audio_buffer = io.BytesIO()
        async with provider:
            async for chunk in provider.synthesize_stream(text, voice, **kwargs):
                audio_buffer.write(chunk.data)

        return audio_buffer.getvalue()

    async def synthesize_stream(
        self,
        text: str,
        voice: str = "default",
        provider_name: str | None = None,
        **kwargs
    ) -> AsyncIterator[AudioChunk]:
        """Synthesize speech as an async iterator of chunks.
        
        Args:
            text: Text to convert
            voice: Voice model
            provider_name: Specific provider to use
            **kwargs: Additional parameters
            
        Yields:
            AudioChunk: Streaming audio chunks
        """
        provider = None
        if provider_name:
            provider = self._providers.get(provider_name)
        elif self._providers:
            provider = next(iter(self._providers.values()))

        if not provider:
            raise RuntimeError("No TTS provider available")

        async with provider:
            async for chunk in provider.synthesize_stream(text, voice, **kwargs):
                yield chunk

    async def start_stream(
        self,
        stream_id: str,
        provider: StreamingTTSProvider,
        text: str,
        voice: str,
        **kwargs
    ) -> None:
        """Start a streaming TTS session.
        
        Args:
            stream_id: Unique stream identifier
            provider: TTS provider instance
            text: Text to synthesize
            voice: Voice model
            **kwargs: Additional provider parameters
        """
        if stream_id in self._active_streams:
            raise ValueError(f"Stream {stream_id} already active")

        # Create buffer queue
        queue = asyncio.Queue(maxsize=self.config.max_buffer_size_chunks)
        self._active_streams[stream_id] = queue

        # Start streaming in background
        asyncio.create_task(self._stream_worker(stream_id, provider, text, voice, **kwargs))

    async def _stream_worker(
        self,
        stream_id: str,
        provider: StreamingTTSProvider,
        text: str,
        voice: str,
        **kwargs
    ) -> None:
        """Background worker for streaming TTS.
        
        Args:
            stream_id: Stream identifier
            provider: TTS provider
            text: Text to synthesize
            voice: Voice model
            **kwargs: Additional parameters
        """
        queue = self._active_streams.get(stream_id)
        if not queue:
            return

        try:
            chunk_count = 0
            async for chunk in provider.synthesize_stream(text, voice, **kwargs):
                await queue.put(chunk)
                chunk_count += 1

                # Add small delay to prevent overwhelming the client
                if self.config.enable_progressive_loading:
                    await asyncio.sleep(0.01)

            # Mark stream complete
            await queue.put(None)  # Sentinel value

        except Exception as e:
            logger.error(f"Stream worker error for {stream_id}: {e}")
            await queue.put(None)  # End stream on error

        finally:
            # Clean up after delay
            await asyncio.sleep(5.0)  # Keep queue for 5s for any late consumers
            self._active_streams.pop(stream_id, None)

    async def get_chunk(self, stream_id: str, timeout: float = 1.0) -> AudioChunk | None:
        """Get next audio chunk from stream.
        
        Args:
            stream_id: Stream identifier
            timeout: Maximum time to wait for chunk
            
        Returns:
            AudioChunk if available, None if stream ended
        """
        queue = self._active_streams.get(stream_id)
        if not queue:
            return None

        try:
            chunk = await asyncio.wait_for(queue.get(), timeout=timeout)
            return chunk
        except TimeoutError:
            return None

    def get_stream_status(self, stream_id: str) -> dict:
        """Get status of a streaming session.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream status information
        """
        queue = self._active_streams.get(stream_id)
        if not queue:
            return {"active": False}

        return {
            "active": True,
            "buffered_chunks": queue.qsize(),
            "max_buffer_size": self.config.max_buffer_size_chunks
        }

    def list_active_streams(self) -> list[str]:
        """Get list of active stream IDs.
        
        Returns:
            List of active stream identifiers
        """
        return list(self._active_streams.keys())

    async def stop_stream(self, stream_id: str) -> None:
        """Stop a streaming session.
        
        Args:
            stream_id: Stream identifier
        """
        if stream_id in self._active_streams:
            # Clear the queue to signal stop
            queue = self._active_streams[stream_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

            # Remove from active streams
            del self._active_streams[stream_id]


# Global manager instance
_tts_manager: StreamingTTSManager | None = None


def get_tts_manager() -> StreamingTTSManager:
    """Get singleton TTS manager instance.
    
    Returns:
        StreamingTTSManager instance
    """
    global _tts_manager
    if _tts_manager is None:
        from app.config.settings import get_settings
        settings = get_settings()

        _tts_manager = StreamingTTSManager()

        # Register default providers if keys are available
        if settings.deepgram_api_key:
            _tts_manager.register_provider(
                "deepgram",
                create_deepgram_tts_provider(settings.deepgram_api_key)
            )

        if settings.openai_api_key:
            _tts_manager.register_provider(
                "openai",
                create_openai_tts_provider(settings.openai_api_key)
            )

        # ElevenLabs key might be in env even if not in settings class yet
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        if elevenlabs_key:
            _tts_manager.register_provider(
                "elevenlabs",
                create_elevenlabs_tts_provider(elevenlabs_key)
            )

    return _tts_manager


def create_deepgram_tts_provider(
    api_key: str,
    config: StreamingTTSConfig = StreamingTTSConfig()
) -> DeepgramStreamingTTS:
    """Create Deepgram streaming TTS provider.
    
    Args:
        api_key: Deepgram API key
        config: Streaming configuration
        
    Returns:
        DeepgramStreamingTTS provider instance
    """
    return DeepgramStreamingTTS(api_key, config)


def create_openai_tts_provider(
    api_key: str,
    config: StreamingTTSConfig = StreamingTTSConfig()
) -> OpenAIStreamingTTS:
    """Create OpenAI streaming TTS provider.
    
    Args:
        api_key: OpenAI API key
        config: Streaming configuration
        
    Returns:
        OpenAIStreamingTTS provider instance
    """
    return OpenAIStreamingTTS(api_key, config)


def create_elevenlabs_tts_provider(
    api_key: str,
    config: StreamingTTSConfig = StreamingTTSConfig()
) -> ElevenLabsStreamingTTS:
    """Create ElevenLabs streaming TTS provider.
    
    Args:
        api_key: ElevenLabs API key
        config: Streaming configuration
        
    Returns:
        ElevenLabsStreamingTTS provider instance
    """
    return ElevenLabsStreamingTTS(api_key, config)
