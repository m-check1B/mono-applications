import os
import re
from pathlib import Path
from typing import Any, Optional, Set
from urllib.parse import urlparse

from ii_agent.tools.base import (
    ToolImplOutput,
    LLMTool,
)
from ii_agent.llm.message_history import MessageHistory
from ii_agent.utils.sandbox_manager import SandboxManager
from ii_agent.utils.workspace_manager import WorkspaceManager


class RegisterDeploymentTool(LLMTool):
    """Tool for registering deployments"""

    name = "register_deployment"
    description = "Register a deployment and get the public url as well as the port that you can deploy your service on."

    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: register a port, deploy a static file, or list HTML links.",
                "enum": ["register_port", "static_file", "list_html_links"],
            },
            "port": {
                "type": "string",
                "description": "Port that you can deploy your service on",
            },
            "file_path": {
                "type": "string",
                "description": "Path to a static file (relative to workspace) to generate a public URL.",
            },
            "path": {
                "type": "string",
                "description": "Path to an HTML file or a directory to scan for local HTML links.",
            },
        },
    }

    def __init__(
        self,
        sandbox_manager: SandboxManager,
        workspace_manager: WorkspaceManager | None = None,
    ):
        super().__init__()
        self.sandbox_manager = sandbox_manager
        self.workspace_manager = workspace_manager
        self._static_base_url: str | None = None

    def _ensure_static_base_url(self) -> str:
        if self._static_base_url:
            return self._static_base_url
        if not self.workspace_manager:
            raise ValueError("Workspace manager is not configured.")

        env_base_url = os.getenv("STATIC_FILE_BASE_URL")
        if env_base_url:
            base_url = env_base_url
        else:
            base_url = f"file://{self.workspace_manager.root.parent.parent.absolute()}"

        parsed = urlparse(base_url)
        valid_schemes = {"http", "https", "file"}
        if parsed.scheme not in valid_schemes:
            raise ValueError(
                f"Invalid STATIC_FILE_BASE_URL scheme: '{parsed.scheme}'. "
                f"Must be one of: {', '.join(valid_schemes)}. "
                f"Current value: {base_url}"
            )

        self._static_base_url = base_url
        return base_url

    def _static_deploy(self, file_path: str) -> ToolImplOutput:
        if not self.workspace_manager:
            return ToolImplOutput(
                "Workspace manager is not configured for static deployment.",
                "Workspace manager is not configured for static deployment.",
            )

        ws_path = self.workspace_manager.workspace_path(Path(file_path))
        if not ws_path.exists():
            return ToolImplOutput(
                f"Path does not exist: {file_path}",
                f"Path does not exist: {file_path}",
            )

        if not ws_path.is_file():
            return ToolImplOutput(
                f"Path is not a file: {file_path}",
                f"Path is not a file: {file_path}",
            )

        try:
            base_url = self._ensure_static_base_url()
        except ValueError as exc:
            return ToolImplOutput(str(exc), str(exc))

        connection_uuid = self.workspace_manager.root.name
        rel_path = ws_path.relative_to(self.workspace_manager.root)
        public_url = f"{base_url}/workspace/{connection_uuid}/{rel_path}"

        return ToolImplOutput(
            public_url,
            f"Static file available at: {public_url}",
        )

    def _extract_links_from_file(self, file_path: Path) -> Set[str]:
        links: Set[str] = set()
        if (
            not file_path.exists()
            or not file_path.is_file()
            or file_path.suffix.lower() != ".html"
        ):
            return links

        html_content = file_path.read_text(errors="ignore")
        for match in re.finditer(
            r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html_content, re.IGNORECASE
        ):
            href = match.group(1)
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue

            parsed_href = urlparse(href)
            if parsed_href.scheme or parsed_href.netloc:
                continue

            if href.endswith(".html") or "." not in Path(href).name:
                links.add(Path(href).name)
        return links

    def _list_html_links(self, relative_path_str: str) -> ToolImplOutput:
        if not self.workspace_manager:
            return ToolImplOutput(
                "Workspace manager is not configured for link scanning.",
                "Workspace manager is not configured for link scanning.",
                {"success": False},
            )

        ws_path = self.workspace_manager.workspace_path(Path(relative_path_str))
        all_found_links: Set[str] = set()

        if not ws_path.exists():
            return ToolImplOutput(
                f"Error: Path not found: {relative_path_str}",
                f"Path not found: {relative_path_str}",
                {"success": False},
            )

        if ws_path.is_file():
            if ws_path.suffix.lower() == ".html":
                all_found_links.update(self._extract_links_from_file(ws_path))
            else:
                return ToolImplOutput(
                    f"Error: Specified path '{relative_path_str}' is not an HTML file.",
                    "Path is not HTML",
                    {"success": False},
                )
        elif ws_path.is_dir():
            for item in ws_path.rglob("*.html"):
                if item.is_file():
                    all_found_links.update(self._extract_links_from_file(item))
        else:
            return ToolImplOutput(
                f"Error: Path is neither a file nor a directory: {relative_path_str}",
                "Invalid path type",
                {"success": False},
            )

        sorted_links = sorted(all_found_links)
        if not sorted_links:
            return ToolImplOutput(
                f"No local HTML links found in '{relative_path_str}'.",
                "No links found.",
                {"success": True, "linked_files": []},
            )

        output_message = (
            f"Found the following unique local HTML file names linked from '{relative_path_str}': "
            f"{sorted_links}. "
            "Please cross-reference this list with your planned files (e.g., in todo.md) and create any missing ones."
        )
        return ToolImplOutput(
            output_message,
            f"Link scan complete for {relative_path_str}.",
            {"success": True, "linked_files": sorted_links},
        )

    async def run_impl(
        self,
        tool_input: dict[str, Any],
        message_history: Optional[MessageHistory] = None,
    ) -> ToolImplOutput:
        action = tool_input.get("action")

        if action == "list_html_links" or (not action and "path" in tool_input):
            path = tool_input.get("path")
            if not path:
                return ToolImplOutput(
                    "Error: 'path' is required for list_html_links action.",
                    "Path is required for list_html_links action.",
                    {"success": False},
                )
            return self._list_html_links(path)

        if action == "static_file" or (not action and "file_path" in tool_input):
            file_path = tool_input.get("file_path")
            if not file_path:
                return ToolImplOutput(
                    "Error: 'file_path' is required for static_file action.",
                    "File path is required for static_file action.",
                )
            return self._static_deploy(file_path)

        if action == "register_port" or "port" in tool_input:
            port = tool_input.get("port")
            if not port:
                return ToolImplOutput(
                    "Error: 'port' is required to register a deployment.",
                    "Port is required to register a deployment.",
                )
            public_url = self.sandbox_manager.expose_port(int(port))
            return ToolImplOutput(
                "Registering successfully. Public url/base path to access the service: "
                f"{public_url}. Update all localhost or 127.0.0.1 to the public url in "
                "your code. If you are using Next Auth, update your NEXTAUTH_URL",
                "Registering successfully. Public url/base path to access the service: "
                f"{public_url}. Update all localhost or 127.0.0.1 to the public url in "
                "your code. If you are using Next Auth, update your NEXTAUTH_URL",
            )

        return ToolImplOutput(
            "Error: Provide an action of register_port, static_file, or list_html_links "
            "with the required parameters.",
            "No valid action provided for register_deployment.",
        )
