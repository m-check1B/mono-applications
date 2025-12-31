"""Tests for base types and protocols."""

import pytest
from ai_core import (
    CompletionConfig,
    CompletionResult,
    LLMProvider,
    Message,
    MessageRole,
    ProviderCapabilities,
    StreamChunk,
)


class TestMessage:
    """Tests for Message model."""

    def test_create_user_message(self):
        """Test creating a user message."""
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        msg = Message(role=MessageRole.ASSISTANT, content="Hi there!")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Hi there!"

    def test_create_system_message(self):
        """Test creating a system message."""
        msg = Message(role=MessageRole.SYSTEM, content="You are helpful")
        assert msg.role == MessageRole.SYSTEM
        assert msg.content == "You are helpful"


class TestCompletionConfig:
    """Tests for CompletionConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CompletionConfig(model="test-model")
        assert config.model == "test-model"
        assert config.max_tokens == 2000
        assert config.temperature == 0.7
        assert config.top_p is None
        assert config.stop_sequences is None
        assert config.system_prompt is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CompletionConfig(
            model="gpt-4",
            max_tokens=1000,
            temperature=0.5,
            top_p=0.9,
            stop_sequences=["END"],
            system_prompt="Be helpful",
        )
        assert config.model == "gpt-4"
        assert config.max_tokens == 1000
        assert config.temperature == 0.5
        assert config.top_p == 0.9
        assert config.stop_sequences == ["END"]
        assert config.system_prompt == "Be helpful"

    def test_temperature_validation(self):
        """Test temperature must be in valid range."""
        # Valid temperatures
        CompletionConfig(model="test", temperature=0.0)
        CompletionConfig(model="test", temperature=2.0)

        # Invalid temperatures
        with pytest.raises(ValueError):
            CompletionConfig(model="test", temperature=-0.1)
        with pytest.raises(ValueError):
            CompletionConfig(model="test", temperature=2.1)

    def test_max_tokens_validation(self):
        """Test max_tokens must be positive."""
        with pytest.raises(ValueError):
            CompletionConfig(model="test", max_tokens=0)


class TestCompletionResult:
    """Tests for CompletionResult model."""

    def test_create_result(self):
        """Test creating a completion result."""
        result = CompletionResult(
            content="Hello, how can I help?",
            model="gpt-4",
            provider=LLMProvider.OPENAI,
            input_tokens=10,
            output_tokens=7,
            finish_reason="stop",
        )
        assert result.content == "Hello, how can I help?"
        assert result.model == "gpt-4"
        assert result.provider == LLMProvider.OPENAI
        assert result.input_tokens == 10
        assert result.output_tokens == 7
        assert result.finish_reason == "stop"

    def test_default_token_counts(self):
        """Test default token counts are zero."""
        result = CompletionResult(
            content="Hello",
            model="test",
            provider=LLMProvider.ANTHROPIC,
        )
        assert result.input_tokens == 0
        assert result.output_tokens == 0


class TestStreamChunk:
    """Tests for StreamChunk model."""

    def test_token_chunk(self):
        """Test creating a token chunk."""
        chunk = StreamChunk(content="Hello", chunk_type="token")
        assert chunk.content == "Hello"
        assert chunk.chunk_type == "token"
        assert chunk.finish_reason is None

    def test_done_chunk(self):
        """Test creating a done chunk."""
        chunk = StreamChunk(
            content="",
            chunk_type="done",
            finish_reason="stop",
            input_tokens=100,
            output_tokens=50,
        )
        assert chunk.chunk_type == "done"
        assert chunk.finish_reason == "stop"
        assert chunk.input_tokens == 100
        assert chunk.output_tokens == 50

    def test_error_chunk(self):
        """Test creating an error chunk."""
        chunk = StreamChunk(content="Connection failed", chunk_type="error")
        assert chunk.chunk_type == "error"
        assert chunk.content == "Connection failed"


class TestProviderCapabilities:
    """Tests for ProviderCapabilities model."""

    def test_default_capabilities(self):
        """Test default capability values."""
        caps = ProviderCapabilities()
        assert caps.supports_streaming is True
        assert caps.supports_system_prompt is True
        assert caps.supports_function_calling is False
        assert caps.max_context_length == 128000
        assert caps.cost_tier == "standard"

    def test_custom_capabilities(self):
        """Test custom capability values."""
        caps = ProviderCapabilities(
            supports_streaming=False,
            supports_function_calling=True,
            max_context_length=200000,
            cost_tier="premium",
        )
        assert caps.supports_streaming is False
        assert caps.supports_function_calling is True
        assert caps.max_context_length == 200000
        assert caps.cost_tier == "premium"


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.GEMINI.value == "gemini"

    def test_provider_from_string(self):
        """Test creating provider from string."""
        assert LLMProvider("anthropic") == LLMProvider.ANTHROPIC
        assert LLMProvider("openai") == LLMProvider.OPENAI
        assert LLMProvider("gemini") == LLMProvider.GEMINI
