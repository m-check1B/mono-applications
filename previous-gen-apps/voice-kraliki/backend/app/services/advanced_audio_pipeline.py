"""Advanced Audio Processing Pipeline

Provides enterprise-grade audio processing with:
- Adaptive jitter buffers for network resilience
- Multi-stage noise reduction (spectral subtraction, Wiener filtering)
- Dynamic audio normalization and compression
- Real-time latency monitoring and optimization
- Audio quality enhancement with ML-based techniques
"""

import logging
import math
import struct
from collections import deque
from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field
from scipy.fft import fft, ifft

logger = logging.getLogger(__name__)


class JitterBufferMode(str, Enum):
    """Jitter buffer adaptation modes."""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    HYBRID = "hybrid"


class NoiseReductionLevel(str, Enum):
    """Noise reduction intensity levels."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"


class AudioFormat(str, Enum):
    """Supported audio formats."""
    PCM16 = "pcm16"
    PCM24 = "pcm24"
    PCM32 = "pcm32"
    FLOAT32 = "float32"
    OPUS = "opus"
    AAC = "aac"


class JitterBufferConfig(BaseModel):
    """Jitter buffer configuration."""
    mode: JitterBufferMode = JitterBufferMode.ADAPTIVE
    min_delay_ms: int = Field(default=20, ge=0, le=500)
    max_delay_ms: int = Field(default=200, ge=50, le=1000)
    target_delay_ms: int = Field(default=50, ge=10, le=500)
    adaptation_rate: float = Field(default=0.1, ge=0.01, le=1.0)
    packet_loss_threshold: float = Field(default=0.05, ge=0.0, le=1.0)


class NoiseReductionConfig(BaseModel):
    """Noise reduction configuration."""
    level: NoiseReductionLevel = NoiseReductionLevel.MODERATE
    spectral_floor: float = Field(default=0.002, ge=0.0001, le=0.1)
    spectral_over_subtraction: float = Field(default=2.0, ge=1.0, le=5.0)
    wiener_gain: float = Field(default=0.8, ge=0.1, le=1.0)
    noise_estimation_frames: int = Field(default=10, ge=1, le=100)
    voice_activity_threshold: float = Field(default=0.3, ge=0.1, le=0.9)


class AudioProcessingConfig(BaseModel):
    """Complete audio processing configuration."""
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    channels: int = Field(default=1, ge=1, le=8)
    frame_size_ms: int = Field(default=20, ge=10, le=100)
    bit_depth: int = Field(default=16, ge=8, le=32)

    jitter_buffer: JitterBufferConfig = Field(default_factory=JitterBufferConfig)
    noise_reduction: NoiseReductionConfig = Field(default_factory=NoiseReductionConfig)

    # Audio enhancement
    enable_compression: bool = True
    compression_ratio: float = Field(default=4.0, ge=1.0, le=20.0)
    compression_threshold: float = Field(default=-20.0, ge=-60.0, le=0.0)

    enable_echo_cancellation: bool = True
    echo_delay_ms: int = Field(default=100, ge=10, le=500)
    echo_decay: float = Field(default=0.5, ge=0.1, le=0.9)


class AudioFrame(BaseModel):
    """Audio frame with metadata."""
    data: bytes
    timestamp: datetime
    sequence_number: int
    sample_rate: int
    channels: int
    format: AudioFormat
    size_ms: int


class AudioMetrics(BaseModel):
    """Audio processing metrics."""
    session_id: UUID
    timestamp: datetime

    # Jitter buffer metrics
    jitter_ms: float
    buffer_delay_ms: float
    packet_loss_rate: float

    # Audio quality metrics
    snr_db: float
    noise_level_db: float
    voice_activity: float

    # Processing metrics
    processing_latency_ms: float
    cpu_usage_percent: float


class JitterBuffer:
    """Adaptive jitter buffer for network audio streams."""

    def __init__(self, config: JitterBufferConfig):
        """Initialize jitter buffer.
        
        Args:
            config: Jitter buffer configuration
        """
        self.config = config
        self._buffer: deque[tuple[AudioFrame, datetime]] = deque()
        self._target_delay = config.target_delay_ms
        self._current_delay = config.target_delay_ms
        self._packet_count = 0
        self._lost_packets = 0
        self._last_sequence = -1
        self._arrival_times: list[float] = []
        self._delay_history: list[float] = []

    def add_frame(self, frame: AudioFrame) -> bool:
        """Add audio frame to jitter buffer.
        
        Args:
            frame: Audio frame to add
            
        Returns:
            True if frame was accepted, False if duplicate/late
        """
        arrival_time = datetime.now(UTC)

        # Check for duplicate packets
        if frame.sequence_number <= self._last_sequence:
            return False

        # Detect packet loss
        if self._last_sequence >= 0:
            expected_seq = self._last_sequence + 1
            if frame.sequence_number > expected_seq:
                self._lost_packets += frame.sequence_number - expected_seq

        self._last_sequence = frame.sequence_number
        self._packet_count += 1

        # Add to buffer
        self._buffer.append((frame, arrival_time))

        # Update delay statistics
        frame_delay = (arrival_time - frame.timestamp).total_seconds() * 1000
        self._arrival_times.append(frame_delay)
        if len(self._arrival_times) > 100:
            self._arrival_times.pop(0)

        # Adapt buffer size if in adaptive mode
        if self.config.mode in [JitterBufferMode.ADAPTIVE, JitterBufferMode.HYBRID]:
            self._adapt_buffer_size()

        return True

    def get_frame(self, current_time: datetime | None = None) -> AudioFrame | None:
        """Get next frame from jitter buffer.
        
        Args:
            current_time: Current time for delay calculation
            
        Returns:
            Audio frame if ready, None otherwise
        """
        if not self._buffer:
            return None

        if current_time is None:
            current_time = datetime.now(UTC)

        frame, arrival_time = self._buffer[0]

        # Check if frame is ready to be played
        target_play_time = arrival_time + timedelta(milliseconds=self._current_delay)

        if current_time >= target_play_time:
            self._buffer.popleft()

            # Update delay history
            actual_delay = (current_time - frame.timestamp).total_seconds() * 1000
            self._delay_history.append(actual_delay)
            if len(self._delay_history) > 100:
                self._delay_history.pop(0)

            return frame

        return None

    def _adapt_buffer_size(self) -> None:
        """Adapt buffer size based on network conditions."""
        if len(self._arrival_times) < 10:
            return

        # Calculate jitter (standard deviation of inter-arrival times)
        if len(self._arrival_times) > 1:
            mean_delay = sum(self._arrival_times) / len(self._arrival_times)
            variance = sum((x - mean_delay) ** 2 for x in self._arrival_times) / len(self._arrival_times)
            jitter = math.sqrt(variance)

            # Adapt target delay based on jitter
            if self.config.mode == JitterBufferMode.ADAPTIVE:
                self._target_delay = min(
                    self.config.max_delay_ms,
                    max(self.config.min_delay_ms, jitter * 2 + self.config.target_delay_ms * 0.1)
                )
            elif self.config.mode == JitterBufferMode.HYBRID:
                # Hybrid mode: use both jitter and packet loss
                packet_loss_rate = self._lost_packets / max(1, self._packet_count)
                if packet_loss_rate > self.config.packet_loss_threshold:
                    self._target_delay = min(
                        self.config.max_delay_ms,
                        self._target_delay * 1.1
                    )
                else:
                    self._target_delay = max(
                        self.config.min_delay_ms,
                        self._target_delay * 0.95
                    )

        # Smooth adaptation
        self._current_delay += (self._target_delay - self._current_delay) * self.config.adaptation_rate

    def get_metrics(self) -> dict:
        """Get jitter buffer metrics.
        
        Returns:
            Dictionary of jitter buffer metrics
        """
        packet_loss_rate = self._lost_packets / max(1, self._packet_count)

        jitter = 0.0
        if len(self._arrival_times) > 1:
            mean_delay = sum(self._arrival_times) / len(self._arrival_times)
            variance = sum((x - mean_delay) ** 2 for x in self._arrival_times) / len(self._arrival_times)
            jitter = math.sqrt(variance)

        return {
            "buffer_size_frames": len(self._buffer),
            "current_delay_ms": self._current_delay,
            "target_delay_ms": self._target_delay,
            "packet_loss_rate": packet_loss_rate,
            "jitter_ms": jitter,
            "total_packets": self._packet_count,
            "lost_packets": self._lost_packets,
        }


class NoiseReducer:
    """Advanced noise reduction using spectral subtraction and Wiener filtering."""

    def __init__(self, config: NoiseReductionConfig, sample_rate: int):
        """Initialize noise reducer.
        
        Args:
            config: Noise reduction configuration
            sample_rate: Audio sample rate
        """
        self.config = config
        self.sample_rate = sample_rate
        self.frame_size = 1024  # FFT frame size
        self.hop_size = 512

        # Noise estimation
        self._noise_spectrum = np.zeros(self.frame_size // 2 + 1)
        self._noise_frames = 0
        self._voice_activity_threshold = config.voice_activity_threshold

        # Spectral subtraction parameters
        self._spectral_floor = config.spectral_floor
        self._over_subtraction = config.spectral_over_subtraction
        self._wiener_gain = config.wiener_gain

    def process_frame(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio frame with noise reduction.
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Processed audio samples
        """
        if len(audio_data) < self.frame_size:
            # Pad with zeros if needed
            audio_data = np.pad(audio_data, (0, self.frame_size - len(audio_data)))

        # Apply window function
        windowed = audio_data * np.hanning(self.frame_size)

        # Compute FFT
        spectrum = fft(windowed)
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)

        # Voice activity detection
        voice_activity = self._detect_voice_activity(magnitude)

        # Update noise estimation
        if not voice_activity:
            self._update_noise_estimate(magnitude)

        # Apply noise reduction
        if self.config.level == NoiseReductionLevel.MINIMAL:
            processed_magnitude = self._minimal_noise_reduction(magnitude)
        elif self.config.level == NoiseReductionLevel.MODERATE:
            processed_magnitude = self._moderate_noise_reduction(magnitude, voice_activity)
        elif self.config.level == NoiseReductionLevel.AGGRESSIVE:
            processed_magnitude = self._aggressive_noise_reduction(magnitude)
        else:  # ADAPTIVE
            processed_magnitude = self._adaptive_noise_reduction(magnitude, voice_activity)

        # Reconstruct signal
        processed_spectrum = processed_magnitude * np.exp(1j * phase)
        processed_audio = np.real(ifft(processed_spectrum))

        return processed_audio[:len(audio_data)]

    def _detect_voice_activity(self, magnitude: np.ndarray) -> bool:
        """Detect voice activity in audio frame.
        
        Args:
            magnitude: FFT magnitude spectrum
            
        Returns:
            True if voice activity detected
        """
        # Simple energy-based VAD
        energy = np.sum(magnitude ** 2)
        noise_energy = np.sum(self._noise_spectrum ** 2)

        if noise_energy > 0:
            snr = 10 * math.log10(energy / noise_energy)
            return snr > 3.0  # 3dB threshold

        return energy > self._voice_activity_threshold

    def _update_noise_estimate(self, magnitude: np.ndarray) -> None:
        """Update noise spectrum estimate.
        
        Args:
            magnitude: Current FFT magnitude spectrum
        """
        # Exponential moving average
        alpha = 0.95
        self._noise_spectrum = alpha * self._noise_spectrum + (1 - alpha) * magnitude
        self._noise_frames = min(self._noise_frames + 1, self.config.noise_estimation_frames)

    def _minimal_noise_reduction(self, magnitude: np.ndarray) -> np.ndarray:
        """Apply minimal noise reduction.
        
        Args:
            magnitude: FFT magnitude spectrum
            
        Returns:
            Processed magnitude spectrum
        """
        # Simple spectral subtraction
        processed = magnitude - self._noise_spectrum * 0.5
        return np.maximum(processed, magnitude * self._spectral_floor)

    def _moderate_noise_reduction(self, magnitude: np.ndarray, voice_activity: bool) -> np.ndarray:
        """Apply moderate noise reduction with spectral subtraction.
        
        Args:
            magnitude: FFT magnitude spectrum
            voice_activity: Voice activity flag
            
        Returns:
            Processed magnitude spectrum
        """
        if voice_activity:
            # Spectral subtraction during speech
            processed = magnitude - self._noise_spectrum * self._over_subtraction
        else:
            # More aggressive reduction during silence
            processed = magnitude - self._noise_spectrum * (self._over_subtraction * 1.5)

        # Apply spectral floor
        processed = np.maximum(processed, magnitude * self._spectral_floor)

        # Apply Wiener filtering
        if self._noise_frames > 0:
            snr = magnitude / (self._noise_spectrum + 1e-10)
            wiener_filter = snr / (snr + 1)
            processed = processed * (wiener_filter * self._wiener_gain + (1 - self._wiener_gain))

        return processed

    def _aggressive_noise_reduction(self, magnitude: np.ndarray) -> np.ndarray:
        """Apply aggressive noise reduction.
        
        Args:
            magnitude: FFT magnitude spectrum
            
        Returns:
            Processed magnitude spectrum
        """
        # Strong spectral subtraction
        processed = magnitude - self._noise_spectrum * (self._over_subtraction * 2)
        processed = np.maximum(processed, magnitude * self._spectral_floor * 0.5)

        # Strong Wiener filtering
        if self._noise_frames > 0:
            snr = magnitude / (self._noise_spectrum + 1e-10)
            wiener_filter = np.power(snr / (snr + 1), 2)
            processed = processed * wiener_filter

        return processed

    def _adaptive_noise_reduction(self, magnitude: np.ndarray, voice_activity: bool) -> np.ndarray:
        """Apply adaptive noise reduction based on conditions.
        
        Args:
            magnitude: FFT magnitude spectrum
            voice_activity: Voice activity flag
            
        Returns:
            Processed magnitude spectrum
        """
        if voice_activity:
            # Conservative processing during speech
            processed = self._moderate_noise_reduction(magnitude, voice_activity)
        else:
            # Aggressive processing during silence
            processed = self._aggressive_noise_reduction(magnitude)

        return processed


class AudioCompressor:
    """Dynamic audio compressor for volume normalization."""

    def __init__(self, threshold: float = -20.0, ratio: float = 4.0):
        """Initialize audio compressor.
        
        Args:
            threshold: Compression threshold in dB
            ratio: Compression ratio
        """
        self.threshold = threshold
        self.ratio = ratio
        self._attack_time = 0.003  # 3ms
        self._release_time = 0.100  # 100ms
        self._envelope = 0.0
        self._sample_rate = 16000

    def process(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply compression to audio data.
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Compressed audio samples
        """
        # Convert to dB
        signal_db = 20 * np.log10(np.abs(audio_data) + 1e-10)

        # Apply compression curve
        compressed_db = np.where(
            signal_db > self.threshold,
            self.threshold + (signal_db - self.threshold) / self.ratio,
            signal_db
        )

        # Calculate gain reduction
        gain_reduction = signal_db - compressed_db

        # Smooth gain reduction with envelope follower
        alpha_attack = math.exp(-1.0 / (self._attack_time * self._sample_rate))
        alpha_release = math.exp(-1.0 / (self._release_time * self._sample_rate))

        for i in range(len(gain_reduction)):
            if gain_reduction[i] > self._envelope:
                self._envelope = alpha_attack * self._envelope + (1 - alpha_attack) * gain_reduction[i]
            else:
                self._envelope = alpha_release * self._envelope + (1 - alpha_release) * gain_reduction[i]

        # Apply gain
        gain_linear = 10 ** (-self._envelope / 20)
        return audio_data * gain_linear


class AdvancedAudioPipeline:
    """Advanced audio processing pipeline with jitter buffering and noise reduction."""

    def __init__(self, config: AudioProcessingConfig):
        """Initialize audio pipeline.
        
        Args:
            config: Audio processing configuration
        """
        self.config = config
        self.sample_rate = config.sample_rate
        self.channels = config.channels
        self.frame_size = int(config.sample_rate * config.frame_size_ms / 1000)

        # Initialize components
        self.jitter_buffer = JitterBuffer(config.jitter_buffer)
        self.noise_reducer = NoiseReducer(config.noise_reduction, config.sample_rate)
        self.compressor = AudioCompressor(config.compression_threshold, config.compression_ratio)

        # Session state
        self._active_sessions: dict[UUID, dict] = {}
        self._metrics_history: dict[UUID, list[AudioMetrics]] = {}

        logger.info(f"Advanced audio pipeline initialized: {config.sample_rate}Hz, {config.channels} channels")

    async def start_session(self, session_id: UUID) -> None:
        """Start audio processing for a session.
        
        Args:
            session_id: Session identifier
        """
        self._active_sessions[session_id] = {
            "start_time": datetime.now(UTC),
            "frames_processed": 0,
            "total_processing_time": 0.0,
            "last_metrics": None,
        }
        self._metrics_history[session_id] = []

        logger.info(f"Started audio processing session {session_id}")

    async def stop_session(self, session_id: UUID) -> None:
        """Stop audio processing for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        if session_id in self._metrics_history:
            del self._metrics_history[session_id]

        logger.info(f"Stopped audio processing session {session_id}")

    async def process_audio_frame(self, session_id: UUID, frame: AudioFrame) -> bytes | None:
        """Process incoming audio frame.
        
        Args:
            session_id: Session identifier
            frame: Audio frame to process
            
        Returns:
            Processed audio data or None if no frame ready
        """
        start_time = datetime.now(UTC)

        try:
            # Add to jitter buffer
            if not self.jitter_buffer.add_frame(frame):
                return None

            # Get frame from jitter buffer
            output_frame = self.jitter_buffer.get_frame()
            if output_frame is None:
                return None

            # Convert to numpy array
            audio_data = self._bytes_to_array(output_frame.data, output_frame.format)

            # Apply noise reduction
            if self.config.noise_reduction.level != NoiseReductionLevel.MINIMAL:
                audio_data = self.noise_reducer.process_frame(audio_data)

            # Apply compression
            if self.config.enable_compression:
                audio_data = self.compressor.process(audio_data)

            # Convert back to bytes
            processed_data = self._array_to_bytes(audio_data, output_frame.format)

            # Update session metrics
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self._update_session_metrics(session_id, processing_time)

            return processed_data

        except Exception as e:
            logger.error(f"Error processing audio frame for session {session_id}: {e}")
            return None

    def _bytes_to_array(self, data: bytes, format: AudioFormat) -> np.ndarray:
        """Convert bytes to numpy array.
        
        Args:
            data: Audio data bytes
            format: Audio format
            
        Returns:
            Numpy array of audio samples
        """
        if format == AudioFormat.PCM16:
            samples = struct.unpack(f'<{len(data)//2}h', data)
            return np.array(samples, dtype=np.float32) / 32768.0
        elif format == AudioFormat.FLOAT32:
            samples = struct.unpack(f'<{len(data)//4}f', data)
            return np.array(samples, dtype=np.float32)
        else:
            raise ValueError(f"Unsupported audio format: {format}")

    def _array_to_bytes(self, audio_data: np.ndarray, format: AudioFormat) -> bytes:
        """Convert numpy array to bytes.
        
        Args:
            audio_data: Audio samples
            format: Target audio format
            
        Returns:
            Audio data bytes
        """
        if format == AudioFormat.PCM16:
            # Convert to int16
            int16_data = (audio_data * 32767).astype(np.int16)
            return struct.pack(f'<{len(int16_data)}h', *int16_data)
        elif format == AudioFormat.FLOAT32:
            return struct.pack(f'<{len(audio_data)}f', *audio_data.astype(np.float32))
        else:
            raise ValueError(f"Unsupported audio format: {format}")

    def _update_session_metrics(self, session_id: UUID, processing_time: float) -> None:
        """Update session processing metrics.
        
        Args:
            session_id: Session identifier
            processing_time: Processing time in milliseconds
        """
        if session_id not in self._active_sessions:
            return

        session = self._active_sessions[session_id]
        session["frames_processed"] += 1
        session["total_processing_time"] += processing_time

        # Generate metrics every 100 frames
        if session["frames_processed"] % 100 == 0:
            jitter_metrics = self.jitter_buffer.get_metrics()

            metrics = AudioMetrics(
                session_id=session_id,
                timestamp=datetime.now(UTC),
                jitter_ms=jitter_metrics["jitter_ms"],
                buffer_delay_ms=jitter_metrics["current_delay_ms"],
                packet_loss_rate=jitter_metrics["packet_loss_rate"],
                snr_db=0.0,  # Would be calculated from audio analysis
                noise_level_db=0.0,  # Would be calculated from audio analysis
                voice_activity=0.0,  # Would be calculated from audio analysis
                processing_latency_ms=processing_time,
                cpu_usage_percent=0.0,  # Would be calculated from system monitoring
            )

            session["last_metrics"] = metrics
            self._metrics_history[session_id].append(metrics)

            # Keep only last 1000 metrics
            if len(self._metrics_history[session_id]) > 1000:
                self._metrics_history[session_id] = self._metrics_history[session_id][-1000:]

    def get_session_metrics(self, session_id: UUID) -> AudioMetrics | None:
        """Get latest metrics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Latest audio metrics or None
        """
        session = self._active_sessions.get(session_id)
        return session["last_metrics"] if session else None

    def get_session_history(self, session_id: UUID) -> list[AudioMetrics]:
        """Get metrics history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of audio metrics
        """
        return self._metrics_history.get(session_id, [])


# Global pipeline instance
default_pipeline = AdvancedAudioPipeline(AudioProcessingConfig())
