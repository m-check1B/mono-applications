#!/usr/bin/env python3
"""
Focus by Kraliki MCP Server

Exposes Focus by Kraliki functionality to AI agents via Model Context Protocol.
This enables the flow: BRAIN → FOCUS → LINEAR → SWARM

Port: 8195 (Focus by Kraliki port 8095 + 100)
"""

import asyncio
import json
import logging
from typing import Any, Optional

import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Focus by Kraliki backend URL
FOCUS_KRALIKI_URL = "http://127.0.0.1:8095"

# Create MCP server
app = Server("focus-kraliki")


async def call_focus_api(method: str, path: str, data: Optional[dict] = None) -> dict:
    """Call Focus by Kraliki API endpoint."""
    async with httpx.AsyncClient() as client:
        url = f"{FOCUS_KRALIKI_URL}{path}"

        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json=data)
        elif method == "PATCH":
            response = await client.patch(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unknown method: {method}")

        if response.status_code >= 400:
            return {"error": response.text, "status_code": response.status_code}

        return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Focus by Kraliki tools."""
    return [
        Tool(
            name="focus_list_projects",
            description="List all Focus by Kraliki projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Max projects to return", "default": 50}
                }
            }
        ),
        Tool(
            name="focus_create_project",
            description="Create a new Focus by Kraliki project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Project name"},
                    "description": {"type": "string", "description": "Project description"},
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="focus_get_project",
            description="Get a Focus by Kraliki project by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="focus_list_tasks",
            description="List tasks, optionally filtered by project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Filter by project ID"},
                    "status": {"type": "string", "description": "Filter by status (pending, in_progress, completed)"},
                    "limit": {"type": "integer", "description": "Max tasks to return", "default": 50}
                }
            }
        ),
        Tool(
            name="focus_create_task",
            description="Create a new task in Focus by Kraliki",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "project_id": {"type": "string", "description": "Project ID"},
                    "priority": {"type": "integer", "description": "Priority (1-4, 4=urgent)", "default": 2},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="focus_update_task",
            description="Update a task status or details",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "status": {"type": "string", "description": "New status (pending, in_progress, completed)"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"},
                    "priority": {"type": "integer", "description": "New priority (1-4)"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="focus_sync_to_linear",
            description="Sync a Focus by Kraliki task to Linear for swarm execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to sync"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Linear labels", "default": ["GIN", "GIN-DEV"]},
                    "priority": {"type": "string", "description": "Linear priority (urgent, high, medium, low)", "default": "medium"},
                    "team_key": {"type": "string", "description": "Linear team key", "default": "PRO"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="focus_import_strategy",
            description="Import a strategy document from brain-2026 as a Focus project",
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy_path": {"type": "string", "description": "Path to the strategy markdown file"}
                },
                "required": ["strategy_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a Focus by Kraliki tool."""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        if name == "focus_list_projects":
            limit = arguments.get("limit", 50)
            result = await call_focus_api("GET", f"/api/projects?limit={limit}")

        elif name == "focus_create_project":
            result = await call_focus_api("POST", "/api/projects", {
                "name": arguments["name"],
                "description": arguments.get("description", "")
            })

        elif name == "focus_get_project":
            project_id = arguments["project_id"]
            result = await call_focus_api("GET", f"/api/projects/{project_id}")

        elif name == "focus_list_tasks":
            params = []
            if "project_id" in arguments:
                params.append(f"projectId={arguments['project_id']}")
            if "status" in arguments:
                params.append(f"status={arguments['status']}")
            params.append(f"limit={arguments.get('limit', 50)}")

            query = "&".join(params)
            result = await call_focus_api("GET", f"/api/tasks?{query}")

        elif name == "focus_create_task":
            result = await call_focus_api("POST", "/api/tasks", {
                "title": arguments["title"],
                "description": arguments.get("description", ""),
                "projectId": arguments.get("project_id"),
                "priority": arguments.get("priority", 2),
                "tags": arguments.get("tags", [])
            })

        elif name == "focus_update_task":
            task_id = arguments["task_id"]
            update_data = {}
            if "status" in arguments:
                update_data["status"] = arguments["status"]
            if "title" in arguments:
                update_data["title"] = arguments["title"]
            if "description" in arguments:
                update_data["description"] = arguments["description"]
            if "priority" in arguments:
                update_data["priority"] = arguments["priority"]

            result = await call_focus_api("PATCH", f"/api/tasks/{task_id}", update_data)

        elif name == "focus_sync_to_linear":
            task_id = arguments["task_id"]
            result = await call_focus_api("POST", f"/linear/sync-task/{task_id}", {
                "labels": arguments.get("labels", ["GIN", "GIN-DEV"]),
                "priority": arguments.get("priority", "medium"),
                "team_key": arguments.get("team_key", "PRO")
            })

        elif name == "focus_import_strategy":
            # This calls the Kraliki brain strategy endpoint
            import aiofiles
            import re

            strategy_path = arguments["strategy_path"]

            # Read and parse strategy file
            async with aiofiles.open(strategy_path, 'r') as f:
                content = await f.read()

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Imported Strategy"

            # Create project
            project = await call_focus_api("POST", "/api/projects", {
                "name": title,
                "description": f"Imported from {strategy_path}"
            })

            if "error" in project:
                result = project
            else:
                # Extract tasks from markdown checkboxes
                tasks_created = 0
                for match in re.finditer(r'^[-*]\s*\[([ xX])\]\s*(.+)$', content, re.MULTILINE):
                    is_complete = match.group(1) != ' '
                    task_title = match.group(2).strip()

                    await call_focus_api("POST", "/api/tasks", {
                        "title": task_title,
                        "projectId": project.get("id"),
                        "status": "completed" if is_complete else "pending"
                    })
                    tasks_created += 1

                result = {
                    "success": True,
                    "project": project,
                    "tasks_created": tasks_created,
                    "message": f"Created project '{title}' with {tasks_created} tasks"
                }
        else:
            result = {"error": f"Unknown tool: {name}"}

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        result = {"error": str(e)}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server."""
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import HTMLResponse
    import uvicorn

    transport = SseServerTransport("/mcp")

    async def handle_sse(request):
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options()
            )

    async def health(request):
        return HTMLResponse("<h1>Focus by Kraliki MCP Server</h1><p>Status: Running</p>")

    starlette_app = Starlette(
        routes=[
            Route("/", health),
            Route("/mcp", handle_sse),
        ]
    )

    config = uvicorn.Config(starlette_app, host="127.0.0.1", port=8195)
    server = uvicorn.Server(config)

    logger.info("Starting Focus by Kraliki MCP server on http://127.0.0.1:8195")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
