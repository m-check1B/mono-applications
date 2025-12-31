#!/usr/bin/env python3
"""Kraliki Agent Spawner.

Unified spawner that launches agents across different CLI tools.
Supports: Claude, OpenCode, Gemini, Codex
"""

import subprocess
import sys
import os
import json
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

KRALIKI_DIR = Path(__file__).parent.parent

# Add kraliki to path for imports
sys.path.insert(0, str(KRALIKI_DIR))

# Import new safety and coordination systems
try:
    from control.safety import get_doom_detector, get_mistake_tracker, cleanup_agent
    from control.permissions import (
        check_permission,
        can_execute,
        Permission,
        get_genome_permissions,
    )
    from control.restricted_commands import is_command_safe, get_blocked_commands
    from extensions.hooks import trigger, trigger_sync
    from instruments.loader import get_prompt_injection as get_instruments_prompt

    SAFETY_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Safety systems not fully available: {e}", file=sys.stderr)
    SAFETY_SYSTEMS_AVAILABLE = False
from control import cli_policy, pipeline_policy

GITHUB_DIR = KRALIKI_DIR.parent.parent  # /github
GENOMES_DIR = KRALIKI_DIR / "genomes"
LOGS_DIR = KRALIKI_DIR / "logs" / "agents"
ARENA_DIR = KRALIKI_DIR / "arena"
SPAWN_STATE_FILE = KRALIKI_DIR / "control" / "spawn_state.json"
RUNNING_AGENTS_FILE = KRALIKI_DIR / "control" / "running_agents.json"

# MCP config for agent access to Linear, mgrep, etc.
MCP_CONFIG_PATH = GITHUB_DIR / ".claude" / "mcp.json"

# Lab prefixes for agent IDs
LAB_PREFIXES = {
    "claude": "CC",
    "opencode": "OC",
    "codex": "CX",
    "gemini": "GE",
    "grok": "GR",
}


def load_cli_policy() -> dict:
    """Load CLI availability policy."""
    return cli_policy.load_cli_policy()


def load_pause_state() -> dict:
    """Load swarm pause state."""
    return cli_policy.load_pause_state()


def is_swarm_paused() -> bool:
    """Check if swarm is paused via dashboard."""
    return cli_policy.is_swarm_paused()


def is_cli_enabled(cli: str, policy: Optional[dict] = None) -> bool:
    """Check if a CLI is enabled by policy."""
    return cli_policy.is_cli_enabled(cli, policy=policy)


def get_enabled_clis() -> list:
    """Get list of currently enabled CLIs."""
    return cli_policy.get_enabled_clis()


def load_spawn_state() -> dict:
    """Load spawn state for ID generation."""
    if SPAWN_STATE_FILE.exists():
        try:
            return json.loads(SPAWN_STATE_FILE.read_text())
        except Exception:
            pass
    return {"counters": {}, "last_reset": None}


def load_running_agents() -> dict:
    """Load running agents registry."""
    if RUNNING_AGENTS_FILE.exists():
        try:
            return json.loads(RUNNING_AGENTS_FILE.read_text())
        except Exception:
            pass
    return {"agents": {}}


def save_running_agents(data: dict):
    """Save running agents registry."""
    RUNNING_AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RUNNING_AGENTS_FILE.write_text(json.dumps(data, indent=2))


def register_running_agent(
    agent_id: str, pid: int, genome: str, cli: str, log_file: str
):
    """Register a newly spawned agent in the running agents registry."""
    data = load_running_agents()
    data["agents"][agent_id] = {
        "pid": pid,
        "genome": genome,
        "cli": cli,
        "log_file": log_file,
        "spawned_at": datetime.now().isoformat(),
    }
    data["last_updated"] = datetime.now().isoformat()
    save_running_agents(data)


def unregister_running_agent(agent_id: str) -> dict:
    """Remove an agent from the running agents registry. Returns the agent data."""
    data = load_running_agents()
    agent_data = data["agents"].pop(agent_id, None)
    if agent_data:
        data["last_updated"] = datetime.now().isoformat()
        save_running_agents(data)
    return agent_data


def get_running_agents(filter_cli: Optional[str] = None) -> dict:
    """Get actually running agents by checking PIDs in registry.

    Args:
        filter_cli: Optional CLI filter (e.g., 'codex', 'claude', 'opencode', 'gemini')

    Returns:
        dict: {
            'running': {agent_id: {agent_data}},
            'dead': {agent_id: {agent_data}},  # PIDs no longer alive
            'count': int
        }
    """
    import os

    data = load_running_agents()
    running = {}
    dead = {}

    for agent_id, agent_data in data.get("agents", {}).items():
        pid = agent_data.get("pid")

        if pid is None:
            dead[agent_id] = agent_data
            continue

        cli = agent_data.get("cli", "")
        if filter_cli and cli != filter_cli:
            continue

        try:
            os.kill(pid, 0)
            running[agent_id] = agent_data
        except (ProcessLookupError, OSError):
            dead[agent_id] = agent_data

    return {"running": running, "dead": dead, "count": len(running)}


def cleanup_dead_agents() -> int:
    """Remove dead agents from registry. Returns count of cleaned up agents."""
    result = get_running_agents()
    dead_count = len(result["dead"])

    if dead_count > 0:
        data = load_running_agents()
        for agent_id in result["dead"].keys():
            data["agents"].pop(agent_id, None)
        data["last_updated"] = datetime.now().isoformat()
        save_running_agents(data)

    return dead_count


def save_spawn_state(state: dict):
    """Save spawn state."""
    SPAWN_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SPAWN_STATE_FILE.write_text(json.dumps(state, indent=2))


def generate_agent_id(cli_tool: str, role: str) -> str:
    """Generate unique agent ID in format: LAB-role-HH:MM.DD.MM.XX

    Format: CC-explorer-23:05.24.12.AA
    - LAB prefix (CC, OC, CX, GE, GR)
    - Role extracted from genome
    - Launch time (HH:MM.DD.MM)
    - Sequential suffix (AA, AB, AC...) for same role+lab+time
    """
    state = load_spawn_state()
    now = datetime.now()

    # Reset counters daily
    today = now.strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        state = {"counters": {}, "last_reset": today}

    # Build time component: HH:MM.DD.MM
    time_part = now.strftime("%H:%M.%d.%m")

    # Get lab prefix
    lab = LAB_PREFIXES.get(cli_tool, "XX")

    # Key for counter: lab-role-time
    counter_key = f"{lab}-{role}-{time_part}"

    # Get and increment counter
    count = state["counters"].get(counter_key, 0)
    state["counters"][counter_key] = count + 1

    # Generate suffix: AA, AB, AC... AZ, BA, BB...
    first_letter = chr(ord("A") + (count // 26))
    second_letter = chr(ord("A") + (count % 26))
    suffix = f"{first_letter}{second_letter}"

    save_spawn_state(state)

    # Final ID: CC-explorer-23:05.24.12.AA
    return f"{lab}-{role}-{time_part}.{suffix}"


def extract_role_from_genome(genome_name: str) -> str:
    """Extract role from genome name (e.g., claude_patcher -> patcher)."""
    # Remove cli prefix if present
    for prefix in ["claude_", "opencode_", "gemini_", "codex_", "grok_"]:
        if genome_name.startswith(prefix):
            return genome_name[len(prefix) :]
    return genome_name


def build_agent_system_prompt(agent_id: str, genome_name: str) -> str:
    """Build system prompt context for agent coordination."""

    # Base coordination protocol
    prompt = f"""You are Kraliki agent {agent_id}.

COORDINATION PROTOCOL:
- Check blackboard before starting: python3 {ARENA_DIR}/blackboard.py read -l 10
- Announce claims: python3 {ARENA_DIR}/blackboard.py post "{agent_id}" "CLAIMING: [task]"
- Post completions: python3 {ARENA_DIR}/blackboard.py post "{agent_id}" "DONE: [task]"
- Query Linear for tasks via MCP (linear_searchIssues)
- Output DARWIN_RESULT at end with status and points

MEMORY PROTOCOL (CRITICAL):
- ALWAYS store important findings: python3 {ARENA_DIR}/memory.py store "{agent_id}" "key" "value"
- Retrieve past learnings: python3 {ARENA_DIR}/memory.py retrieve "{agent_id}" "key"
- Store: discoveries, solutions, gotchas, commands that worked
- Your memories help YOU and OTHER agents learn faster

DECISION TRACE PROTOCOL (RECOMMENDED):
- Emit traces for important decisions: python3 {ARENA_DIR}/decision_trace.py emit "{agent_id}" "<type>" "<decision>" -r "<reasoning>"
- Types: task_selection, implementation_strategy, tool_choice, error_handling, completion, skip, delegate, abort
- Query past traces: python3 {ARENA_DIR}/decision_trace.py query -a "{agent_id}"
- This helps build institutional knowledge about agent decision-making"""

    # Add safety systems context if available
    if SAFETY_SYSTEMS_AVAILABLE:
        # Add permissions info
        perms = get_genome_permissions(genome_name)
        denied_tools = [k for k, v in perms.items() if v == "deny"]
        if denied_tools:
            prompt += f"\n\nPERMISSIONS (DENIED for your genome):\n- " + "\n- ".join(
                denied_tools
            )

        # Add restricted commands warning
        blocked = get_blocked_commands()[:10]  # Top 10 blocked commands
        prompt += f"\n\nRESTRICTED COMMANDS (NEVER run these):\n- " + "\n- ".join(
            blocked
        )

        # Add instruments (reusable procedures)
        try:
            instruments_prompt = get_instruments_prompt()
            if instruments_prompt:
                prompt += f"\n\n{instruments_prompt}"
        except Exception:
            pass

        # Add memory bank context
        memory_bank_dir = KRALIKI_DIR / "memory-bank"
        if memory_bank_dir.exists():
            prompt += "\n\nMEMORY BANK (persistent context):"
            for md_file in ["activeContext.md", "progress.md"]:
                md_path = memory_bank_dir / md_file
                if md_path.exists():
                    try:
                        content = md_path.read_text()[:500]  # First 500 chars
                        prompt += f"\n\n--- {md_file} ---\n{content}..."
                    except Exception:
                        pass

    return prompt


# CLI tool configurations
# Models are configured manually per CLI, not hardcoded here
# CLIs use their own default models as set by user
CLI_CONFIGS = {
    "claude": {
        "cmd": ["claude", "-p"],
        "suffix": "",
        "needs_content_arg": True,
    },
    "opencode": {
        "cmd": ["opencode", "run"],
        "suffix": "",
        "needs_content_arg": True,
    },
    "gemini": {
        "cmd": ["gemini", "-y"],
        "suffix": "",
        "needs_content_arg": True,
    },
    "codex": {
        "cmd": [
            "codex",
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
        ],
        "suffix": "",
        "needs_content_arg": True,
    },
}


def get_cli_from_genome(genome_path: Path) -> str:
    """Extract CLI tool from genome frontmatter."""
    content = genome_path.read_text()
    for line in content.split("\n"):
        if line.startswith("cli:"):
            return line.split(":")[1].strip()
    # Default based on filename
    name = genome_path.stem
    if "claude" in name:
        return "claude"
    elif "opencode" in name:
        return "opencode"
    elif "gemini" in name:
        return "gemini"
    elif "codex" in name:
        return "codex"
    return "claude"  # default


def spawn_agent(
    genome_name: str, dry_run: bool = False, respect_policy: bool = True
) -> dict:
    """Spawn an agent from a genome.

    Args:
        genome_name: Name of genome (without .md extension)
        dry_run: If True, don't actually spawn
        respect_policy: If True, enforce pause state and CLI policy

    Returns:
        Dict with spawn result including unique agent_id
    """
    if respect_policy and is_swarm_paused():
        return {
            "success": False,
            "error": "Swarm is PAUSED. Resume via dashboard to spawn agents.",
        }

    # Check if genome is disabled first
    disabled_path = GENOMES_DIR / f"{genome_name}.md.disabled"
    if disabled_path.exists():
        return {
            "success": False,
            "error": f"Genome is DISABLED: {genome_name}. Enable it in dashboard first.",
        }

    # Find genome file
    genome_path = GENOMES_DIR / f"{genome_name}.md"
    if not genome_path.exists():
        # Try with claude_ prefix
        genome_path = GENOMES_DIR / f"claude_{genome_name}.md"
        # Also check if claude_ prefixed version is disabled
        claude_disabled = GENOMES_DIR / f"claude_{genome_name}.md.disabled"
        if claude_disabled.exists():
            return {
                "success": False,
                "error": f"Genome is DISABLED: claude_{genome_name}. Enable it in dashboard first.",
            }
    if not genome_path.exists():
        return {"success": False, "error": f"Genome not found: {genome_name}"}

    # Get CLI tool
    cli_tool = get_cli_from_genome(genome_path)
    if cli_tool not in CLI_CONFIGS:
        return {"success": False, "error": f"Unknown CLI tool: {cli_tool}"}

    if respect_policy:
        policy = load_cli_policy()
        if not is_cli_enabled(cli_tool, policy):
            reason = policy.get("clis", {}).get(cli_tool, {}).get("reason")
            reason_note = f" ({reason})" if reason else ""
            return {
                "success": False,
                "error": f"CLI {cli_tool} is disabled by policy{reason_note}.",
            }

        if not pipeline_policy.is_genome_allowed(genome_name):
            pipeline = pipeline_policy.pipeline_for_genome(genome_name) or "unknown"
            return {
                "success": False,
                "error": f"Pipeline '{pipeline}' is disabled by policy for genome {genome_name}.",
            }

    config = CLI_CONFIGS[cli_tool]

    # Verify CLI tool exists in PATH
    import shutil

    if not shutil.which(config["cmd"][0]):
        return {
            "success": False,
            "error": f"CLI tool '{config['cmd'][0]}' not found in PATH. Please install it or check your environment.",
        }

    # Extract role and generate unique agent ID
    role = extract_role_from_genome(genome_name)
    agent_id = generate_agent_id(cli_tool, role)

    # Check permission to spawn this genome type
    if SAFETY_SYSTEMS_AVAILABLE:
        if not can_execute(genome_name, "spawn_agent"):
            return {
                "success": False,
                "error": f"Permission denied: cannot spawn genome {genome_name}",
            }

        # Trigger pre-spawn hook
        try:
            hook_results = trigger_sync(
                "agent_spawn_before",
                agent_id=agent_id,
                genome=genome_name,
                cli=cli_tool,
            )
            # Check if any hook blocked the spawn
            for result in hook_results:
                if result.get("error") or result.get("result", {}).get("block"):
                    return {
                        "success": False,
                        "error": f"Spawn blocked by hook: {result}",
                    }
        except Exception as e:
            print(f"Warning: Pre-spawn hook failed: {e}")

    # Read genome content and inject agent ID
    genome_content = genome_path.read_text()
    # Inject agent ID at start of genome for agent self-identification
    pipeline_guard = pipeline_policy.build_guard_prompt(genome_name)
    genome_content = f"# AGENT_ID: {agent_id}\n\n{pipeline_guard}\n\n{genome_content}"

    # Prepare log file with agent_id
    log_file = LOGS_DIR / f"{agent_id}.log"

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "agent_id": agent_id,
            "genome": genome_name,
            "cli": cli_tool,
            "log_file": str(log_file),
        }

    # Build command - Claude uses stdin for prompt
    cmd = config["cmd"].copy()

    # Spawn in background
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        with open(log_file, "w") as lf:
            if cli_tool == "claude":
                # Claude with MCP injection, system prompt, and structured output
                system_prompt = build_agent_system_prompt(agent_id, genome_name)
                claude_cmd = [
                    "claude",
                    "-p",
                    "--output-format",
                    "json",
                    "--append-system-prompt",
                    system_prompt,
                ]
                # Add MCP config if exists (gives agent Linear + mgrep access)
                if MCP_CONFIG_PATH.exists():
                    claude_cmd.extend(["--mcp-config", str(MCP_CONFIG_PATH)])

                process = subprocess.Popen(
                    claude_cmd,
                    stdin=subprocess.PIPE,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(GITHUB_DIR),
                    start_new_session=True,
                )
                process.stdin.write(genome_content.encode())
                process.stdin.close()
            elif cli_tool == "gemini":
                # Gemini with yolo mode and structured output
                process = subprocess.Popen(
                    ["gemini", "-y", "--output-format", "json"],
                    stdin=subprocess.PIPE,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(GITHUB_DIR),
                    start_new_session=True,
                )
                process.stdin.write(genome_content.encode())
                process.stdin.close()
            elif cli_tool == "opencode":
                # OpenCode: reads prompt from stdin (use - for stdin mode)
                # Model configured via ~/.config/opencode/opencode.json (not hardcoded here)
                env = os.environ.copy()
                # Ensure LINEAR_API_KEY is available for MCP
                linear_key_path = Path.home() / "secrets" / "linear_api_key.txt"
                if linear_key_path.exists():
                    env["LINEAR_API_KEY"] = linear_key_path.read_text().strip()
                process = subprocess.Popen(
                    ["opencode", "run", "--print-logs", "--format", "json", "-"],
                    stdin=subprocess.PIPE,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(GITHUB_DIR),
                    start_new_session=True,
                    env=env,
                )
                process.stdin.write(genome_content.encode())
                process.stdin.close()
            elif cli_tool == "codex":
                # Codex exec: reads prompt from stdin (use - for stdin mode)
                # --dangerously-bypass-approvals-and-sandbox for headless operation
                process = subprocess.Popen(
                    [
                        "codex",
                        "exec",
                        "--dangerously-bypass-approvals-and-sandbox",
                        "--skip-git-repo-check",
                        "-",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(GITHUB_DIR),
                    start_new_session=True,
                )
                process.stdin.write(genome_content.encode())
                process.stdin.close()
            else:
                # Other CLIs - fallback to command arg
                other_cmd = config["cmd"] + [genome_content]
                process = subprocess.Popen(
                    other_cmd,
                    stdout=lf,
                    stderr=subprocess.STDOUT,
                    cwd=str(GITHUB_DIR),
                    start_new_session=True,
                )

        # Post to social feed with new agent ID format
        try:
            sys.path.insert(0, str(ARENA_DIR))
            from social import post

            post(
                f"🚀 Spawned {agent_id} (genome: {genome_name}, PID: {process.pid})",
                author="kraliki-spawner",
            )
        except Exception:
            pass  # Social feed optional

        # Trigger post-spawn hook
        if SAFETY_SYSTEMS_AVAILABLE:
            try:
                trigger_sync(
                    "agent_spawn_after",
                    agent_id=agent_id,
                    genome=genome_name,
                    cli=cli_tool,
                    pid=process.pid,
                )
            except Exception as e:
                print(f"Warning: Post-spawn hook failed: {e}")

        # Register in running agents for monitoring
        register_running_agent(
            agent_id=agent_id,
            pid=process.pid,
            genome=genome_name,
            cli=cli_tool,
            log_file=str(log_file),
        )

        return {
            "success": True,
            "agent_id": agent_id,
            "genome": genome_name,
            "cli": cli_tool,
            "pid": process.pid,
            "log_file": str(log_file),
        }

    except Exception as e:
        # Trigger error hook
        if SAFETY_SYSTEMS_AVAILABLE:
            try:
                trigger_sync(
                    "agent_error", agent_id=agent_id, error=str(e), genome=genome_name
                )
            except Exception:
                pass
        return {"success": False, "error": str(e)}


def list_genomes(include_disabled: bool = False, respect_policy: bool = True) -> list:
    """List available genomes.

    Args:
        include_disabled: Include .md.disabled files
        respect_policy: Filter out genomes whose CLI is disabled by policy
    """
    genomes = []
    # List enabled genomes
    for f in GENOMES_DIR.glob("*.md"):
        if f.suffix == ".md" and not str(f).endswith(".md.disabled"):
            cli = get_cli_from_genome(f)
            cli_allowed = is_cli_enabled(cli)

            # Skip if CLI is disabled by policy and we're respecting policy
            if respect_policy and not cli_allowed:
                continue

            genomes.append(
                {
                    "name": f.stem,
                    "cli": cli,
                    "path": str(f),
                    "enabled": True,
                    "cli_allowed": cli_allowed,
                }
            )
    # List disabled genomes if requested
    if include_disabled:
        for f in GENOMES_DIR.glob("*.md.disabled"):
            name = f.stem.replace(".md", "")
            genomes.append(
                {
                    "name": name,
                    "cli": "unknown",  # Can't read cli from disabled file easily
                    "path": str(f),
                    "enabled": False,
                    "cli_allowed": False,
                }
            )
    return genomes


def toggle_cli(cli: str, enable: bool) -> bool:
    """Toggle a CLI's enabled status in the policy file."""
    policy = load_cli_policy()
    if cli not in policy.get("clis", {}):
        policy.setdefault("clis", {})[cli] = {
            "enabled": enable,
            "reason": "Toggled via CLI",
        }
    else:
        policy["clis"][cli]["enabled"] = enable
    cli_policy.save_cli_policy(policy)
    return True


def main():
    parser = argparse.ArgumentParser(description="Kraliki Agent Spawner")
    parser.add_argument("genome", nargs="?", help="Genome name to spawn")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available genomes"
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Don't actually spawn"
    )
    parser.add_argument("--all", "-a", action="store_true", help="Spawn all genomes")
    parser.add_argument("--policy", action="store_true", help="Show CLI policy status")
    parser.add_argument(
        "--enable-cli",
        metavar="CLI",
        help="Enable a CLI (opencode, gemini, codex, claude)",
    )
    parser.add_argument("--disable-cli", metavar="CLI", help="Disable a CLI")
    parser.add_argument(
        "--ignore-policy",
        action="store_true",
        help="Ignore CLI policy when listing/spawning",
    )

    args = parser.parse_args()

    # Show CLI policy
    if args.policy:
        policy = load_cli_policy()
        print("CLI Policy Status:")
        print("-" * 40)
        for cli in ["opencode", "gemini", "codex", "claude"]:
            config = policy.get("clis", {}).get(cli, {})
            status = "ENABLED" if config.get("enabled", True) else "DISABLED"
            reason = config.get("reason", "default")
            print(f"  {cli:12} {status:10} ({reason})")
        print("-" * 40)
        enabled = get_enabled_clis()
        print(f"Active CLIs: {', '.join(enabled) if enabled else 'none'}")
        return

    # Toggle CLI
    if args.enable_cli:
        toggle_cli(args.enable_cli, True)
        print(f"Enabled CLI: {args.enable_cli}")
        return

    if args.disable_cli:
        toggle_cli(args.disable_cli, False)
        print(f"Disabled CLI: {args.disable_cli}")
        return

    # List genomes
    if args.list:
        respect_policy = not args.ignore_policy
        genomes = list_genomes(respect_policy=respect_policy)
        policy_note = "" if respect_policy else " (ignoring policy)"
        print(f"Available genomes ({len(genomes)}){policy_note}:")
        for g in genomes:
            print(f"  {g['name']} ({g['cli']})")
        if respect_policy:
            enabled_clis = get_enabled_clis()
            print(f"\nActive CLIs: {', '.join(enabled_clis)}")
            print("Use --policy to see full status, --ignore-policy to list all")
        return

    if args.all:
        respect_policy = not args.ignore_policy
        genomes = list_genomes(respect_policy=respect_policy)
        results = []
        for g in genomes:
            result = spawn_agent(
                g["name"], dry_run=args.dry_run, respect_policy=respect_policy
            )
            results.append(result)
            status = "OK" if result["success"] else "FAIL"
            print(f"  [{status}] {g['name']}")
        return

    if not args.genome:
        parser.print_help()
        return

    result = spawn_agent(
        args.genome, dry_run=args.dry_run, respect_policy=not args.ignore_policy
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
