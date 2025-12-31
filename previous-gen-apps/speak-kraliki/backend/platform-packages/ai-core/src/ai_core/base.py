"""Base protocols and types for LLM providers.

This module defines the abstract interfaces that all LLM providers must implement
for unified text generation and streaming.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncGenerator, Optional, Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM provider types."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"


class MessageRole(str, Enum):
    """Standard message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """A chat message."""
    role: MessageRole
    content: str


class CompletionConfig(BaseModel):
    """Configuration for text completion."""
    model: str = Field(description="Model identifier")
    max_tokens: int = Field(default=2000, ge=1, le=100000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    stop_sequences: Optional[list[str]] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class CompletionResult(BaseModel):
    """Result from a completion request."""
    content: str
    model: str
    provider: LLMProvider
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: Optional[str] = None


class StreamChunk(BaseModel):
    """A chunk from a streaming response."""
    content: str
    chunk_type: str = "token"  # token, done, error
    finish_reason: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class ProviderCapabilities(BaseModel):
    """Provider capability descriptor."""
    supports_streaming: bool = True
    supports_system_prompt: bool = True
    supports_function_calling: bool = False
    max_context_length: int = 128000
    cost_tier: str = "standard"


@runtime_checkable
class TextProvider(Protocol):
    """Protocol for text-based LLM providers."""

    @property
    def provider_type(self) -> LLMProvider:
        """Get the provider type."""
        ...

    @property
    def capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        ...

    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> CompletionResult:
        """Generate a completion for the given messages.

        Args:
            messages: List of messages in the conversation
            config: Completion configuration

        Returns:
            CompletionResult with the generated text
        """
        ...

    async def stream(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a completion for the given messages.

        Args:
            messages: List of messages in the conversation
            config: Completion configuration

        Yields:
            StreamChunk for each token/event
        """
        ...


class BaseTextProvider(ABC):
    """Base class for text providers with common functionality."""

    def __init__(self, api_key: str):
        """Initialize the provider with an API key.

        Args:
            api_key: Provider API key
        """
        self._api_key = api_key

    @property
    @abstractmethod
    def provider_type(self) -> LLMProvider:
        """Get the provider type."""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities."""
        ...

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> CompletionResult:
        """Generate a completion for the given messages."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        config: CompletionConfig,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a completion for the given messages."""
        ...

    def _validate_config(self, config: CompletionConfig) -> None:
        """Validate configuration against provider capabilities.

        Args:
            config: Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        if config.system_prompt and not self.capabilities.supports_system_prompt:
            raise ValueError(f"Provider {self.provider_type} does not support system prompts")
