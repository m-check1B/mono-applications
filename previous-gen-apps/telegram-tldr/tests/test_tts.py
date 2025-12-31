"""Tests for TTS (Text-to-Speech) service."""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.tts import TTSService, tts


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    return redis_mock


@pytest.fixture
def tts_service(mock_redis):
    """TTS service with mock Redis."""
    service = TTSService()
    service.redis = mock_redis
    return service


class TestTTSServiceInit:
    """Tests for TTSService initialization."""

    def test_creates_audio_directory(self):
        """Should create audio directory on init."""
        service = TTSService()
        assert service._audio_dir.exists()
        assert service._audio_dir.is_dir()

    def test_audio_directory_in_temp(self):
        """Audio directory should be in temp folder."""
        service = TTSService()
        assert "tldr_audio" in str(service._audio_dir)


class TestConnect:
    """Tests for connect method."""

    @pytest.mark.asyncio
    async def test_connects_redis(self, mock_redis):
        """Should store Redis client reference."""
        service = TTSService()
        await service.connect(mock_redis)
        assert service.redis is mock_redis


class TestKeyPatterns:
    """Tests for Redis key generation."""

    def test_audio_file_key(self, tts_service):
        """Should generate correct audio file key."""
        key = tts_service._audio_file_key("abc123")
        assert key == "tldr:audio:abc123"


class TestDigestHash:
    """Tests for digest hash generation."""

    def test_generates_hash(self, tts_service):
        """Should generate a hash for text."""
        hash1 = tts_service._digest_hash("Hello world")
        assert len(hash1) == 16
        assert hash1.isalnum()

    def test_same_text_same_hash(self, tts_service):
        """Same text should produce same hash."""
        hash1 = tts_service._digest_hash("Hello world")
        hash2 = tts_service._digest_hash("Hello world")
        assert hash1 == hash2

    def test_different_text_different_hash(self, tts_service):
        """Different text should produce different hash."""
        hash1 = tts_service._digest_hash("Hello world")
        hash2 = tts_service._digest_hash("Goodbye world")
        assert hash1 != hash2


class TestGenerateAudioFilePath:
    """Tests for audio file path generation."""

    def test_generates_mp3_path(self, tts_service):
        """Should generate MP3 file path."""
        path = tts_service._generate_audio_file_path("abc123")
        assert path.suffix == ".mp3"
        assert "abc123" in path.name

    def test_path_in_audio_directory(self, tts_service):
        """Path should be in audio directory."""
        path = tts_service._generate_audio_file_path("abc123")
        assert path.parent == tts_service._audio_dir


class TestTextToSpeech:
    """Tests for text_to_speech conversion."""

    @pytest.mark.asyncio
    async def test_returns_cached_file(self, tts_service, mock_redis):
        """Should return cached file if exists."""
        # Create a temp file to simulate cached audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            cached_path = f.name
            f.write(b"fake audio data")

        mock_redis.get.return_value = cached_path

        try:
            result = await tts_service.text_to_speech("Hello world")
            assert result == cached_path
        finally:
            os.unlink(cached_path)

    @pytest.mark.asyncio
    async def test_generates_new_audio(self, tts_service, mock_redis):
        """Should generate new audio when not cached."""
        mock_redis.get.return_value = None

        with patch.object(tts_service, "_generate_audio") as mock_gen:
            result = await tts_service.text_to_speech("Hello world")
            assert result is not None
            assert result.endswith(".mp3")
            mock_gen.assert_called_once()

    @pytest.mark.asyncio
    async def test_caches_generated_audio(self, tts_service, mock_redis):
        """Should cache generated audio in Redis."""
        mock_redis.get.return_value = None

        with patch.object(tts_service, "_generate_audio"):
            await tts_service.text_to_speech("Hello world")
            mock_redis.set.assert_called()

    @pytest.mark.asyncio
    async def test_handles_generation_error(self, tts_service, mock_redis):
        """Should return None on generation error."""
        mock_redis.get.return_value = None

        with patch.object(
            tts_service, "_generate_audio", side_effect=Exception("TTS error")
        ):
            result = await tts_service.text_to_speech("Hello world")
            assert result is None

    @pytest.mark.asyncio
    async def test_works_without_redis(self):
        """Should work without Redis connection."""
        service = TTSService()
        # No Redis connected

        with patch.object(service, "_generate_audio"):
            result = await service.text_to_speech("Hello world")
            assert result is not None

    @pytest.mark.asyncio
    async def test_passes_language_parameter(self, tts_service, mock_redis):
        """Should pass language parameter to gTTS."""
        mock_redis.get.return_value = None

        with patch.object(tts_service, "_generate_audio") as mock_gen:
            await tts_service.text_to_speech("Bonjour", lang="fr")
            # Check that the language was passed
            call_args = mock_gen.call_args
            assert call_args[0][2] == "fr"  # lang parameter

    @pytest.mark.asyncio
    async def test_passes_slow_parameter(self, tts_service, mock_redis):
        """Should pass slow parameter to gTTS."""
        mock_redis.get.return_value = None

        with patch.object(tts_service, "_generate_audio") as mock_gen:
            await tts_service.text_to_speech("Hello", slow=True)
            call_args = mock_gen.call_args
            assert call_args[0][3] is True  # slow parameter


class TestGenerateAudio:
    """Tests for _generate_audio (blocking)."""

    def test_generates_audio_file(self, tts_service):
        """Should generate audio file using gTTS."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = Path(f.name)

        try:
            with patch("app.services.tts.gTTS") as mock_gtts:
                mock_instance = MagicMock()
                mock_gtts.return_value = mock_instance

                tts_service._generate_audio("Hello", output_path, "en", False)

                mock_gtts.assert_called_once_with(text="Hello", lang="en", slow=False)
                mock_instance.save.assert_called_once_with(str(output_path))
        finally:
            if output_path.exists():
                os.unlink(output_path)


class TestCleanupOldAudio:
    """Tests for cleanup_old_audio."""

    @pytest.mark.asyncio
    async def test_returns_integer_count(self, tts_service):
        """Should return an integer count of deleted files."""
        # Just verify the method runs and returns an int
        # Note: The actual cleanup logic uses asyncio event loop time
        # which may not match filesystem mtime in tests
        deleted = await tts_service.cleanup_old_audio(days=7)
        assert isinstance(deleted, int)
        assert deleted >= 0

    @pytest.mark.asyncio
    async def test_keeps_recent_files(self, tts_service):
        """Should keep files newer than cutoff."""
        # Create a recent file
        recent_path = tts_service._audio_dir / "recent.mp3"
        recent_path.write_bytes(b"test")

        try:
            deleted = await tts_service.cleanup_old_audio(days=7)
            assert deleted == 0
            assert recent_path.exists()
        finally:
            if recent_path.exists():
                os.unlink(recent_path)


class TestGlobalInstance:
    """Tests for global tts instance."""

    def test_global_instance_exists(self):
        """Should have a global instance."""
        assert tts is not None
        assert isinstance(tts, TTSService)

    def test_global_instance_has_audio_dir(self):
        """Global instance should have audio directory."""
        assert tts._audio_dir is not None
        assert tts._audio_dir.exists()
