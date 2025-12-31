"""
Focus by Kraliki Tools - II-Agent integration with Focus by Kraliki API

This module provides tools for II-Agent to interact with Focus by Kraliki's
knowledge base, tasks, and projects via HTTP API calls.

All tools use the agentToken for authentication, passed from the frontend
during agent initialization.
"""

import httpx
import logging
from typing import Any, Optional, Dict, Literal
from ii_agent.tools.base import LLMTool, ToolImplOutput
from ii_agent.llm.message_history import MessageHistory


logger = logging.getLogger(__name__)


ToolType = Literal[
    "create_task",
    "update_task",
    "create_project",
    "list_tasks",
    "list_projects",
    "create_knowledge_item",
    "update_knowledge_item",
    "list_knowledge_items",
    "update_settings",
    "check_infra_status",
    "get_service_logs",
    "restart_service",
]


class FocusToolBase(LLMTool):
    """Base class for Focus by Kraliki tools with shared HTTP client logic."""

    def __init__(self, focus_api_base_url: str, agent_token: Optional[str] = None):
        """
        Initialize Focus tool with API base URL and authentication token.

        Args:
            focus_api_base_url: Base URL for Focus by Kraliki API (e.g., http://127.0.0.1:3017)
            agent_token: JWT token for authentication (passed from frontend)
        """
        self.focus_api_base_url = focus_api_base_url.rstrip('/')
        self.agent_token = agent_token

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.agent_token:
            headers["Authorization"] = f"Bearer {self.agent_token}"
        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Focus by Kraliki API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g., /agent-tools/knowledge/create)
            json_data: JSON body for POST/PATCH requests
            params: Query parameters for GET requests

        Returns:
            Response JSON as dictionary

        Raises:
            Exception: If request fails
        """
        url = f"{self.focus_api_base_url}{endpoint}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=json_data)
                elif method.upper() == "PATCH":
                    response = await client.patch(url, headers=headers, json=json_data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except httpx.RequestError as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)


class CreateKnowledgeItemTool(FocusToolBase):
    """Create a new knowledge item in Focus by Kraliki."""

    name = "create_knowledge_item"
    description = """Create a new knowledge item (note, idea, plan, goal, task, custom type) in Focus by Kraliki.

Use this tool for any user-defined item type. The platform ships with defaults (Task, Idea, Plan, Note, Goal)
but users can add/edit types. Always supply the typeId you intend to use (e.g., the Task typeId for a task)."""

    input_schema = {
        "type": "object",
        "properties": {
            "typeId": {
                "type": "string",
                "description": "The type ID of the knowledge item (e.g., 'bookmark', 'note', 'insight')"
            },
            "title": {
                "type": "string",
                "description": "Title of the knowledge item"
            },
            "content": {
                "type": "string",
                "description": "The main content/body of the knowledge item"
            },
            "item_metadata": {
                "type": "object",
                "description": "Optional metadata as JSON object (e.g., url, tags, source)"
            }
        },
        "required": ["typeId", "title", "content"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        type_id = tool_input["typeId"]
        title = tool_input["title"]
        content = tool_input["content"]
        item_metadata = tool_input.get("item_metadata", None)

        try:
            # Call Focus by Kraliki API endpoint
            data = {
                "typeId": type_id,
                "title": title,
                "content": content,
                "item_metadata": item_metadata
            }

            result = await self._make_request("POST", "/agent-tools/knowledge/create", json_data=data)

            item_id = result.get("id", "unknown")
            output_msg = f"Successfully created knowledge item '{title}' (ID: {item_id})"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Created knowledge item: {title}",
                auxiliary_data={"success": True, "item": result}
            )

        except Exception as e:
            error_msg = f"Failed to create knowledge item: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to create knowledge item",
                auxiliary_data={"success": False, "error": str(e)}
            )


class UpdateKnowledgeItemTool(FocusToolBase):
    """Update an existing knowledge item in Focus by Kraliki."""

    name = "update_knowledge_item"
    description = """Update an existing knowledge item by ID.

Use this tool to modify the title, content, completed status, or metadata of an existing
knowledge item. Only provide the fields you want to update."""

    input_schema = {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "The ID of the knowledge item to update"
            },
            "title": {
                "type": "string",
                "description": "New title (optional)"
            },
            "content": {
                "type": "string",
                "description": "New content (optional)"
            },
            "completed": {
                "type": "boolean",
                "description": "Mark as completed or not (optional)"
            },
            "item_metadata": {
                "type": "object",
                "description": "Updated metadata (optional)"
            }
        },
        "required": ["item_id"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        item_id = tool_input["item_id"]

        # Build update payload with only provided fields
        update_data = {}
        if "title" in tool_input:
            update_data["title"] = tool_input["title"]
        if "content" in tool_input:
            update_data["content"] = tool_input["content"]
        if "completed" in tool_input:
            update_data["completed"] = tool_input["completed"]
        if "item_metadata" in tool_input:
            update_data["item_metadata"] = tool_input["item_metadata"]

        try:
            result = await self._make_request(
                "PATCH",
                f"/agent-tools/knowledge/{item_id}",
                json_data=update_data
            )

            output_msg = f"Successfully updated knowledge item (ID: {item_id})"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Updated knowledge item: {item_id}",
                auxiliary_data={"success": True, "item": result}
            )

        except Exception as e:
            error_msg = f"Failed to update knowledge item: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to update knowledge item",
                auxiliary_data={"success": False, "error": str(e)}
            )


class ListKnowledgeItemsTool(FocusToolBase):
    """List knowledge items from Focus by Kraliki."""

    name = "list_knowledge_items"
    description = """List knowledge items with optional filtering.

Use this for any item type (Task, Idea, Plan, Note, Goal, or custom). Pass typeId when you want a
specific type, because users can rename/add types and "task" is just one predefined type."""

    input_schema = {
        "type": "object",
        "properties": {
            "typeId": {
                "type": "string",
                "description": "Filter by type ID (optional)"
            },
            "completed": {
                "type": "boolean",
                "description": "Filter by completed status (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of items to return (default: 50, max: 100)"
            }
        }
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        # Build query parameters
        params = {}
        if "typeId" in tool_input:
            params["typeId"] = tool_input["typeId"]
        if "completed" in tool_input:
            params["completed"] = tool_input["completed"]
        if "limit" in tool_input:
            params["limit"] = min(tool_input["limit"], 100)
        else:
            params["limit"] = 50

        try:
            result = await self._make_request("GET", "/agent-tools/knowledge", params=params)

            items = result.get("items", [])
            total = result.get("total", 0)

            # Format output for LLM
            if not items:
                output_msg = "No knowledge items found."
            else:
                output_lines = [f"Found {len(items)} knowledge items (total: {total}):\n"]
                for item in items:
                    item_id = item.get("id", "?")
                    title = item.get("title", "Untitled")
                    completed = item.get("completed", False)
                    status = "✓" if completed else "○"
                    output_lines.append(f"{status} {title} (ID: {item_id})")

                output_msg = "\n".join(output_lines)

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Listed {len(items)} knowledge items",
                auxiliary_data={"success": True, "items": items, "total": total}
            )

        except Exception as e:
            error_msg = f"Failed to list knowledge items: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to list knowledge items",
                auxiliary_data={"success": False, "error": str(e)}
            )


class CreateTaskTool(FocusToolBase):
    """Create a new task in Focus by Kraliki (unified with knowledge items)."""

    name = "create_task"
    description = """Create a new task in Focus by Kraliki.

Tasks are unified with knowledge items - they are stored as knowledge_item with typeId='Tasks'.
Task-specific fields (priority, dueDate, etc) are preserved in metadata for backward compatibility.

Use this when the intent is explicitly a task/to-do. For other types (idea/plan/note/goal/custom),
use create_knowledge_item with the correct typeId."""

    input_schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title"
            },
            "description": {
                "type": "string",
                "description": "Detailed task description (optional)"
            },
            "projectId": {
                "type": "string",
                "description": "Project ID to assign task to (optional)"
            },
            "priority": {
                "type": "integer",
                "description": "Priority level: 1 (low), 2 (medium), 3 (high). Default: 2"
            },
            "estimatedMinutes": {
                "type": "integer",
                "description": "Estimated time in minutes (optional)"
            },
            "dueDate": {
                "type": "string",
                "description": "Due date in ISO format (optional)"
            }
        },
        "required": ["title"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        title = tool_input["title"]

        # Build task data
        task_data = {"title": title}

        if "description" in tool_input:
            task_data["description"] = tool_input["description"]
        if "projectId" in tool_input:
            task_data["projectId"] = tool_input["projectId"]
        if "priority" in tool_input:
            task_data["priority"] = tool_input["priority"]
        else:
            task_data["priority"] = 2  # Default to medium
        if "estimatedMinutes" in tool_input:
            task_data["estimatedMinutes"] = tool_input["estimatedMinutes"]
        if "dueDate" in tool_input:
            task_data["dueDate"] = tool_input["dueDate"]

        try:
            result = await self._make_request("POST", "/agent-tools/tasks", json_data=task_data)

            task_id = result.get("id", "unknown")
            output_msg = f"Successfully created task '{title}' (ID: {task_id})"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Created task: {title}",
                auxiliary_data={"success": True, "task": result}
            )

        except Exception as e:
            error_msg = f"Failed to create task: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to create task",
                auxiliary_data={"success": False, "error": str(e)}
            )


class UpdateTaskTool(FocusToolBase):
    """Update an existing task in Focus by Kraliki (unified with knowledge items)."""

    name = "update_task"
    description = """Update an existing task by ID.

Tasks are unified with knowledge items backend. This tool updates the knowledge_item
and its metadata fields. Status changes automatically update completion tracking.

Only provide the fields you want to update."""

    input_schema = {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to update"
            },
            "title": {
                "type": "string",
                "description": "New task title (optional)"
            },
            "description": {
                "type": "string",
                "description": "New description (optional)"
            },
            "status": {
                "type": "string",
                "description": "New status: PENDING, IN_PROGRESS, COMPLETED (optional)",
                "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"]
            },
            "priority": {
                "type": "integer",
                "description": "New priority: 1 (low), 2 (medium), 3 (high) (optional)"
            },
            "estimatedMinutes": {
                "type": "integer",
                "description": "New estimated time in minutes (optional)"
            },
            "dueDate": {
                "type": "string",
                "description": "New due date in ISO format (optional)"
            }
        },
        "required": ["task_id"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        task_id = tool_input["task_id"]

        # Build update payload with only provided fields
        update_data = {}
        if "title" in tool_input:
            update_data["title"] = tool_input["title"]
        if "description" in tool_input:
            update_data["description"] = tool_input["description"]
        if "status" in tool_input:
            update_data["status"] = tool_input["status"]
        if "priority" in tool_input:
            update_data["priority"] = tool_input["priority"]
        if "estimatedMinutes" in tool_input:
            update_data["estimatedMinutes"] = tool_input["estimatedMinutes"]
        if "dueDate" in tool_input:
            update_data["dueDate"] = tool_input["dueDate"]

        try:
            result = await self._make_request(
                "PATCH",
                f"/agent-tools/tasks/{task_id}",
                json_data=update_data
            )

            output_msg = f"Successfully updated task (ID: {task_id})"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Updated task: {task_id}",
                auxiliary_data={"success": True, "task": result}
            )

        except Exception as e:
            error_msg = f"Failed to update task: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to update task",
                auxiliary_data={"success": False, "error": str(e)}
            )


class ListTasksTool(FocusToolBase):
    """List tasks from Focus by Kraliki (unified with knowledge items)."""

    name = "list_tasks"
    description = """List tasks with optional filtering.

Tasks are unified with knowledge items (typeId='Tasks'). This retrieves items from
the unified knowledge_item table, filtered by task-specific metadata.

Useful for reviewing pending work, tracking progress, or filtering by status/project."""

    input_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by status: PENDING, IN_PROGRESS, COMPLETED (optional)",
                "enum": ["PENDING", "IN_PROGRESS", "COMPLETED"]
            },
            "projectId": {
                "type": "string",
                "description": "Filter by project ID (optional)"
            },
            "priority": {
                "type": "integer",
                "description": "Filter by priority: 1 (low), 2 (medium), 3 (high) (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tasks to return (default: 50, max: 100)"
            }
        }
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        # Build query parameters
        params = {}
        if "status" in tool_input:
            params["status"] = tool_input["status"]
        if "projectId" in tool_input:
            params["projectId"] = tool_input["projectId"]
        if "priority" in tool_input:
            params["priority"] = tool_input["priority"]
        if "limit" in tool_input:
            params["limit"] = min(tool_input["limit"], 100)
        else:
            params["limit"] = 50

        try:
            result = await self._make_request("GET", "/agent-tools/tasks", params=params)

            tasks = result.get("tasks", [])
            total = result.get("total", 0)

            # Format output for LLM
            if not tasks:
                output_msg = "No tasks found."
            else:
                output_lines = [f"Found {len(tasks)} tasks (total: {total}):\n"]
                for task in tasks:
                    task_id = task.get("id", "?")
                    title = task.get("title", "Untitled")
                    status = task.get("status", "PENDING")
                    priority = task.get("priority", 2)

                    # Status emoji
                    status_emoji = {
                        "PENDING": "○",
                        "IN_PROGRESS": "◐",
                        "COMPLETED": "●"
                    }.get(status, "?")

                    # Priority indicator
                    priority_str = ["!", "!!", "!!!"][priority - 1] if 1 <= priority <= 3 else ""

                    output_lines.append(
                        f"{status_emoji} {title} {priority_str} [{status}] (ID: {task_id})"
                    )

                output_msg = "\n".join(output_lines)

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Listed {len(tasks)} tasks",
                auxiliary_data={"success": True, "tasks": tasks, "total": total}
            )

        except Exception as e:
            error_msg = f"Failed to list tasks: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to list tasks",
                auxiliary_data={"success": False, "error": str(e)}
            )


class CreateOrGetProjectTool(FocusToolBase):
    """Create a new project or get an existing one by name."""

    name = "create_or_get_project"
    description = """Create a new project or get an existing project by name.

Use this tool to ensure a project exists before assigning tasks to it. If a project
with the given name already exists, it will be returned. Otherwise, a new project
will be created."""

    input_schema = {
        "type": "object",
        "properties": {
            "projectName": {
                "type": "string",
                "description": "Name of the project"
            },
            "description": {
                "type": "string",
                "description": "Project description (optional, only used when creating new project)"
            },
            "color": {
                "type": "string",
                "description": "Project color in hex format (e.g., #3B82F6) (optional)"
            }
        },
        "required": ["projectName"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        project_name = tool_input["projectName"]
        description = tool_input.get("description", None)
        color = tool_input.get("color", None)

        try:
            # Use the create-or-get endpoint
            project_data = {
                "name": project_name,
                "description": description,
                "color": color
            }

            result = await self._make_request("POST", "/agent-tools/projects/create-or-get", json_data=project_data)

            project_id = result.get("id", "unknown")
            output_msg = f"Created project '{project_name}' (ID: {project_id})"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Created/retrieved project: {project_name}",
                auxiliary_data={"success": True, "project": result}
            )

        except Exception as e:
            # The create-or-get endpoint should handle both create and existing cases
            # If it fails, return the error
            error_msg = f"Failed to create or get project: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to create or get project",
                auxiliary_data={"success": False, "error": str(e)}
            )


class FocusFileSearchTool(FocusToolBase):
    """Search user's knowledge base using semantic search powered by Gemini."""

    name = "focus_file_search_query"
    description = """Search the user's knowledge base using natural language semantic search.

Use this tool when you need to:
- Recall information from past notes, tasks, or transcripts
- Find relevant context for complex workflows or decisions
- Answer questions about the user's historical data
- Retrieve specific details from knowledge items
- Understand what the user has discussed or documented previously

This tool returns AI-generated answers grounded in the user's actual content,
with citations to source documents.

Examples:
- "What did I discuss in meetings last week?"
- "Find my notes about the project architecture"
- "What tasks did I create related to the API redesign?"
- "What are my current priorities?"
- "What decisions did I make about the database migration?"""

    input_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language search query (e.g., 'What are my priorities this week?')"
            },
            "context": {
                "type": "object",
                "description": "Optional context to narrow search (e.g., {'project_id': 'abc123'})"
            }
        },
        "required": ["query"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        query = tool_input["query"]
        context = tool_input.get("context", None)

        try:
            # Call Focus by Kraliki file search API endpoint
            request_data = {"query": query}
            if context:
                request_data["context"] = context

            result = await self._make_request(
                "POST",
                "/ai/file-search/query",
                json_data=request_data
            )

            # Parse response
            answer = result.get("answer", "No answer found.")
            citations = result.get("citations", [])

            # Format response for agent
            output_lines = [f"**Answer:** {answer}"]

            if citations:
                output_lines.append("\n**Sources:**")
                for i, citation in enumerate(citations, 1):
                    doc_name = citation.get("documentName", "Unknown")
                    item_id = citation.get("knowledgeItemId")
                    excerpt = citation.get("excerpt", "")

                    citation_line = f"{i}. {doc_name}"
                    if item_id:
                        citation_line += f" (ID: {item_id})"
                    output_lines.append(citation_line)

                    if excerpt:
                        # Truncate long excerpts
                        max_excerpt_len = 150
                        if len(excerpt) > max_excerpt_len:
                            excerpt = excerpt[:max_excerpt_len] + "..."
                        output_lines.append(f"   Excerpt: {excerpt}")

            output_msg = "\n".join(output_lines)

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Searched knowledge base for: {query}",
                auxiliary_data={
                    "success": True,
                    "query": query,
                    "answer": answer,
                    "citations": citations
                }
            )

        except Exception as e:
            error_msg = f"Failed to search knowledge base: {str(e)}"
            logger.error(f"File search failed for query '{query}': {e}")
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to search knowledge base",
                auxiliary_data={"success": False, "error": str(e), "query": query}
            )


class ExportInvoiceTool(FocusToolBase):
    """Generate invoice from billable hours."""

    name = "export_invoice"
    description = """Generate an invoice for billable hours.

Use this tool to create invoices for freelancers based on tracked time.
Supports CSV and JSON formats with project breakdowns."""

    input_schema = {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format"
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format"
            },
            "client_name": {
                "type": "string",
                "description": "Client name for invoice (optional)"
            },
            "invoice_number": {
                "type": "string",
                "description": "Invoice number (optional)"
            },
            "hourly_rate": {
                "type": "number",
                "description": "Hourly rate in USD (optional, overrides entry rates)"
            },
            "format": {
                "type": "string",
                "description": "Export format: 'csv' or 'json'",
                "enum": ["csv", "json"]
            }
        },
        "required": ["start_date", "end_date"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            result = await self._make_request(
                "POST",
                "/exports/invoices/generate",
                json_data=tool_input
            )

            if tool_input.get("format") == "json":
                summary = result.get("summary", {})
                output_msg = (
                    f"Generated invoice:\n"
                    f"- Total Hours: {summary.get('total_hours', 0)}\n"
                    f"- Billable Hours: {summary.get('billable_hours', 0)}\n"
                    f"- Total Amount: ${summary.get('total_amount', 0):.2f}\n"
                    f"- Projects: {len(result.get('projects', []))}"
                )
            else:
                output_msg = "Invoice CSV generated successfully"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message="Invoice generated",
                auxiliary_data={"success": True, "invoice": result}
            )

        except Exception as e:
            error_msg = f"Failed to generate invoice: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Invoice generation failed",
                auxiliary_data={"success": False, "error": str(e)}
            )


class GetBillableSummaryTool(FocusToolBase):
    """Get billable hours summary."""

    name = "get_billable_summary"
    description = """Get a summary of billable hours for a date range.

Use this to quickly check billable hours, revenue, and project breakdowns
for freelancers. Useful for weekly/monthly reviews."""

    input_schema = {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date (YYYY-MM-DD)"
            },
            "end_date": {
                "type": "string",
                "description": "End date (YYYY-MM-DD)"
            },
            "project_id": {
                "type": "string",
                "description": "Optional project ID to filter by"
            }
        },
        "required": ["start_date", "end_date"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            params = {
                "start_date": tool_input["start_date"],
                "end_date": tool_input["end_date"]
            }
            if "project_id" in tool_input:
                params["project_id"] = tool_input["project_id"]

            result = await self._make_request("GET", "/exports/billable/summary", params=params)

            output_lines = [
                f"Billable Hours Summary ({params['start_date']} to {params['end_date']}):",
                f"- Total Hours: {result['total_hours']}",
                f"- Billable Hours: {result['billable_hours']}",
                f"- Non-Billable Hours: {result['non_billable_hours']}",
                f"- Total Revenue: ${result['total_amount']:.2f}",
                f"\nProject Breakdown:"
            ]

            for project in result.get("projects", []):
                output_lines.append(
                    f"  • {project['project_name']}: "
                    f"{project['billable_hours']}h (${project['total_amount']:.2f})"
                )

            return ToolImplOutput(
                output="\n".join(output_lines),
                tool_result_message="Retrieved billable summary",
                auxiliary_data={"success": True, "summary": result}
            )

        except Exception as e:
            error_msg = f"Failed to get billable summary: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to retrieve summary",
                auxiliary_data={"success": False, "error": str(e)}
            )


class CalendarSyncStatusTool(FocusToolBase):
    """Check Google Calendar sync status."""

    name = "calendar_sync_status"
    description = """Check the status of Google Calendar integration.

Shows whether calendar sync is enabled, connected, and when it last ran.
Useful before syncing tasks to calendar."""

    input_schema = {
        "type": "object",
        "properties": {}
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            result = await self._make_request("GET", "/calendar-sync/status")

            output_lines = [
                "Google Calendar Sync Status:",
                f"- Enabled: {'Yes' if result['enabled'] else 'No'}",
                f"- Connected: {'Yes' if result['connected'] else 'No'}",
                f"- Sync Direction: {result['sync_direction']}",
                f"- Last Sync: {result.get('last_sync', 'Never')}"
            ]

            if result.get('calendars'):
                output_lines.append("\nAvailable Calendars:")
                for cal in result['calendars']:
                    output_lines.append(f"  • {cal['name']} (ID: {cal['id']})")

            return ToolImplOutput(
                output="\n".join(output_lines),
                tool_result_message="Calendar sync status retrieved",
                auxiliary_data={"success": True, "status": result}
            )

        except Exception as e:
            error_msg = f"Failed to get calendar sync status: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Failed to retrieve status",
                auxiliary_data={"success": False, "error": str(e)}
            )


class TriggerCalendarSyncTool(FocusToolBase):
    """Manually trigger calendar sync."""

    name = "trigger_calendar_sync"
    description = """Manually trigger a Google Calendar sync.

Use this to sync Focus tasks to calendar or pull calendar events to Focus.
Supports one-way and two-way sync."""

    input_schema = {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "description": "Sync direction: 'to_calendar', 'from_calendar', or 'both'",
                "enum": ["to_calendar", "from_calendar", "both"]
            },
            "start_date": {
                "type": "string",
                "description": "Optional start date (YYYY-MM-DD)"
            },
            "end_date": {
                "type": "string",
                "description": "Optional end date (YYYY-MM-DD)"
            }
        }
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            sync_data = {
                "direction": tool_input.get("direction", "both")
            }
            if "start_date" in tool_input:
                sync_data["start_date"] = tool_input["start_date"]
            if "end_date" in tool_input:
                sync_data["end_date"] = tool_input["end_date"]

            result = await self._make_request("POST", "/calendar-sync/sync", json_data=sync_data)

            output_msg = (
                f"Calendar sync triggered successfully!\n"
                f"Direction: {result['direction']}\n"
                f"Date Range: {result['date_range']['start']} to {result['date_range']['end']}\n"
                f"Sync is running in the background."
            )

            return ToolImplOutput(
                output=output_msg,
                tool_result_message="Calendar sync started",
                auxiliary_data={"success": True, "sync": result}
            )

        except Exception as e:
            error_msg = f"Failed to trigger calendar sync: {str(e)}"
            return ToolImplOutput(
                output=error_msg,
                tool_result_message="Calendar sync failed",
                auxiliary_data={"success": False, "error": str(e)}
            )


class UpdateSettingsTool(FocusToolBase):
    """Update user settings and preferences."""

    name = "update_settings"
    description = """Update user settings and preferences.

Use this tool to change user preferences such as theme (light/dark), notification settings,
or other profile options. Only provide fields to update."""

    input_schema = {
        "type": "object",
        "properties": {
            "theme": {
                "type": "string",
                "description": "UI theme preference",
                "enum": ["light", "dark", "system"]
            },
            "notifications": {
                "type": "boolean",
                "description": "Enable/disable notifications"
            },
            "language": {
                "type": "string",
                "description": "Preferred language code (e.g., 'en', 'cs')"
            }
        }
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            result = await self._make_request("POST", "/agent-tools/settings/update", json_data=tool_input)

            output_msg = "Settings updated successfully."
            return ToolImplOutput(
                output=output_msg,
                tool_result_message="Updated user settings",
                auxiliary_data={"success": True, "preferences": result.get("preferences")}
            )
        except Exception as e:
            return ToolImplOutput(
                output=f"Failed to update settings: {str(e)}",
                tool_result_message="Failed to update settings",
                auxiliary_data={"success": False, "error": str(e)}
            )


class CheckInfraStatusTool(FocusToolBase):
    """Check system infrastructure status."""

    name = "check_infra_status"
    description = """Check the health status of system infrastructure.

Use this tool to verify if the backend, database, and other services are running correctly."""

    input_schema = {"type": "object", "properties": {}}
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        try:
            result = await self._make_request("GET", "/agent-tools/infra/status")

            services = result.get("services", {})
            output_lines = [
                f"System Status: {result.get('system', 'unknown')}",
                f"Uptime: {result.get('uptime_seconds', 0)}s",
                "Services:"
            ]
            for svc, health in services.items():
                output_lines.append(f"- {svc}: {health}")

            return ToolImplOutput(
                output="\n".join(output_lines),
                tool_result_message="Checked infra status",
                auxiliary_data={"success": True, "status": result}
            )
        except Exception as e:
            return ToolImplOutput(
                output=f"Failed to check status: {str(e)}",
                tool_result_message="Failed to check status",
                auxiliary_data={"success": False, "error": str(e)}
            )


class GetLogsTool(FocusToolBase):
    """Get logs for a service."""

    name = "get_service_logs"
    description = """Get recent logs for a system service.

Use this tool to debug issues by reading the latest logs from 'backend' or 'frontend'."""

    input_schema = {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "Service name",
                "enum": ["backend", "frontend"]
            },
            "lines": {
                "type": "integer",
                "description": "Number of lines to retrieve (default: 50)"
            }
        },
        "required": ["service"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        service = tool_input["service"]
        lines = tool_input.get("lines", 50)

        try:
            result = await self._make_request("GET", "/agent-tools/infra/logs", params={"service": service, "lines": lines})

            content = result.get("content", "")
            output_msg = f"Logs for {service} (last {result.get('lines')} lines):\n\n{content}"

            return ToolImplOutput(
                output=output_msg,
                tool_result_message=f"Retrieved {service} logs",
                auxiliary_data={"success": True, "logs": result}
            )
        except Exception as e:
             return ToolImplOutput(
                output=f"Failed to get logs: {str(e)}",
                tool_result_message="Failed to get logs",
                auxiliary_data={"success": False, "error": str(e)}
            )


class RestartServiceTool(FocusToolBase):
    """Restart a system service via Focus by Kraliki infra router."""

    name = "restart_service"
    description = """Restart a Focus by Kraliki service (backend or frontend).\n\nUse sparingly; only allowed services are 'backend' and 'frontend'."""

    input_schema = {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "Service to restart",
                "enum": ["backend", "frontend"]
            }
        },
        "required": ["service"]
    }
    output_type = "string"

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        service = tool_input["service"]
        try:
            result = await self._make_request("POST", "/agent-tools/infra/restart", params={"service": service})
            return ToolImplOutput(
                output=f"Restarted {service}: {result.get('status')}",
                tool_result_message=f"Restarted {service}",
                auxiliary_data={"success": True, "service": service}
            )
        except Exception as e:
            return ToolImplOutput(
                output=f"Failed to restart {service}: {str(e)}",
                tool_result_message="Failed to restart service",
                auxiliary_data={"success": False, "error": str(e)}
            )


class ListEventsTool(FocusToolBase):
    """List calendar events."""

    name = "list_events"
    description = "List upcoming calendar events within an optional date range."
    input_schema = {
        "type": "object",
        "properties": {
            "startDate": {"type": "string", "description": "ISO start date"},
            "endDate": {"type": "string", "description": "ISO end date"},
            "limit": {"type": "integer", "description": "Max results (default 50)"}
        }
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        params = {}
        if tool_input.get("startDate"):
            params["startDate"] = tool_input["startDate"]
        if tool_input.get("endDate"):
            params["endDate"] = tool_input["endDate"]
        if tool_input.get("limit"):
            params["limit"] = tool_input["limit"]

        data = await self._make_request("GET", "/agent-tools/events", params=params)
        events = data.get("events", [])
        formatted = "\n".join([f"- {e.get('title','(no title)')} @ {e.get('start_time')}" for e in events]) or "No events."
        return ToolImplOutput(content=formatted, stop_session=False)


class CreateEventTool(FocusToolBase):
    """Create a calendar event."""

    name = "create_event"
    description = "Create a new calendar event with title, start/end time."
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "start_time": {"type": "string", "description": "ISO date-time"},
            "end_time": {"type": "string", "description": "ISO date-time"},
            "location": {"type": "string"}
        },
        "required": ["title", "start_time", "end_time"]
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        payload = {k: v for k, v in tool_input.items() if v is not None}
        event = await self._make_request("POST", "/agent-tools/events", json_data=payload)
        return ToolImplOutput(content=f"Event created: {event.get('title')} ({event.get('id')})", stop_session=False)


class ListTimeEntriesTool(FocusToolBase):
    """List recent time entries."""

    name = "list_time_entries"
    description = "List recent time entries for the user."
    input_schema = {"type": "object", "properties": {"limit": {"type": "integer"}}}
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        params = {}
        if tool_input.get("limit"):
            params["limit"] = tool_input["limit"]
        data = await self._make_request("GET", "/agent-tools/time", params=params)
        entries = data.get("entries", [])
        formatted = "\n".join([f"- {e.get('description','(no desc)')} ({e.get('duration_seconds','?')}s)" for e in entries]) or "No entries."
        return ToolImplOutput(content=formatted, stop_session=False)


class StartTimerTool(FocusToolBase):
    """Start a new timer."""

    name = "start_timer"
    description = "Start a timer/time entry with a description and optional project/task."
    input_schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "task_id": {"type": "string"},
            "project_id": {"type": "string"},
            "billable": {"type": "string", "enum": ["true", "false"]}
        },
        "required": ["description"]
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        payload = {k: v for k, v in tool_input.items() if v is not None}
        if "start_time" not in payload:
            import datetime
            payload["start_time"] = datetime.datetime.utcnow().isoformat() + "Z"
        entry = await self._make_request("POST", "/agent-tools/time/start", json_data=payload)
        return ToolImplOutput(content=f"Timer started: {entry.get('id')}", stop_session=False)


class StopTimerTool(FocusToolBase):
    """Stop an existing timer."""

    name = "stop_timer"
    description = "Stop a running timer/time entry by ID."
    input_schema = {
        "type": "object",
        "properties": {
            "entry_id": {"type": "string", "description": "Time entry ID to stop"},
            "description": {"type": "string", "description": "Optional summary"}
        },
        "required": ["entry_id"]
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        entry_id = tool_input["entry_id"]
        payload = {}
        if tool_input.get("description"):
            payload["description"] = tool_input["description"]
        entry = await self._make_request("POST", f"/agent-tools/time/{entry_id}/stop", json_data=payload)
        return ToolImplOutput(content=f"Timer stopped: {entry.get('id')} ({entry.get('duration_seconds','?')}s)", stop_session=False)


class ListWorkflowTemplatesTool(FocusToolBase):
    """List available workflow templates."""

    name = "list_workflow_templates"
    description = "List workflow templates (user/system/public)."
    input_schema = {"type": "object", "properties": {"include_public": {"type": "boolean"}}}
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        params = {"include_public": tool_input.get("include_public", True)}
        data = await self._make_request("GET", "/agent-tools/workflow/templates", params=params)
        templates = data.get("templates", [])
        formatted = "\n".join([f"- {t.get('name')} ({t.get('id')})" for t in templates]) or "No templates found."
        return ToolImplOutput(content=formatted, stop_session=False)


class ExecuteWorkflowTemplateTool(FocusToolBase):
    """Execute a workflow template."""

    name = "execute_workflow_template"
    description = "Execute a workflow template to create tasks."
    input_schema = {
        "type": "object",
        "properties": {
            "templateId": {"type": "string"},
            "customTitle": {"type": "string"},
            "priority": {"type": "integer"},
            "startDate": {"type": "string"},
            "additionalTags": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["templateId"]
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        payload = {k: v for k, v in tool_input.items() if v is not None}
        res = await self._make_request("POST", "/agent-tools/workflow/execute", json_data=payload)
        return ToolImplOutput(content=res.get("message", "Workflow executed"), stop_session=False)


class AnalyticsOverviewTool(FocusToolBase):
    """Get productivity analytics overview."""

    name = "analytics_overview"
    description = "Fetch workspace analytics (task metrics, focus metrics, bottlenecks)."
    input_schema = {
        "type": "object",
        "properties": {"workspaceId": {"type": "string"}}
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        params = {}
        if tool_input.get("workspaceId"):
            params["workspaceId"] = tool_input["workspaceId"]
        data = await self._make_request("GET", "/agent-tools/analytics/overview", params=params)
        workspace = data.get("workspace", {})
        metrics = data.get("taskMetrics", {})
        summary = f"Workspace {workspace.get('name')} - tasks: {metrics.get('total',0)} total, {metrics.get('completed',0)} completed, overdue: {metrics.get('overdue',0)}"
        return ToolImplOutput(content=summary, stop_session=False)


class ListWorkspacesTool(FocusToolBase):
    """List available workspaces."""

    name = "list_workspaces"
    description = "List workspaces and active workspace."
    input_schema = {"type": "object", "properties": {}}
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        data = await self._make_request("GET", "/agent-tools/workspaces")
        wkspaces = data.get("workspaces", [])
        active = data.get("activeWorkspaceId")
        formatted = "\n".join([f"- {w.get('name')} ({w.get('id')}){' [active]' if w.get('id')==active else ''}" for w in wkspaces]) or "No workspaces."
        return ToolImplOutput(content=formatted, stop_session=False)


class SwitchWorkspaceTool(FocusToolBase):
    """Switch active workspace."""

    name = "switch_workspace"
    description = "Switch the user's active workspace by ID."
    input_schema = {
        "type": "object",
        "properties": {"workspaceId": {"type": "string"}},
        "required": ["workspaceId"]
    }
    output_type = "string"

    async def run_impl(self, tool_input: dict[str, Any], message_history: Optional[MessageHistory] = None) -> ToolImplOutput:
        workspace_id = tool_input["workspaceId"]
        res = await self._make_request("POST", "/agent-tools/workspaces/switch", json_data={"workspaceId": workspace_id})
        return ToolImplOutput(content=f"Switched to workspace {res.get('activeWorkspaceId')}", stop_session=False)


# Tool factory function
def create_focus_tools(
    focus_api_base_url: str = "http://127.0.0.1:3017",
    agent_token: Optional[str] = None
) -> list[LLMTool]:
    """
    Create all Focus by Kraliki tools with shared configuration.

    Args:
        focus_api_base_url: Base URL for Focus by Kraliki API
        agent_token: JWT authentication token

    Returns:
        List of Focus tool instances
    """
    return [
        # Core tools
        CreateKnowledgeItemTool(focus_api_base_url, agent_token),
        UpdateKnowledgeItemTool(focus_api_base_url, agent_token),
        ListKnowledgeItemsTool(focus_api_base_url, agent_token),
        CreateTaskTool(focus_api_base_url, agent_token),
        UpdateTaskTool(focus_api_base_url, agent_token),
        ListTasksTool(focus_api_base_url, agent_token),
        CreateOrGetProjectTool(focus_api_base_url, agent_token),
        FocusFileSearchTool(focus_api_base_url, agent_token),
        ListEventsTool(focus_api_base_url, agent_token),
        CreateEventTool(focus_api_base_url, agent_token),
        ListTimeEntriesTool(focus_api_base_url, agent_token),
        StartTimerTool(focus_api_base_url, agent_token),
        StopTimerTool(focus_api_base_url, agent_token),
        ListWorkflowTemplatesTool(focus_api_base_url, agent_token),
        ExecuteWorkflowTemplateTool(focus_api_base_url, agent_token),
        AnalyticsOverviewTool(focus_api_base_url, agent_token),
        ListWorkspacesTool(focus_api_base_url, agent_token),
        SwitchWorkspaceTool(focus_api_base_url, agent_token),

        # Integration tools (Track 6)
        ExportInvoiceTool(focus_api_base_url, agent_token),
        GetBillableSummaryTool(focus_api_base_url, agent_token),
        CalendarSyncStatusTool(focus_api_base_url, agent_token),
        TriggerCalendarSyncTool(focus_api_base_url, agent_token),

        # System tools (AI-First Architecture)
        UpdateSettingsTool(focus_api_base_url, agent_token),
        CheckInfraStatusTool(focus_api_base_url, agent_token),
        GetLogsTool(focus_api_base_url, agent_token),
        RestartServiceTool(focus_api_base_url, agent_token),
    ]
