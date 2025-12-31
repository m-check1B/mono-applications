"""
Focus MCP Server

Exposes Focus capabilities to Kraliki agents via Model Context Protocol.

Run: python -m mcp_server.server
Or:  uv run python server.py

Environment:
    FOCUS_API_URL - Focus backend URL (default: http://127.0.0.1:8000)
    JWT_SECRET - JWT secret for token verification
"""

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    Resource as MCPResource,
    ResourceTemplate,
)

from tools import TOOLS, execute_tool
from resources import list_resources, read_resource
from auth import AuthContext

# Server instance
server = Server("focus-mcp")

# Store auth context (in production, use proper session management)
_auth_token: str | None = None


def set_auth_token(token: str):
    """Set authentication token for API calls."""
    global _auth_token
    _auth_token = token


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in TOOLS.values()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool."""
    if not _auth_token:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Not authenticated. Set token first."})
        )]

    # Check permissions
    auth = AuthContext(_auth_token)

    # Map tool to required permission
    permission_map = {
        "focus_get_tasks": "read:tasks",
        "focus_create_task": "create:tasks",
        "focus_update_task": "update:tasks",
        "focus_get_daily_plan": "read:tasks",
        "focus_ask_brain": "read:tasks",
        "focus_log_work": "create:tasks",
        "focus_get_projects": "read:projects",
        "focus_capture": "create:tasks",
        "focus_search": "read:tasks",
    }

    required = permission_map.get(name, "read:tasks")
    if not auth.can(required):
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Permission denied: {required}"})
        )]

    # Execute tool
    result = await execute_tool(name, _auth_token, arguments)

    return [TextContent(
        type="text",
        text=json.dumps({
            "success": result.success,
            "data": result.data,
            "error": result.error
        }, default=str)
    )]


@server.list_resources()
async def server_list_resources() -> list[MCPResource]:
    """List available resources."""
    resources = list_resources()
    return [
        MCPResource(
            uri=r["uri"],
            name=r["name"],
            description=r["description"],
            mimeType=r["mimeType"]
        )
        for r in resources
    ]


@server.read_resource()
async def server_read_resource(uri: str) -> str:
    """Read a resource."""
    if not _auth_token:
        return json.dumps({"error": "Not authenticated"})

    data = await read_resource(uri, _auth_token)
    return json.dumps(data, default=str)


async def main():
    """Run the MCP server."""
    # Get token from environment for testing
    token = os.getenv("FOCUS_MCP_TOKEN")
    if token:
        set_auth_token(token)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
