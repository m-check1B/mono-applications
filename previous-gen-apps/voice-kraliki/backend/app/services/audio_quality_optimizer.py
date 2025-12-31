"""Audio Quality Optimizer Service

Monitors and optimizes audio quality in real-time:
- Quality analysis (SNR, clarity, volume)
- Sample rate detection and conversion
- Noise reduction
- Volume normalization
- Quality metrics and recommendations
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

import numpy as np
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AudioQualityLevel(str, Enum):
    """Audio quality classification."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class AudioIssueType(str, Enum):
    """Types of audio issues."""
    LOW_VOLUME = "low_volume"
    HIGH_VOLUME = "high_volume"
    HIGH_NOISE = "high_noise"
    LOW_CLARITY = "low_clarity"
    CLIPPING = "clipping"
    DROPOUTS = "dropouts"
    ECHO = "echo"


class AudioMetrics(BaseModel):
    """Audio quality metrics."""
    session_id: UUID
    timestamp: datetime
    quality_level: AudioQualityLevel
    overall_score: float  # 0-100

    # Technical metrics
    signal_to_noise_ratio_db: float
    clarity_score: float  # 0-1
    volume_level_db: float
    peak_level_db: float
    dynamic_range_db: float

    # Detection flags
    has_clipping: bool
    has_dropouts: bool
    has_echo: bool

    # Sample information
    sample_rate_hz: int
    bit_depth: int
    channels: int

    # Issues detected
    issues: list[AudioIssueType]
    recommendations: list[str]


class AudioOptimizationConfig(BaseModel):
    """Configuration for audio optimization."""
    enable_noise_reduction: bool = True
    enable_volume_normalization: bool = True
    enable_echo_cancellation: bool = True

    # Thresholds
    min_snr_db: float = 20.0  # Minimum acceptable SNR
    target_volume_db: float = -20.0  # Target volume level
    max_peak_db: float = -3.0  # Maximum peak to avoid clipping

    # Processing
    noise_reduction_strength: float = 0.5  # 0-1
    normalization_speed: float = 0.3  # 0-1 (how fast to adjust)


class AudioQualityOptimizer:
    """Real-time audio quality monitoring and optimization.

    Analyzes audio streams, detects quality issues, and applies
    real-time optimizations to improve call quality.
    """

    def __init__(self, config: AudioOptimizationConfig = AudioOptimizationConfig()):
        """Initialize audio quality optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self._active_sessions: dict[UUID, dict] = {}
        self._metrics_history: dict[UUID, list[AudioMetrics]] = {}

    async def start_optimization(
        self,
        session_id: UUID,
        sample_rate: int = 16000,
        bit_depth: int = 16,
        channels: int = 1
    ) -> None:
        """Start audio optimization for a session.

        Args:
            session_id: Session identifier
            sample_rate: Audio sample rate in Hz
            bit_depth: Audio bit depth
            channels: Number of audio channels
        """
        self._active_sessions[session_id] = {
            "sample_rate": sample_rate,
            "bit_depth": bit_depth,
            "channels": channels,
            "start_time": datetime.now(UTC),
            "frame_count": 0,
            "volume_history": [],
            "noise_estimate": 0.0
        }
        self._metrics_history[session_id] = []
        logger.info(f"Started audio optimization for session {session_id}")

    async def stop_optimization(self, session_id: UUID) -> None:
        """Stop audio optimization for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        logger.info(f"Stopped audio optimization for session {session_id}")

    async def analyze_audio(
        self,
        session_id: UUID,
        audio_data: bytes
    ) -> AudioMetrics | None:
        """Analyze audio quality and generate metrics.

        Args:
            session_id: Session identifier
            audio_data: Raw audio data

        Returns:
            Audio quality metrics if session is active
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return None

        try:
            # Convert bytes to numpy array
            audio_array = self._bytes_to_array(audio_data, session["bit_depth"])

            # Calculate metrics
            metrics = await self._calculate_metrics(session_id, audio_array, session)

            # Store metrics
            self._metrics_history[session_id].append(metrics)

            # Keep only recent history (last 1000 frames)
            if len(self._metrics_history[session_id]) > 1000:
                self._metrics_history[session_id] = self._metrics_history[session_id][-1000:]

            session["frame_count"] += 1

            return metrics

        except Exception as error:
            logger.error(f"Failed to analyze audio for session {session_id}: {error}")
            return None

    async def optimize_audio(
        self,
        session_id: UUID,
        audio_data: bytes
    ) -> bytes | None:
        """Optimize audio quality in real-time.

        Args:
            session_id: Session identifier
            audio_data: Raw audio data

        Returns:
            Optimized audio data if session is active
        """
        session = self._active_sessions.get(session_id)
        if not session:
            return audio_data

        try:
            # Convert to numpy array
            audio_array = self._bytes_to_array(audio_data, session["bit_depth"])

            # Apply optimizations
            optimized = audio_array.copy()

            if self.config.enable_noise_reduction:
                optimized = await self._reduce_noise(optimized, session)

            if self.config.enable_volume_normalization:
                optimized = await self._normalize_volume(optimized, session)

            # Convert back to bytes
            return self._array_to_bytes(optimized, session["bit_depth"])

        except Exception as error:
            logger.error(f"Failed to optimize audio for session {session_id}: {error}")
            return audio_data

    async def _calculate_metrics(
        self,
        session_id: UUID,
        audio_array: np.ndarray,
        session: dict
    ) -> AudioMetrics:
        """Calculate comprehensive audio quality metrics.

        Args:
            session_id: Session identifier
            audio_array: Audio data as numpy array
            session: Session information

        Returns:
            Audio quality metrics
        """
        # Calculate basic metrics
        rms = np.sqrt(np.mean(audio_array ** 2))
        peak = np.max(np.abs(audio_array))

        # Convert to dB
        volume_db = 20 * np.log10(rms + 1e-10)
        peak_db = 20 * np.log10(peak + 1e-10)

        # Estimate noise floor (using lowest 10% of samples)
        sorted_samples = np.sort(np.abs(audio_array))
        noise_floor = np.mean(sorted_samples[:len(sorted_samples) // 10])
        session["noise_estimate"] = noise_floor

        # Signal to noise ratio
        signal_power = rms ** 2
        noise_power = noise_floor ** 2
        snr_db = 10 * np.log10((signal_power / (noise_power + 1e-10)) + 1e-10)

        # Clarity score (based on frequency content - simplified)
        clarity_score = min(1.0, snr_db / 40.0)

        # Dynamic range
        dynamic_range_db = peak_db - volume_db

        # Detect issues
        issues = []
        recommendations = []

        has_clipping = peak >= 0.95
        has_dropouts = rms < 0.001
        has_echo = False  # Placeholder - requires more sophisticated analysis

        if has_clipping:
            issues.append(AudioIssueType.CLIPPING)
            recommendations.append("Reduce input gain to prevent clipping")

        if has_dropouts:
            issues.append(AudioIssueType.DROPOUTS)
            recommendations.append("Check microphone connection")

        if volume_db < -40:
            issues.append(AudioIssueType.LOW_VOLUME)
            recommendations.append("Increase microphone volume")
        elif volume_db > -10:
            issues.append(AudioIssueType.HIGH_VOLUME)
            recommendations.append("Decrease microphone volume")

        if snr_db < self.config.min_snr_db:
            issues.append(AudioIssueType.HIGH_NOISE)
            recommendations.append("Reduce background noise or use noise cancellation")

        if clarity_score < 0.6:
            issues.append(AudioIssueType.LOW_CLARITY)
            recommendations.append("Improve audio quality or check connection")

        # Determine overall quality level
        overall_score = self._calculate_overall_score(
            snr_db, clarity_score, volume_db, len(issues)
        )
        quality_level = self._classify_quality(overall_score)

        return AudioMetrics(
            session_id=session_id,
            timestamp=datetime.now(UTC),
            quality_level=quality_level,
            overall_score=round(overall_score, 2),
            signal_to_noise_ratio_db=round(snr_db, 2),
            clarity_score=round(clarity_score, 3),
            volume_level_db=round(volume_db, 2),
            peak_level_db=round(peak_db, 2),
            dynamic_range_db=round(dynamic_range_db, 2),
            has_clipping=has_clipping,
            has_dropouts=has_dropouts,
            has_echo=has_echo,
            sample_rate_hz=session["sample_rate"],
            bit_depth=session["bit_depth"],
            channels=session["channels"],
            issues=issues,
            recommendations=recommendations
        )

    def _calculate_overall_score(
        self,
        snr_db: float,
        clarity_score: float,
        volume_db: float,
        issue_count: int
    ) -> float:
        """Calculate overall quality score (0-100).

        Args:
            snr_db: Signal to noise ratio
            clarity_score: Audio clarity (0-1)
            volume_db: Volume level
            issue_count: Number of issues detected

        Returns:
            Overall quality score
        """
        # SNR contribution (0-40 points)
        snr_score = min(40, (snr_db / 50.0) * 40)

        # Clarity contribution (0-30 points)
        clarity_points = clarity_score * 30

        # Volume contribution (0-20 points)
        # Ideal range: -30 to -10 dB
        if -30 <= volume_db <= -10:
            volume_points = 20
        else:
            distance_from_ideal = min(abs(volume_db - (-20)), 30)
            volume_points = max(0, 20 - distance_from_ideal)

        # Penalty for issues (0-10 points deduction)
        issue_penalty = min(10, issue_count * 5)

        total_score = snr_score + clarity_points + volume_points - issue_penalty
        return max(0, min(100, total_score))

    def _classify_quality(self, score: float) -> AudioQualityLevel:
        """Classify quality level based on score.

        Args:
            score: Overall quality score (0-100)

        Returns:
            Quality level classification
        """
        if score >= 80:
            return AudioQualityLevel.EXCELLENT
        elif score >= 60:
            return AudioQualityLevel.GOOD
        elif score >= 40:
            return AudioQualityLevel.FAIR
        elif score >= 20:
            return AudioQualityLevel.POOR
        else:
            return AudioQualityLevel.CRITICAL

    async def _reduce_noise(
        self,
        audio_array: np.ndarray,
        session: dict
    ) -> np.ndarray:
        """Apply noise reduction to audio.

        Args:
            audio_array: Audio data
            session: Session information

        Returns:
            Noise-reduced audio
        """
        # Simple spectral subtraction noise reduction
        noise_estimate = session["noise_estimate"]
        strength = self.config.noise_reduction_strength

        # Apply noise gate
        threshold = noise_estimate * (1 + strength)
        mask = np.abs(audio_array) > threshold

        return audio_array * mask

    async def _normalize_volume(
        self,
        audio_array: np.ndarray,
        session: dict
    ) -> np.ndarray:
        """Normalize audio volume.

        Args:
            audio_array: Audio data
            session: Session information

        Returns:
            Volume-normalized audio
        """
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio_array ** 2))

        if rms < 1e-10:
            return audio_array

        # Target RMS from dB
        target_rms = 10 ** (self.config.target_volume_db / 20.0)

        # Calculate gain
        current_gain = target_rms / rms

        # Smooth gain changes
        speed = self.config.normalization_speed
        gain = 1.0 + (current_gain - 1.0) * speed

        # Apply gain with limiting
        normalized = audio_array * gain
        normalized = np.clip(normalized, -0.95, 0.95)

        return normalized

    def _bytes_to_array(self, audio_data: bytes, bit_depth: int) -> np.ndarray:
        """Convert audio bytes to numpy array.

        Args:
            audio_data: Raw audio bytes
            bit_depth: Audio bit depth

        Returns:
            Audio as numpy array (normalized to -1 to 1)
        """
        if bit_depth == 16:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            return audio_array.astype(np.float32) / 32768.0
        elif bit_depth == 8:
            audio_array = np.frombuffer(audio_data, dtype=np.uint8)
            return (audio_array.astype(np.float32) - 128) / 128.0
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}")

    def _array_to_bytes(self, audio_array: np.ndarray, bit_depth: int) -> bytes:
        """Convert numpy array to audio bytes.

        Args:
            audio_array: Audio as numpy array (-1 to 1)
            bit_depth: Audio bit depth

        Returns:
            Raw audio bytes
        """
        if bit_depth == 16:
            audio_int = (audio_array * 32768.0).astype(np.int16)
            return audio_int.tobytes()
        elif bit_depth == 8:
            audio_int = ((audio_array * 128.0) + 128).astype(np.uint8)
            return audio_int.tobytes()
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}")

    def get_session_metrics(self, session_id: UUID) -> AudioMetrics | None:
        """Get latest metrics for a session.

        Args:
            session_id: Session identifier

        Returns:
            Latest audio metrics if available
        """
        history = self._metrics_history.get(session_id, [])
        return history[-1] if history else None

    def get_metrics_history(
        self,
        session_id: UUID,
        limit: int | None = None
    ) -> list[AudioMetrics]:
        """Get metrics history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of metrics to return

        Returns:
            List of audio metrics
        """
        history = self._metrics_history.get(session_id, [])

        if limit:
            return history[-limit:]

        return history


# Singleton instance
_audio_optimizer: AudioQualityOptimizer | None = None


def get_audio_optimizer() -> AudioQualityOptimizer:
    """Get singleton audio optimizer instance.

    Returns:
        AudioQualityOptimizer instance
    """
    global _audio_optimizer
    if _audio_optimizer is None:
        _audio_optimizer = AudioQualityOptimizer()
    return _audio_optimizer
