#!/usr/bin/env python3
"""Per-genome permission system.

From OpenCode research - three-tier permissions (allow/ask/deny).
"""

from enum import Enum
from typing import Dict, Optional
import json
import os

class Permission(Enum):
    ALLOW = "allow"   # Execute without approval
    ASK = "ask"       # Would need approval (logged for now)
    DENY = "deny"     # Block completely


# Default permissions for all genomes
DEFAULT_PERMISSIONS: Dict[str, Permission] = {
    # File operations
    "read": Permission.ALLOW,
    "glob": Permission.ALLOW,
    "grep": Permission.ALLOW,
    "edit": Permission.ALLOW,
    "write": Permission.ALLOW,

    # Shell operations
    "bash": Permission.ALLOW,
    "bash.git_push": Permission.ASK,
    "bash.git_push_force": Permission.DENY,
    "bash.rm_rf": Permission.DENY,
    "bash.systemctl": Permission.DENY,

    # Network operations
    "web_fetch": Permission.ALLOW,
    "web_search": Permission.ALLOW,

    # Agent operations
    "spawn_agent": Permission.ALLOW,
    "kill_agent": Permission.ASK,
}


# Per-genome permission overrides
GENOME_PERMISSIONS: Dict[str, Dict[str, Permission]] = {
    # Explorers - read only
    "claude_explorer": {
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.DENY,
    },
    "opencode_explorer": {
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.DENY,
    },
    "gemini_explorer": {
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.DENY,
    },

    # Builders - full access
    "claude_builder": {
        "edit": Permission.ALLOW,
        "write": Permission.ALLOW,
        "bash": Permission.ALLOW,
        "bash.git_push": Permission.ALLOW,
    },
    "opencode_builder": {
        "edit": Permission.ALLOW,
        "write": Permission.ALLOW,
        "bash": Permission.ALLOW,
    },

    # Orchestrators - coordination only (like Roo Code)
    "claude_orchestrator": {
        "read": Permission.DENY,  # Can't read files directly
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.DENY,
        "spawn_agent": Permission.ALLOW,
    },

    # Patchers - targeted changes only
    "claude_patcher": {
        "edit": Permission.ALLOW,
        "write": Permission.DENY,  # Can't create new files
        "bash": Permission.ASK,
    },

    # Testers - run tests only
    "claude_tester": {
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.ALLOW,  # Need to run test commands
    },

    # R&D - experimental, full access
    "claude_rnd": {
        "edit": Permission.ALLOW,
        "write": Permission.ALLOW,
        "bash": Permission.ALLOW,
    },

    # Business agents - no code access
    "claude_business": {
        "edit": Permission.DENY,
        "write": Permission.DENY,
        "bash": Permission.DENY,
        "web_search": Permission.ALLOW,
    },
}


def check_permission(genome: str, tool: str, sub_action: str = None) -> Permission:
    """Check if genome has permission for tool.

    Args:
        genome: The genome name (e.g., 'claude_builder')
        tool: The tool name (e.g., 'bash')
        sub_action: Optional sub-action (e.g., 'git_push')

    Returns:
        Permission enum value
    """
    # Build permission key
    key = f"{tool}.{sub_action}" if sub_action else tool

    # Check genome-specific first
    genome_perms = GENOME_PERMISSIONS.get(genome, {})

    # Check specific key first, then general tool
    if key in genome_perms:
        return genome_perms[key]
    if tool in genome_perms:
        return genome_perms[tool]

    # Fall back to defaults
    if key in DEFAULT_PERMISSIONS:
        return DEFAULT_PERMISSIONS[key]
    if tool in DEFAULT_PERMISSIONS:
        return DEFAULT_PERMISSIONS[tool]

    # Default allow if not specified
    return Permission.ALLOW


def can_execute(genome: str, tool: str, sub_action: str = None) -> bool:
    """Simple check if tool can be executed."""
    perm = check_permission(genome, tool, sub_action)
    return perm != Permission.DENY


def get_genome_permissions(genome: str) -> Dict[str, str]:
    """Get all effective permissions for a genome."""
    result = {}

    # Start with defaults
    for key, perm in DEFAULT_PERMISSIONS.items():
        result[key] = perm.value

    # Apply genome overrides
    for key, perm in GENOME_PERMISSIONS.get(genome, {}).items():
        result[key] = perm.value

    return result


def list_all_permissions() -> dict:
    """List all genomes and their permissions."""
    return {
        "defaults": {k: v.value for k, v in DEFAULT_PERMISSIONS.items()},
        "genomes": {
            genome: {k: v.value for k, v in perms.items()}
            for genome, perms in GENOME_PERMISSIONS.items()
        }
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        genome = sys.argv[1]
        print(f"\nPermissions for {genome}:")
        print("-" * 40)
        perms = get_genome_permissions(genome)
        for tool, perm in sorted(perms.items()):
            print(f"  {tool}: {perm}")
    else:
        print("Permission System")
        print("=" * 40)
        print("\nUsage: python permissions.py <genome_name>")
        print("\nAvailable genomes:")
        for genome in sorted(GENOME_PERMISSIONS.keys()):
            print(f"  - {genome}")

        print("\nDefault permissions:")
        for tool, perm in sorted(DEFAULT_PERMISSIONS.items()):
            print(f"  {tool}: {perm.value}")
