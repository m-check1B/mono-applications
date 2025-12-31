"""MCP Server implementation for ai-core.

Provides Model Context Protocol server that exposes LLM providers as tools.

Example:
    # Run as standalone server
    python -m ai_core.mcp.server --provider anthropic --api-key $ANTHROPIC_API_KEY

    # Or integrate with existing application
    from ai_core.mcp import create_mcp_server, run_mcp_server

    server = create_mcp_server(provider)
    await run_mcp_server(server)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Try importing MCP SDK
_mcp_available = False
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolResult,
        ListToolsResult,
    )
    _mcp_available = True
    logger.debug("MCP SDK available")
except ImportError:
    logger.warning("MCP SDK not installed. Install with: pip install mcp")
    Server = None
    Tool = None

# Import ai-core types
from ai_core.base import (
    BaseTextProvider,
    CompletionConfig,
    Message,
    MessageRole,
    LLMProvider,
)


@dataclass
class MCPConfig:
    """Configuration for MCP server."""
    server_name: str = "ai-core"
    server_version: str = "0.1.0"
    default_model: Optional[str] = None
    max_tokens_limit: int = 100000
    allowed_models: list[str] = field(default_factory=list)


class AICoreServer:
    """MCP Server that exposes ai-core LLM providers as tools.

    Features:
    - Expose LLM completion as MCP tool
    - Streaming completion support
    - Provider information tool
    - Custom tool registration

    Usage:
        from ai_core import create_provider, LLMProvider
        from ai_core.mcp import AICoreServer

        provider = create_provider(LLMProvider.ANTHROPIC, api_key="sk-...")
        server = AICoreServer(provider)
        await server.run()
    """

    def __init__(
        self,
        provider: BaseTextProvider,
        config: Optional[MCPConfig] = None,
    ):
        """Initialize MCP server with LLM provider.

        Args:
            provider: Configured ai-core provider
            config: Optional server configuration
        """
        if not _mcp_available:
            raise ImportError(
                "MCP SDK not installed. Install with: pip install mcp"
            )

        self.provider = provider
        self.config = config or MCPConfig()
        self._server = Server(self.config.server_name)
        self._custom_tools: dict[str, callable] = {}

        # Register handlers
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP server handlers."""

        @self._server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            tools = [
                Tool(
                    name="ai_core_complete",
                    description=f"Generate text completion using {self.provider.provider_type.value} LLM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The prompt or message to send to the LLM"
                            },
                            "system_prompt": {
                                "type": "string",
                                "description": "Optional system prompt"
                            },
                            "model": {
                                "type": "string",
                                "description": f"Model to use (default: {self.config.default_model or 'provider default'})"
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximum tokens to generate",
                                "default": 2000
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Sampling temperature (0.0-2.0)",
                                "default": 0.7
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="ai_core_provider_info",
                    description="Get information about the configured LLM provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_capabilities": {
                                "type": "boolean",
                                "description": "Include detailed capabilities",
                                "default": True
                            }
                        }
                    }
                ),
            ]

            # Add custom tools
            for name, handler in self._custom_tools.items():
                if hasattr(handler, "_mcp_tool_schema"):
                    tools.append(handler._mcp_tool_schema)

            return tools

        @self._server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
            """Handle tool calls."""
            try:
                if name == "ai_core_complete":
                    return await self._handle_complete(arguments)
                elif name == "ai_core_provider_info":
                    return await self._handle_provider_info(arguments)
                elif name in self._custom_tools:
                    result = await self._custom_tools[name](arguments)
                    return [TextContent(type="text", text=str(result))]
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _handle_complete(self, arguments: dict) -> Sequence[TextContent]:
        """Handle completion tool call."""
        prompt = arguments.get("prompt", "")
        system_prompt = arguments.get("system_prompt")
        model = arguments.get("model", self.config.default_model)
        max_tokens = min(
            arguments.get("max_tokens", 2000),
            self.config.max_tokens_limit
        )
        temperature = arguments.get("temperature", 0.7)

        # Validate model if allowed_models specified
        if self.config.allowed_models and model:
            if model not in self.config.allowed_models:
                return [TextContent(
                    type="text",
                    text=f"Model '{model}' not allowed. Allowed models: {self.config.allowed_models}"
                )]

        # Build messages
        messages = [Message(role=MessageRole.USER, content=prompt)]

        # Build config
        config = CompletionConfig(
            model=model or "default",  # Provider will use its default
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
        )

        # Execute completion
        result = await self.provider.complete(messages, config)

        # Format response
        response_text = f"{result.content}\n\n---\nTokens: {result.input_tokens} in / {result.output_tokens} out"

        return [TextContent(type="text", text=response_text)]

    async def _handle_provider_info(self, arguments: dict) -> Sequence[TextContent]:
        """Handle provider info tool call."""
        include_capabilities = arguments.get("include_capabilities", True)

        info = {
            "provider": self.provider.provider_type.value,
            "server_name": self.config.server_name,
            "server_version": self.config.server_version,
        }

        if include_capabilities:
            caps = self.provider.capabilities
            info["capabilities"] = {
                "streaming": caps.supports_streaming,
                "system_prompt": caps.supports_system_prompt,
                "function_calling": caps.supports_function_calling,
                "max_context_length": caps.max_context_length,
                "cost_tier": caps.cost_tier,
            }

        if self.config.default_model:
            info["default_model"] = self.config.default_model

        if self.config.allowed_models:
            info["allowed_models"] = self.config.allowed_models

        # Format as readable text
        lines = ["AI Core Provider Info", "=" * 30]
        for key, value in info.items():
            if isinstance(value, dict):
                lines.append(f"\n{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")

        return [TextContent(type="text", text="\n".join(lines))]

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: callable
    ) -> None:
        """Register a custom tool.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool input
            handler: Async function to handle tool calls
        """
        if not _mcp_available:
            raise ImportError("MCP SDK not installed")

        # Store schema on handler for list_tools
        handler._mcp_tool_schema = Tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        self._custom_tools[name] = handler
        logger.info(f"Registered custom tool: {name}")

    async def run(self) -> None:
        """Run the MCP server using stdio transport."""
        if not _mcp_available:
            raise ImportError("MCP SDK not installed")

        logger.info(f"Starting MCP server: {self.config.server_name}")

        async with stdio_server() as (read_stream, write_stream):
            await self._server.run(
                read_stream,
                write_stream,
                self._server.create_initialization_options()
            )


def create_mcp_server(
    provider: BaseTextProvider,
    config: Optional[MCPConfig] = None,
) -> AICoreServer:
    """Factory function to create MCP server.

    Args:
        provider: Configured ai-core provider
        config: Optional server configuration

    Returns:
        Configured AICoreServer instance
    """
    return AICoreServer(provider=provider, config=config)


async def run_mcp_server(server: AICoreServer) -> None:
    """Run MCP server.

    Args:
        server: AICoreServer instance to run
    """
    await server.run()


# CLI entry point
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="AI Core MCP Server")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "gemini"],
        default="anthropic",
        help="LLM provider to use"
    )
    parser.add_argument(
        "--api-key",
        help="API key (or use *_API_KEY env var)"
    )
    parser.add_argument(
        "--model",
        help="Default model to use"
    )
    parser.add_argument(
        "--server-name",
        default="ai-core",
        help="MCP server name"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key
    if not api_key:
        env_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }
        api_key = os.getenv(env_map.get(args.provider, ""))

    if not api_key:
        print(f"Error: API key required for {args.provider}")
        exit(1)

    # Create provider
    from ai_core import create_provider, LLMProvider

    provider_map = {
        "anthropic": LLMProvider.ANTHROPIC,
        "openai": LLMProvider.OPENAI,
        "gemini": LLMProvider.GEMINI,
    }

    provider = create_provider(
        provider_map[args.provider],
        api_key=api_key,
        model=args.model,
    )

    # Create and run server
    config = MCPConfig(
        server_name=args.server_name,
        default_model=args.model,
    )
    server = create_mcp_server(provider, config)

    print(f"Starting {args.server_name} MCP server with {args.provider} provider...")
    asyncio.run(server.run())
