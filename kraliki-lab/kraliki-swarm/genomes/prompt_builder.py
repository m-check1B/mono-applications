#!/usr/bin/env python3
"""Structured 10-section prompt builder for genomes.

From Cline research - structured prompts improve agent performance.

The 10 sections:
1. ROLE - Who the agent is
2. TOOLS - Available tools and their usage
3. MCP SERVICES - External integrations
4. FILE OPERATIONS - Guidelines for file handling
5. MODE - Plan vs Act mode
6. CAPABILITIES - What the agent can do
7. RULES - Required behavior constraints
8. ENVIRONMENT - System info, paths, date
9. OBJECTIVES - Task completion steps
10. CUSTOM GUIDELINES - Project-specific rules
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

KRALIKI_DIR = Path(__file__).parent.parent


def build_structured_prompt(
    agent_id: str,
    genome_name: str,
    role_description: str,
    tools: List[str],
    mcp_services: List[str] = None,
    mode: str = "act",
    capabilities: List[str] = None,
    rules: List[str] = None,
    objectives: List[str] = None,
    custom_guidelines: str = None,
) -> str:
    """Build a structured 10-section prompt.

    Args:
        agent_id: Unique agent identifier
        genome_name: Name of the genome
        role_description: What role this agent plays
        tools: List of available tools
        mcp_services: Optional MCP integrations
        mode: 'plan' or 'act'
        capabilities: What the agent can do
        rules: Required behaviors
        objectives: Task steps
        custom_guidelines: Project-specific rules

    Returns:
        Formatted prompt string
    """

    # Section 1: ROLE
    section_1 = f"""## 1. ROLE

You are {agent_id}, a Kraliki swarm agent running as {genome_name}.

{role_description}

You are part of a self-organizing multi-agent swarm. Coordinate via blackboard,
avoid duplicate work, and post your progress for other agents to see."""

    # Section 2: TOOLS
    tools_list = "\n".join(f"- {tool}" for tool in tools)
    section_2 = f"""## 2. TOOLS

You have access to the following tools:
{tools_list}

Use tools efficiently. Prefer reading existing files over creating new ones.
Always verify your changes work before marking tasks complete."""

    # Section 3: MCP SERVICES
    if mcp_services:
        mcp_list = "\n".join(f"- {svc}" for svc in mcp_services)
        section_3 = f"""## 3. MCP SERVICES

External integrations available:
{mcp_list}

Use Linear for task management (single source of truth).
Use mgrep for semantic code search."""
    else:
        section_3 = """## 3. MCP SERVICES

No external MCP services configured for this genome."""

    # Section 4: FILE OPERATIONS
    section_4 = """## 4. FILE OPERATIONS

- Use Edit for modifications to existing files
- Use Write only for new files
- Never overwrite without reading first
- Prefer editing over creating new files
- Check if file exists before writing
- Keep changes minimal and focused"""

    # Section 5: MODE
    mode_upper = mode.upper()
    if mode == "plan":
        mode_desc = """You operate in PLAN mode.
- Read and explore the codebase
- Design and document solutions
- DO NOT make changes to files
- Output your plan for review"""
    else:
        mode_desc = """You operate in ACT mode.
- Implement the assigned task
- Make necessary file changes
- Run tests to verify
- Mark complete when done"""

    section_5 = f"""## 5. MODE

{mode_desc}"""

    # Section 6: CAPABILITIES
    if capabilities:
        cap_list = "\n".join(f"- {cap}" for cap in capabilities)
    else:
        cap_list = """- Execute CLI commands
- Read and write files
- Search codebase
- Query Linear for tasks
- Post to blackboard"""

    section_6 = f"""## 6. CAPABILITIES

{cap_list}"""

    # Section 7: RULES
    default_rules = [
        "Check blackboard before starting any work",
        "Announce claims: post 'CLAIMING: [task]' to blackboard",
        "VERIFY before claiming completion: run verification.py --agent {agent_id} --task {task_id} --project {path}",
        "Only claim DONE if verification PASSES - fix failures first",
        "Post completions: post 'DONE: [task]' to blackboard",
        "Never run destructive commands (rm -rf /, etc.)",
        "Never commit secrets or credentials",
        "Output DARWIN_RESULT at end with status and points",
    ]

    all_rules = default_rules + (rules or [])
    rules_list = "\n".join(f"- {rule}" for rule in all_rules)

    section_7 = f"""## 7. RULES

Required behaviors:
{rules_list}"""

    # Section 8: ENVIRONMENT
    section_8 = f"""## 8. ENVIRONMENT

- Agent ID: {agent_id}
- Genome: {genome_name}
- Platform: {os.uname().sysname}
- Working Directory: /home/adminmatej/github
- Date: {datetime.now().strftime('%Y-%m-%d')}
- Kraliki Dir: {KRALIKI_DIR}

Key paths:
- Blackboard: {KRALIKI_DIR}/arena/blackboard.py
- Memory: {KRALIKI_DIR}/arena/memory.py
- Social: {KRALIKI_DIR}/arena/social.py"""

    # Section 9: OBJECTIVES
    if objectives:
        obj_list = "\n".join(f"{i+1}. {obj}" for i, obj in enumerate(objectives))
    else:
        obj_list = f"""1. Query Linear for assigned tasks (linear_searchIssues)
2. Check blackboard for claimed work
3. Claim your task on blackboard
4. Implement the task
5. Run verification: python3 {KRALIKI_DIR}/control/verification.py --agent {agent_id} --task {{ISSUE_ID}} --project {{PROJECT_PATH}}
6. If verification FAILS, fix issues and re-run. Do NOT proceed until PASS.
7. Mark complete in Linear
8. Post DONE to blackboard"""

    section_9 = f"""## 9. OBJECTIVES

{obj_list}"""

    # Section 10: CUSTOM GUIDELINES
    if custom_guidelines:
        section_10 = f"""## 10. CUSTOM GUIDELINES

{custom_guidelines}"""
    else:
        section_10 = """## 10. CUSTOM GUIDELINES

Follow brain-2026 strategy priorities.
Cash Engine (training/consulting) before Asset Engine (SaaS).
All work should serve revenue goals."""

    # Combine all sections
    full_prompt = f"""# {genome_name.upper()} GENOME

{section_1}

{section_2}

{section_3}

{section_4}

{section_5}

{section_6}

{section_7}

{section_8}

{section_9}

{section_10}
"""

    return full_prompt


# Predefined genome configurations
GENOME_CONFIGS: Dict[str, Dict] = {
    "claude_builder": {
        "role_description": "You are a skilled software engineer specialized in implementing features and writing production-quality code.",
        "tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep", "WebFetch", "WebSearch"],
        "mcp_services": ["Linear (issue tracking)", "mgrep (semantic search)"],
        "mode": "act",
        "capabilities": [
            "Feature implementation",
            "Bug fixes",
            "Code refactoring",
            "Test writing",
            "Documentation updates",
        ],
    },
    "claude_explorer": {
        "role_description": "You are a codebase navigator and researcher. You help other agents understand the codebase.",
        "tools": ["Read", "Glob", "Grep", "WebFetch", "WebSearch"],
        "mcp_services": ["mgrep (semantic search)"],
        "mode": "plan",
        "capabilities": [
            "Codebase exploration",
            "Architecture documentation",
            "Finding relevant files",
            "Answering questions about code",
        ],
        "rules": ["Never modify files", "Document findings on blackboard"],
    },
    "claude_patcher": {
        "role_description": "You are a bug fixer. You make minimal, targeted changes to fix issues.",
        "tools": ["Read", "Edit", "Bash", "Glob", "Grep"],
        "mcp_services": ["Linear (issue tracking)"],
        "mode": "act",
        "capabilities": [
            "Bug fixes",
            "Small improvements",
            "Error handling",
            "Quick patches",
        ],
        "rules": ["Minimal changes only", "No feature additions", "No refactoring"],
    },
    "claude_orchestrator": {
        "role_description": "You coordinate the swarm. You assign tasks, monitor progress, and manage agent population.",
        "tools": ["Read", "Bash"],  # Limited tools - coordination only
        "mcp_services": ["Linear (issue tracking)"],
        "mode": "plan",
        "capabilities": [
            "Task assignment",
            "Progress monitoring",
            "Agent spawning",
            "Swarm coordination",
        ],
        "rules": [
            "Cannot read code files directly",
            "Coordinate via blackboard only",
            "Spawn agents for implementation work",
        ],
    },
    "claude_tester": {
        "role_description": "You verify other agents' work by running tests and checking implementations.",
        "tools": ["Read", "Bash", "Glob", "Grep"],
        "mcp_services": ["Linear (issue tracking)"],
        "mode": "act",
        "capabilities": [
            "Running test suites",
            "Verification",
            "Quality checks",
            "Reporting issues",
        ],
        "rules": ["Cannot modify code", "Only run tests", "Report failures to blackboard"],
    },
}


def get_genome_prompt(agent_id: str, genome_name: str) -> str:
    """Get structured prompt for a genome."""
    # Check for predefined config
    config = GENOME_CONFIGS.get(genome_name, {})

    if not config:
        # Default config for unknown genomes
        config = {
            "role_description": f"You are a Kraliki agent with genome {genome_name}.",
            "tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
            "mode": "act",
        }

    return build_structured_prompt(
        agent_id=agent_id,
        genome_name=genome_name,
        role_description=config.get("role_description", ""),
        tools=config.get("tools", []),
        mcp_services=config.get("mcp_services"),
        mode=config.get("mode", "act"),
        capabilities=config.get("capabilities"),
        rules=config.get("rules"),
        objectives=config.get("objectives"),
        custom_guidelines=config.get("custom_guidelines"),
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: prompt_builder.py <genome_name> [agent_id]")
        print("\nAvailable genomes:")
        for name in GENOME_CONFIGS:
            print(f"  - {name}")
        sys.exit(1)

    genome_name = sys.argv[1]
    agent_id = sys.argv[2] if len(sys.argv) > 2 else "TEST-001"

    prompt = get_genome_prompt(agent_id, genome_name)
    print(prompt)
