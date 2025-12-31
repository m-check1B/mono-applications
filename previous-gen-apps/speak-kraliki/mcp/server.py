#!/usr/bin/env python3
"""
Speak by Kraliki (VoP) MCP Server

Exposes VoP survey/feedback functionality to AI agents via MCP.
Port: 8120 (VoP port 8020 + 100)
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

VOP_URL = "http://127.0.0.1:8020"
app = Server("vop")


async def call_api(method: str, path: str, data: Optional[dict] = None) -> dict:
    """Call VoP API."""
    async with httpx.AsyncClient() as client:
        url = f"{VOP_URL}{path}"
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
            name="vop_list_surveys",
            description="List all surveys",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "draft, active, completed"},
                    "limit": {"type": "integer", "default": 50}
                }
            }
        ),
        Tool(
            name="vop_create_survey",
            description="Create a new employee survey",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Survey title"},
                    "description": {"type": "string"},
                    "questions": {"type": "array", "items": {"type": "object"}, "description": "Survey questions"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="vop_send_survey",
            description="Send survey to employees",
            inputSchema={
                "type": "object",
                "properties": {
                    "survey_id": {"type": "string"},
                    "employee_ids": {"type": "array", "items": {"type": "string"}},
                    "send_reminder": {"type": "boolean", "default": True}
                },
                "required": ["survey_id"]
            }
        ),
        Tool(
            name="vop_get_responses",
            description="Get survey responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "survey_id": {"type": "string"},
                    "include_anonymous": {"type": "boolean", "default": True}
                },
                "required": ["survey_id"]
            }
        ),
        Tool(
            name="vop_get_insights",
            description="Get AI-analyzed insights from survey responses",
            inputSchema={
                "type": "object",
                "properties": {
                    "survey_id": {"type": "string"},
                    "focus_area": {"type": "string", "description": "engagement, satisfaction, culture, leadership"}
                },
                "required": ["survey_id"]
            }
        ),
        Tool(
            name="vop_list_actions",
            description="List action items generated from survey insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "survey_id": {"type": "string"},
                    "status": {"type": "string", "description": "pending, in_progress, completed"}
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Calling tool: {name}")

    if name == "vop_list_surveys":
        params = f"?limit={arguments.get('limit', 50)}"
        if "status" in arguments:
            params += f"&status={arguments['status']}"
        result = await call_api("GET", f"/api/surveys{params}")
    elif name == "vop_create_survey":
        result = await call_api("POST", "/api/surveys", arguments)
    elif name == "vop_send_survey":
        result = await call_api("POST", f"/api/surveys/{arguments['survey_id']}/send", arguments)
    elif name == "vop_get_responses":
        result = await call_api("GET", f"/api/surveys/{arguments['survey_id']}/responses")
    elif name == "vop_get_insights":
        params = ""
        if "focus_area" in arguments:
            params = f"?focus_area={arguments['focus_area']}"
        result = await call_api("GET", f"/api/surveys/{arguments['survey_id']}/insights{params}")
    elif name == "vop_list_actions":
        params = ""
        if "survey_id" in arguments:
            params += f"?survey_id={arguments['survey_id']}"
        if "status" in arguments:
            params += f"&status={arguments['status']}" if params else f"?status={arguments['status']}"
        result = await call_api("GET", f"/api/actions{params}")
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
        return HTMLResponse("<h1>VoP MCP Server</h1><p>Port: 8120</p>")

    starlette_app = Starlette(routes=[Route("/", health), Route("/mcp", handle_sse)])
    config = uvicorn.Config(starlette_app, host="127.0.0.1", port=8120)
    server = uvicorn.Server(config)
    logger.info("Starting VoP MCP server on http://127.0.0.1:8120")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
