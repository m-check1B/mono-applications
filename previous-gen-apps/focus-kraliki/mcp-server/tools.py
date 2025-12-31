"""
Focus MCP Server - Tool Definitions

Tools that Kraliki agents can call to interact with Focus.
All tools use OpenRouter-style cheap models, no expensive defaults.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
import os

# Focus API base URL
FOCUS_API_URL = os.getenv("FOCUS_API_URL", "http://127.0.0.1:8000")


@dataclass
class ToolResult:
    """Result from a tool call."""
    success: bool
    data: Any
    error: Optional[str] = None


async def call_focus_api(
    method: str,
    endpoint: str,
    token: str,
    data: Optional[Dict] = None
) -> Dict:
    """Call Focus API endpoint."""
    async with httpx.AsyncClient() as client:
        url = f"{FOCUS_API_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}

        if method == "GET":
            response = await client.get(url, headers=headers, params=data)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")

        response.raise_for_status()
        return response.json()


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = {
    "focus_get_tasks": {
        "name": "focus_get_tasks",
        "description": "Get tasks from Focus. Filter by status, priority, or project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "done", "blocked"],
                    "description": "Filter by task status"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Filter by priority"
                },
                "project_id": {
                    "type": "string",
                    "description": "Filter by project ID"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Max tasks to return"
                }
            }
        }
    },
    "focus_create_task": {
        "name": "focus_create_task",
        "description": "Create a new task in Focus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title"
                },
                "description": {
                    "type": "string",
                    "description": "Task description"
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "default": "medium"
                },
                "project_id": {
                    "type": "string",
                    "description": "Project to add task to"
                }
            },
            "required": ["title"]
        }
    },
    "focus_update_task": {
        "name": "focus_update_task",
        "description": "Update a task status or add notes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID to update"
                },
                "status": {
                    "type": "string",
                    "enum": ["todo", "in_progress", "done", "blocked"]
                },
                "notes": {
                    "type": "string",
                    "description": "Add notes to task"
                }
            },
            "required": ["task_id"]
        }
    },
    "focus_get_daily_plan": {
        "name": "focus_get_daily_plan",
        "description": "Get the Brain's daily plan with prioritized tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    "focus_ask_brain": {
        "name": "focus_ask_brain",
        "description": "Ask Focus Brain a question about tasks, priorities, or what to work on.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Question to ask the Brain"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context"
                }
            },
            "required": ["question"]
        }
    },
    "focus_log_work": {
        "name": "focus_log_work",
        "description": "Log time spent working on a task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Minutes worked"
                },
                "notes": {
                    "type": "string",
                    "description": "Work notes"
                }
            },
            "required": ["task_id", "duration_minutes"]
        }
    },
    "focus_get_projects": {
        "name": "focus_get_projects",
        "description": "Get active projects.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "completed", "archived"]
                },
                "workspace_id": {
                    "type": "string"
                }
            }
        }
    },
    "focus_capture": {
        "name": "focus_capture",
        "description": "Capture an idea, note, or task via Brain AI-first capture.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Natural language input to capture"
                },
                "create": {
                    "type": "boolean",
                    "default": True,
                    "description": "Create item immediately"
                }
            },
            "required": ["input"]
        }
    },
    "focus_search": {
        "name": "focus_search",
        "description": "Search across Focus data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "type": {
                    "type": "string",
                    "enum": ["tasks", "projects", "knowledge", "all"],
                    "default": "all"
                }
            },
            "required": ["query"]
        }
    }
}


# =============================================================================
# TOOL HANDLERS
# =============================================================================

async def handle_focus_get_tasks(token: str, params: Dict) -> ToolResult:
    """Get tasks from Focus API."""
    try:
        data = await call_focus_api("GET", "/tasks", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_create_task(token: str, params: Dict) -> ToolResult:
    """Create task via Focus API."""
    try:
        data = await call_focus_api("POST", "/tasks", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_update_task(token: str, params: Dict) -> ToolResult:
    """Update task via Focus API."""
    try:
        task_id = params.pop("task_id")
        data = await call_focus_api("PUT", f"/tasks/{task_id}", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_get_daily_plan(token: str, params: Dict) -> ToolResult:
    """Get daily plan from Brain."""
    try:
        data = await call_focus_api("GET", "/brain/daily-plan", token)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_ask_brain(token: str, params: Dict) -> ToolResult:
    """Ask Brain a question."""
    try:
        data = await call_focus_api("POST", "/brain/ask", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_log_work(token: str, params: Dict) -> ToolResult:
    """Log time entry."""
    try:
        data = await call_focus_api("POST", "/time-entries", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_get_projects(token: str, params: Dict) -> ToolResult:
    """Get projects."""
    try:
        data = await call_focus_api("GET", "/projects", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_capture(token: str, params: Dict) -> ToolResult:
    """Capture via Brain AI-first."""
    try:
        data = await call_focus_api("POST", "/brain/capture", token, params)
        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


async def handle_focus_search(token: str, params: Dict) -> ToolResult:
    """Search Focus data."""
    try:
        # Route to appropriate search endpoint
        search_type = params.get("type", "all")
        query = params.get("query", "")

        if search_type == "tasks":
            data = await call_focus_api("GET", "/tasks/search", token, {"q": query})
        elif search_type == "projects":
            data = await call_focus_api("GET", "/projects/search", token, {"q": query})
        else:
            # General search via Brain
            data = await call_focus_api("POST", "/brain/ask", token, {
                "question": f"Search for: {query}"
            })

        return ToolResult(success=True, data=data)
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))


# Handler mapping
TOOL_HANDLERS = {
    "focus_get_tasks": handle_focus_get_tasks,
    "focus_create_task": handle_focus_create_task,
    "focus_update_task": handle_focus_update_task,
    "focus_get_daily_plan": handle_focus_get_daily_plan,
    "focus_ask_brain": handle_focus_ask_brain,
    "focus_log_work": handle_focus_log_work,
    "focus_get_projects": handle_focus_get_projects,
    "focus_capture": handle_focus_capture,
    "focus_search": handle_focus_search,
}


async def execute_tool(name: str, token: str, params: Dict) -> ToolResult:
    """Execute a tool by name."""
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return ToolResult(success=False, data=None, error=f"Unknown tool: {name}")
    return await handler(token, params)
