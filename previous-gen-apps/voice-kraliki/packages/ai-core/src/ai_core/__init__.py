"""AI Core - Unified LLM provider abstraction.

This package provides a unified interface for working with multiple LLM providers
(Anthropic Claude, OpenAI, Google Gemini) with support for:

- Text completion (sync and streaming)
- Provider-agnostic message format
- SSE streaming utilities
- Lazy provider loading (only import when needed)

Basic usage:
    from ai_core import Message, MessageRole, CompletionConfig
    from ai_core.providers.claude import create_claude_provider

    provider = create_claude_provider(api_key="sk-...")

    messages = [
        Message(role=MessageRole.USER, content="Hello!")
    ]

    config = CompletionConfig(model="claude-sonnet-4-20250514", max_tokens=1000)

    # Synchronous completion
    result = await provider.complete(messages, config)
    print(result.content)

    # Streaming completion
    async for chunk in provider.stream(messages, config):
        print(chunk.content, end="")
"""

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
from ai_core.streaming.sse import (
    SSEEvent,
    create_sse_response_headers,
    format_sse_chunk,
    format_sse_event,
    parse_sse_event,
    stream_to_sse,
)

__version__ = "0.1.0"

__all__ = [
    # Core types
    "BaseTextProvider",
    "CompletionConfig",
    "CompletionResult",
    "LLMProvider",
    "Message",
    "MessageRole",
    "ProviderCapabilities",
    "StreamChunk",
    "TextProvider",
    # SSE utilities
    "SSEEvent",
    "create_sse_response_headers",
    "format_sse_chunk",
    "format_sse_event",
    "parse_sse_event",
    "stream_to_sse",
    # Factory functions (lazy imports)
    "create_provider",
    "get_available_providers",
    # MCP utilities (lazy imports)
    "create_mcp_server",
    "get_mcp_available",
]


def get_available_providers() -> list[LLMProvider]:
    """Get list of providers that have their dependencies installed.

    Returns:
        List of available LLMProvider types
    """
    available = []

    try:
        import anthropic  # noqa: F401
        available.append(LLMProvider.ANTHROPIC)
    except ImportError:
        pass

    try:
        import openai  # noqa: F401
        available.append(LLMProvider.OPENAI)
    except ImportError:
        pass

    try:
        import google.generativeai  # noqa: F401
        available.append(LLMProvider.GEMINI)
    except ImportError:
        pass

    return available


def create_provider(
    provider_type: LLMProvider,
    api_key: str,
    model: str | None = None,
    **kwargs,
) -> BaseTextProvider:
    """Factory function to create a provider instance.

    Args:
        provider_type: Type of provider to create
        api_key: API key for the provider
        model: Optional default model
        **kwargs: Additional provider-specific arguments

    Returns:
        Configured provider instance

    Raises:
        ImportError: If provider dependencies are not installed
        ValueError: If provider type is unknown
    """
    if provider_type == LLMProvider.ANTHROPIC:
        from ai_core.providers.claude import create_claude_provider
        return create_claude_provider(api_key=api_key, model=model)

    elif provider_type == LLMProvider.OPENAI:
        from ai_core.providers.openai import create_openai_provider
        return create_openai_provider(
            api_key=api_key,
            model=model,
            base_url=kwargs.get("base_url"),
        )

    elif provider_type == LLMProvider.GEMINI:
        from ai_core.providers.gemini import create_gemini_provider
        return create_gemini_provider(api_key=api_key, model=model)

    else:
        raise ValueError(f"Unknown provider type: {provider_type}")


def get_mcp_available() -> bool:
    """Check if MCP SDK is installed.

    Returns:
        True if MCP SDK is available
    """
    try:
        import mcp  # noqa: F401
        return True
    except ImportError:
        return False


def create_mcp_server(
    provider: BaseTextProvider,
    server_name: str = "ai-core",
    default_model: str | None = None,
):
    """Factory function to create MCP server.

    Args:
        provider: Configured ai-core provider
        server_name: Name for the MCP server
        default_model: Default model to use

    Returns:
        Configured AICoreServer instance

    Raises:
        ImportError: If MCP SDK is not installed

    Example:
        from ai_core import create_provider, create_mcp_server, LLMProvider

        provider = create_provider(LLMProvider.ANTHROPIC, api_key="sk-...")
        server = create_mcp_server(provider)
        await server.run()
    """
    from ai_core.mcp.server import AICoreServer, MCPConfig

    config = MCPConfig(
        server_name=server_name,
        default_model=default_model,
    )
    return AICoreServer(provider=provider, config=config)
