"""LLM Provider implementations."""

from ai_core.base import (
    BaseTextProvider,
    CompletionConfig,
    CompletionResult,
    LLMProvider,
    Message,
    MessageRole,
    ProviderCapabilities,
    StreamChunk,
    TextProvider,
)

__all__ = [
    "BaseTextProvider",
    "CompletionConfig",
    "CompletionResult",
    "LLMProvider",
    "Message",
    "MessageRole",
    "ProviderCapabilities",
    "StreamChunk",
    "TextProvider",
]

# Lazy imports for optional dependencies
def get_claude_provider():
    """Get Claude provider class (requires anthropic extra)."""
    from ai_core.providers.claude import ClaudeProvider
    return ClaudeProvider


def get_openai_provider():
    """Get OpenAI provider class (requires openai extra)."""
    from ai_core.providers.openai import OpenAIProvider
    return OpenAIProvider


def get_gemini_provider():
    """Get Gemini provider class (requires gemini extra)."""
    from ai_core.providers.gemini import GeminiProvider
    return GeminiProvider
