"""Tests for base protocols and types."""

import pytest
from voice_core.base import (
    AudioFormat,
    SessionState,
    ProviderCapabilities,
    SessionConfig,
    AudioChunk,
    TextMessage,
    FunctionCall,
    ProviderEvent,
)


class TestAudioFormat:
    """Tests for AudioFormat enum."""

    def test_pcm16_value(self):
        assert AudioFormat.PCM16.value == "pcm16"

    def test_ulaw_value(self):
        assert AudioFormat.ULAW.value == "ulaw"

    def test_all_formats(self):
        formats = [f.value for f in AudioFormat]
        assert "pcm16" in formats
        assert "ulaw" in formats
        assert "opus" in formats
        assert "mp3" in formats


class TestSessionState:
    """Tests for SessionState enum."""

    def test_idle_state(self):
        assert SessionState.IDLE.value == "idle"

    def test_state_transitions(self):
        # Verify all expected states exist
        states = [s.value for s in SessionState]
        expected = ["idle", "connecting", "connected", "active", "disconnecting", "disconnected", "error"]
        for state in expected:
            assert state in states


class TestProviderCapabilities:
    """Tests for ProviderCapabilities model."""

    def test_create_capabilities(self):
        caps = ProviderCapabilities(
            supports_realtime=True,
            supports_text=True,
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=True,
            supports_streaming=True,
            audio_formats=[AudioFormat.PCM16],
        )
        assert caps.supports_realtime is True
        assert caps.supports_multimodal is False
        assert AudioFormat.PCM16 in caps.audio_formats

    def test_default_values(self):
        caps = ProviderCapabilities(
            supports_realtime=False,
            supports_text=False,
            supports_audio=True,
            supports_multimodal=False,
            supports_function_calling=False,
            supports_streaming=False,
        )
        assert caps.audio_formats == []
        assert caps.max_session_duration is None
        assert caps.cost_tier == "standard"


class TestSessionConfig:
    """Tests for SessionConfig model."""

    def test_create_config(self):
        config = SessionConfig(
            model_id="gemini-2.5-flash",
            system_prompt="You are helpful.",
        )
        assert config.model_id == "gemini-2.5-flash"
        assert config.audio_format == AudioFormat.PCM16  # default
        assert config.sample_rate == 16000  # default
        assert config.temperature == 0.7  # default

    def test_config_with_tools(self):
        config = SessionConfig(
            model_id="test",
            tools=[{"type": "function", "function": {"name": "test"}}],
        )
        assert len(config.tools) == 1


class TestAudioChunk:
    """Tests for AudioChunk model."""

    def test_create_chunk(self):
        chunk = AudioChunk(
            data=b"test_audio_data",
            format=AudioFormat.PCM16,
            sample_rate=16000,
        )
        assert chunk.data == b"test_audio_data"
        assert chunk.format == AudioFormat.PCM16
        assert chunk.timestamp is None

    def test_chunk_with_timestamp(self):
        chunk = AudioChunk(
            data=b"data",
            format=AudioFormat.ULAW,
            sample_rate=8000,
            timestamp=1.5,
        )
        assert chunk.timestamp == 1.5


class TestTextMessage:
    """Tests for TextMessage model."""

    def test_create_message(self):
        msg = TextMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp is None


class TestFunctionCall:
    """Tests for FunctionCall model."""

    def test_create_function_call(self):
        call = FunctionCall(
            id="call_123",
            name="get_weather",
            arguments={"location": "Prague"},
        )
        assert call.id == "call_123"
        assert call.name == "get_weather"
        assert call.arguments["location"] == "Prague"


class TestProviderEvent:
    """Tests for ProviderEvent model."""

    def test_create_event(self):
        event = ProviderEvent(
            type="audio.output",
            data={"audio": b"data", "format": "pcm16"},
        )
        assert event.type == "audio.output"
        assert event.data["format"] == "pcm16"
