"""
Focus MCP Server - Resource Definitions

Resources that Kraliki agents can read from Focus.
URI pattern: focus://{type}/{id}
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import httpx
import os

FOCUS_API_URL = os.getenv("FOCUS_API_URL", "http://127.0.0.1:8000")


@dataclass
class Resource:
    """MCP Resource definition."""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"


# Resource templates
RESOURCE_TEMPLATES = {
    "focus://tasks/{id}": Resource(
        uri="focus://tasks/{id}",
        name="Task Details",
        description="Get full task details including project, subtasks, and history"
    ),
    "focus://projects/{id}": Resource(
        uri="focus://projects/{id}",
        name="Project Details",
        description="Get project with all tasks and progress"
    ),
    "focus://goals/{id}": Resource(
        uri="focus://goals/{id}",
        name="Goal Details",
        description="Get goal with progress and linked tasks"
    ),
    "focus://brain/context": Resource(
        uri="focus://brain/context",
        name="Brain Context",
        description="Current user context for AI - tasks, priorities, patterns"
    ),
    "focus://brain/priorities": Resource(
        uri="focus://brain/priorities",
        name="Brain Priorities",
        description="Current prioritized task list from Brain"
    ),
    "focus://knowledge/{id}": Resource(
        uri="focus://knowledge/{id}",
        name="Knowledge Item",
        description="Get knowledge item (idea, note, plan, etc.)"
    ),
    "focus://summary": Resource(
        uri="focus://summary",
        name="Focus Summary",
        description="Summary of all captured items by type"
    ),
}


async def call_focus_api(endpoint: str, token: str) -> Dict:
    """Call Focus API endpoint."""
    async with httpx.AsyncClient() as client:
        url = f"{FOCUS_API_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def read_resource(uri: str, token: str) -> Optional[Dict[str, Any]]:
    """
    Read a resource by URI.

    URI patterns:
    - focus://tasks/{id}
    - focus://projects/{id}
    - focus://goals/{id}
    - focus://brain/context
    - focus://brain/priorities
    - focus://knowledge/{id}
    - focus://summary
    """
    try:
        if uri.startswith("focus://tasks/"):
            task_id = uri.replace("focus://tasks/", "")
            return await call_focus_api(f"/tasks/{task_id}", token)

        elif uri.startswith("focus://projects/"):
            project_id = uri.replace("focus://projects/", "")
            return await call_focus_api(f"/projects/{project_id}", token)

        elif uri.startswith("focus://goals/"):
            goal_id = uri.replace("focus://goals/", "")
            return await call_focus_api(f"/goals/{goal_id}", token)

        elif uri == "focus://brain/context":
            # Get comprehensive context for AI
            daily_plan = await call_focus_api("/brain/daily-plan", token)
            summary = await call_focus_api("/brain/summary", token)
            return {
                "daily_plan": daily_plan,
                "summary": summary,
                "timestamp": "now"
            }

        elif uri == "focus://brain/priorities":
            plan = await call_focus_api("/brain/daily-plan", token)
            return {
                "priorities": plan.get("top_tasks", []),
                "overdue_count": plan.get("overdue_count", 0),
                "due_today_count": plan.get("due_today_count", 0)
            }

        elif uri.startswith("focus://knowledge/"):
            item_id = uri.replace("focus://knowledge/", "")
            return await call_focus_api(f"/knowledge/items/{item_id}", token)

        elif uri == "focus://summary":
            return await call_focus_api("/brain/summary", token)

        else:
            return None

    except Exception as e:
        return {"error": str(e)}


def list_resources() -> list:
    """List available resource templates."""
    return [
        {
            "uri": r.uri,
            "name": r.name,
            "description": r.description,
            "mimeType": r.mimeType
        }
        for r in RESOURCE_TEMPLATES.values()
    ]
