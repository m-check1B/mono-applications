"""
Focus MCP Server - Authentication

Token-based auth for Kraliki agents.
Each agent has scoped access based on role.
"""

from typing import Dict, List, Optional
from jose import jwt, JWTError
import os

# Agent permission scopes
AGENT_SCOPES = {
    "builder": ["read:tasks", "update:tasks", "create:tasks", "read:projects"],
    "caretaker": ["read:*"],
    "business": ["read:goals", "read:projects", "read:analytics"],
    "orchestrator": ["*"],  # Full access
    "focus_user": ["read:own", "write:own"],  # Regular Focus users
}

# JWT settings from environment
JWT_SECRET = os.getenv("JWT_SECRET", "focus-mcp-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_agent_scopes(agent_type: str) -> List[str]:
    """Get scopes for agent type."""
    return AGENT_SCOPES.get(agent_type, [])


def check_permission(scopes: List[str], required: str) -> bool:
    """Check if scopes include required permission."""
    if "*" in scopes:
        return True
    if required in scopes:
        return True
    # Check wildcard patterns (e.g., "read:*" matches "read:tasks")
    required_parts = required.split(":")
    for scope in scopes:
        scope_parts = scope.split(":")
        if len(scope_parts) == 2 and scope_parts[1] == "*":
            if scope_parts[0] == required_parts[0]:
                return True
    return False


class AuthContext:
    """Authentication context for MCP requests."""

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.payload = None
        self.scopes: List[str] = []
        self.user_id: Optional[str] = None
        self.agent_type: Optional[str] = None

        if token:
            self.payload = verify_token(token)
            if self.payload:
                self.user_id = self.payload.get("sub")
                self.agent_type = self.payload.get("agent_type", "focus_user")
                self.scopes = get_agent_scopes(self.agent_type)

    def can(self, permission: str) -> bool:
        """Check if context has permission."""
        return check_permission(self.scopes, permission)

    def require(self, permission: str) -> None:
        """Require permission or raise error."""
        if not self.can(permission):
            raise PermissionError(f"Missing permission: {permission}")
