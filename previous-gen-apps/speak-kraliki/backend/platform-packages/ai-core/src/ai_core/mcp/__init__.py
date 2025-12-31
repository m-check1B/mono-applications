"""MCP (Model Context Protocol) server for ai-core.

Exposes ai-core LLM providers as MCP tools for use by AI agents and clients.

Basic usage:
    from ai_core.mcp import create_mcp_server, run_mcp_server
    from ai_core import create_provider, LLMProvider

    # Create provider
    provider = create_provider(LLMProvider.ANTHROPIC, api_key="sk-...")

    # Create MCP server with provider
    server = create_mcp_server(provider)

    # Run server (stdio transport by default)
    await run_mcp_server(server)
"""

from ai_core.mcp.server import (
    AICoreServer,
    create_mcp_server,
    run_mcp_server,
    MCPConfig,
)
from ai_core.mcp.tools import (
    CompletionTool,
    StreamingCompletionTool,
    ProviderInfoTool,
)

__all__ = [
    # Server
    "AICoreServer",
    "create_mcp_server",
    "run_mcp_server",
    "MCPConfig",
    # Tools
    "CompletionTool",
    "StreamingCompletionTool",
    "ProviderInfoTool",
]
