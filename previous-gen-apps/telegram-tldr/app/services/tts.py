"""Text-to-Speech service for newsletter audio digests."""

import asyncio
import logging
import os
import tempfile
from pathlib import Path

import redis.asyncio as redis
from gtts import gTTS

logger = logging.getLogger(__name__)


class TTSService:
    """Converts text to audio using Google TTS."""

    def __init__(self):
        self.redis: redis.Redis | None = None
        self._audio_dir = Path(tempfile.gettempdir()) / "tldr_audio"
        self._audio_dir.mkdir(exist_ok=True)

    async def connect(self, redis_client: redis.Redis):
        """Connect using existing Redis client."""
        self.redis = redis_client

    def _audio_file_key(self, digest_hash: str) -> str:
        """Key for storing audio file path in Redis."""
        return f"tldr:audio:{digest_hash}"

    def _generate_audio_file_path(self, digest_hash: str) -> Path:
        """Generate unique file path for audio."""
        return self._audio_dir / f"{digest_hash}.mp3"

    def _digest_hash(self, text: str) -> str:
        """Generate hash of digest text for caching."""
        import hashlib

        return hashlib.md5(text.encode()).hexdigest()[:16]

    async def text_to_speech(
        self, text: str, lang: str = "en", slow: bool = False
    ) -> str | None:
        """Convert text to speech and return file path.

        Uses caching: returns cached file if digest was already converted.

        Args:
            text: Text to convert to speech
            lang: Language code (default: "en")
            slow: Slow speech mode

        Returns:
            Path to audio file or None if failed
        """
        digest_hash = self._digest_hash(text)

        # Check cache
        if self.redis:
            cached_path = await self.redis.get(self._audio_file_key(digest_hash))
            if cached_path and os.path.exists(cached_path):
                logger.debug(f"Using cached audio: {cached_path}")
                return cached_path

        audio_file = self._generate_audio_file_path(digest_hash)

        # Run gTTS in thread pool (blocking I/O)
        try:
            await asyncio.to_thread(self._generate_audio, text, audio_file, lang, slow)

            # Cache the file path (expire in 7 days)
            if self.redis:
                await self.redis.set(
                    self._audio_file_key(digest_hash), str(audio_file), ex=7 * 24 * 3600
                )

            logger.info(f"Generated audio for digest: {audio_file}")
            return str(audio_file)

        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    def _generate_audio(self, text: str, output_file: Path, lang: str, slow: bool):
        """Generate audio file using gTTS (blocking)."""
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(str(output_file))

    async def cleanup_old_audio(self, days: int = 7) -> int:
        """Remove old audio files.

        Returns count of deleted files.
        """
        cutoff = asyncio.get_event_loop().time() - (days * 24 * 3600)
        deleted = 0

        for file_path in self._audio_dir.glob("*.mp3"):
            file_age = os.path.getmtime(file_path)
            if file_age < cutoff:
                try:
                    os.remove(file_path)
                    deleted += 1
                except OSError:
                    pass

        logger.info(f"Cleaned up {deleted} old audio files")
        return deleted


# Global instance
tts = TTSService()
