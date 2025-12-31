#!/usr/bin/env python3
"""
Voice by Kraliki MCP Server

Exposes Voice by Kraliki call center functionality to AI agents via MCP.
Port: 8100 (Voice by Kraliki port 8000 + 100)
"""

import asyncio
import json
import logging
from typing import Optional

import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VOICE_KRALIKI_URL = "http://127.0.0.1:8000"
app = Server("voice-kraliki")


async def call_api(method: str, path: str, data: Optional[dict] = None) -> dict:
    """Call Voice by Kraliki API."""
    async with httpx.AsyncClient() as client:
        url = f"{VOICE_KRALIKI_URL}{path}"
        try:
            if method == "GET":
                response = await client.get(url, timeout=10)
            elif method == "POST":
                response = await client.post(url, json=data, timeout=30)
            else:
                return {"error": f"Unknown method: {method}"}

            if response.status_code >= 400:
                return {"error": response.text, "status_code": response.status_code}
            return response.json()
        except Exception as e:
            return {"error": str(e)}


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cc_list_campaigns",
            description="List all call campaigns",
            inputSchema={"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}}
        ),
        Tool(
            name="cc_create_campaign",
            description="Create a new call campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Campaign name"},
                    "description": {"type": "string"},
                    "script": {"type": "string", "description": "Call script template"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="cc_list_agents",
            description="List voice agents",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="cc_start_call",
            description="Initiate an outbound call",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "agent_id": {"type": "string"}
                },
                "required": ["phone_number"]
            }
        ),
        Tool(
            name="cc_get_call_status",
            description="Get status of a call",
            inputSchema={
                "type": "object",
                "properties": {"call_id": {"type": "string"}},
                "required": ["call_id"]
            }
        ),
        Tool(
            name="cc_list_recordings",
            description="List call recordings",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 50}
                }
            }
        ),
        Tool(
            name="cc_get_analytics",
            description="Get call analytics and metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "period": {"type": "string", "description": "day, week, month"}
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Calling tool: {name}")

    if name == "cc_list_campaigns":
        result = await call_api("GET", f"/api/campaigns?limit={arguments.get('limit', 50)}")
    elif name == "cc_create_campaign":
        result = await call_api("POST", "/api/campaigns", arguments)
    elif name == "cc_list_agents":
        result = await call_api("GET", "/api/agents")
    elif name == "cc_start_call":
        result = await call_api("POST", "/api/calls/outbound", arguments)
    elif name == "cc_get_call_status":
        result = await call_api("GET", f"/api/calls/{arguments['call_id']}")
    elif name == "cc_list_recordings":
        params = f"?limit={arguments.get('limit', 50)}"
        if "campaign_id" in arguments:
            params += f"&campaign_id={arguments['campaign_id']}"
        result = await call_api("GET", f"/api/recordings{params}")
    elif name == "cc_get_analytics":
        params = f"?period={arguments.get('period', 'week')}"
        if "campaign_id" in arguments:
            params += f"&campaign_id={arguments['campaign_id']}"
        result = await call_api("GET", f"/api/analytics{params}")
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import HTMLResponse
    import uvicorn

    transport = SseServerTransport("/mcp")

    async def handle_sse(request):
        async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    async def health(request):
        return HTMLResponse("<h1>Voice by Kraliki MCP Server</h1><p>Port: 8100</p>")

    starlette_app = Starlette(routes=[Route("/", health), Route("/mcp", handle_sse)])
    config = uvicorn.Config(starlette_app, host="127.0.0.1", port=8100)
    server = uvicorn.Server(config)
    logger.info("Starting Voice by Kraliki MCP server on http://127.0.0.1:8100")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
