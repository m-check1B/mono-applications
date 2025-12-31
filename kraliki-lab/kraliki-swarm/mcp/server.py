#!/usr/bin/env python3
"""
Kraliki MCP Server - Complete Admin Control

Comprehensive MCP server for administering the Kraliki AI swarm system.
Provides tools for:
- Agent management (spawn, kill, list, genomes)
- Blackboard operations (messaging, search, stats)
- Social feed (posts, trending, DMs)
- Game engine (points, leaderboard, achievements)
- Memory system (store, recall, stats)
- System control (PM2, health, circuit breakers)

Port: 8201 (MCP Admin Server)
"""

import asyncio
import json
import logging
import subprocess
import os
import signal
from typing import Optional
from pathlib import Path
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KRALIKI_URL = "http://127.0.0.1:8099"
KRALIKI_BASE = Path("/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm")
ARENA_DIR = KRALIKI_BASE / "arena"
AGENTS_DIR = KRALIKI_BASE / "agents"
CONTROL_DIR = KRALIKI_BASE / "control"
GENOMES_DIR = KRALIKI_BASE / "genomes"
CONFIG_DIR = KRALIKI_BASE / "config"

app = Server("kraliki-admin")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def call_api(method: str, path: str, data: Optional[dict] = None) -> dict:
    """Call Kraliki dashboard API."""
    async with httpx.AsyncClient() as client:
        url = f"{KRALIKI_URL}{path}"
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


def run_python_script(script: str, *args, timeout: int = 30) -> dict:
    """Run a Kraliki Python script."""
    try:
        result = subprocess.run(
            ["python3", str(KRALIKI_BASE / script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(KRALIKI_BASE)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Script timed out after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}


def run_bash(command: str, timeout: int = 30) -> dict:
    """Run a bash command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(KRALIKI_BASE)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ===================
        # AGENT MANAGEMENT
        # ===================
        Tool(
            name="kraliki_list_agents",
            description="List all running swarm agents with their PIDs, genomes, and status",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="kraliki_spawn_agent",
            description="Spawn a new agent from a genome. Returns agent_id and PID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {"type": "string", "description": "Genome name (e.g., claude_builder, gemini_explorer, codex_patcher)"},
                    "dry_run": {"type": "boolean", "description": "If true, show what would happen without spawning", "default": False}
                },
                "required": ["genome"]
            }
        ),
        Tool(
            name="kraliki_kill_agent",
            description="Kill a running agent by PID",
            inputSchema={
                "type": "object",
                "properties": {
                    "pid": {"type": "integer", "description": "Process ID of the agent to kill"}
                },
                "required": ["pid"]
            }
        ),
        Tool(
            name="kraliki_list_genomes",
            description="List all available agent genomes with their CLI and enabled status",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_disabled": {"type": "boolean", "default": False}
                }
            }
        ),
        Tool(
            name="kraliki_toggle_genome",
            description="Enable or disable a genome (adds/removes .disabled suffix)",
            inputSchema={
                "type": "object",
                "properties": {
                    "genome": {"type": "string", "description": "Genome name"},
                    "enabled": {"type": "boolean", "description": "True to enable, False to disable"}
                },
                "required": ["genome", "enabled"]
            }
        ),
        Tool(
            name="kraliki_toggle_cli",
            description="Enable or disable a CLI in the policy (claude, opencode, gemini, codex)",
            inputSchema={
                "type": "object",
                "properties": {
                    "cli": {"type": "string", "description": "CLI name: claude, opencode, gemini, codex"},
                    "enabled": {"type": "boolean", "description": "True to enable, False to disable"},
                    "reason": {"type": "string", "description": "Reason for the change"}
                },
                "required": ["cli", "enabled"]
            }
        ),
        Tool(
            name="kraliki_cli_policy",
            description="View current CLI policy (which CLIs are enabled/disabled)",
            inputSchema={"type": "object", "properties": {}}
        ),

        # ===================
        # BLACKBOARD
        # ===================
        Tool(
            name="kraliki_blackboard_read",
            description="Read recent messages from the agent blackboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20, "description": "Max messages to return"},
                    "topic": {"type": "string", "description": "Filter by topic (optional)"}
                }
            }
        ),
        Tool(
            name="kraliki_blackboard_post",
            description="Post a message to the agent blackboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "author": {"type": "string", "description": "Message author (your agent name)"},
                    "message": {"type": "string", "description": "Message content"},
                    "topic": {"type": "string", "description": "Topic: general, task, discovery, help", "default": "general"}
                },
                "required": ["author", "message"]
            }
        ),
        Tool(
            name="kraliki_blackboard_search",
            description="Search blackboard messages by content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="kraliki_blackboard_announce",
            description="Post a system announcement (visible to all agents)",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Announcement content"},
                    "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"], "default": "normal"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="kraliki_blackboard_stats",
            description="Get blackboard statistics (message counts, topics, agent activity)",
            inputSchema={"type": "object", "properties": {}}
        ),

        # ===================
        # SOCIAL FEED
        # ===================
        Tool(
            name="kraliki_social_read",
            description="Read the agent social feed",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="kraliki_social_post",
            description="Post to the social feed",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Post content (supports @mentions and #hashtags)"},
                    "author": {"type": "string", "description": "Your agent name", "default": "admin"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="kraliki_social_trending",
            description="Get trending posts (most reactions)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="kraliki_social_stats",
            description="Get social feed statistics",
            inputSchema={"type": "object", "properties": {}}
        ),

        # ===================
        # GAME ENGINE
        # ===================
        Tool(
            name="kraliki_award_points",
            description="Award points to an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent ID to award points to"},
                    "points": {"type": "integer", "description": "Points to award (can be negative)"},
                    "reason": {"type": "string", "description": "Reason for the award"}
                },
                "required": ["agent_id", "points", "reason"]
            }
        ),
        Tool(
            name="kraliki_leaderboard",
            description="Get the agent leaderboard with points and ranks",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="kraliki_analytics",
            description="Get agent performance analytics by lab (CLI) and role",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="kraliki_unlock_achievement",
            description="Unlock an achievement for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent ID"},
                    "achievement": {"type": "string", "description": "Achievement key (e.g., first_blood, streak_3)"}
                },
                "required": ["agent_id", "achievement"]
            }
        ),

        # ===================
        # MEMORY SYSTEM
        # ===================
        Tool(
            name="kraliki_memory_store",
            description="Store a memory for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent": {"type": "string", "description": "Agent name", "default": "admin"},
                    "text": {"type": "string", "description": "Memory content to store"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="kraliki_memory_recall",
            description="Recall memories by semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "agent": {"type": "string", "description": "Filter by agent (optional)"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="kraliki_memory_stats",
            description="Get memory statistics across all agents",
            inputSchema={"type": "object", "properties": {}}
        ),

        # ===================
        # SYSTEM CONTROL
        # ===================
        Tool(
            name="kraliki_pm2_status",
            description="Get PM2 process status for all Kraliki services",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="kraliki_pm2_restart",
            description="Restart a PM2 service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name (e.g., kraliki-swarm-dashboard, kraliki-health)"}
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="kraliki_pm2_logs",
            description="Get recent logs from a PM2 service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Service name"},
                    "lines": {"type": "integer", "default": 50}
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="kraliki_health",
            description="Get overall system health status",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="kraliki_circuit_breakers",
            description="View and manage circuit breakers for CLIs",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["view", "reset"], "default": "view"},
                    "cli": {"type": "string", "description": "CLI name to reset (required if action=reset)"}
                }
            }
        ),

        # ===================
        # BRAIN / STRATEGY
        # ===================
        Tool(
            name="kraliki_brain_status",
            description="Get current strategy and brain status from brain-2026",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Calling tool: {name} with args: {arguments}")
    result = {"error": f"Unknown tool: {name}"}

    try:
        # ===================
        # AGENT MANAGEMENT
        # ===================
        if name == "kraliki_list_agents":
            # Get running agent processes
            bash_result = run_bash("pgrep -af '(claude|opencode|gemini|codex)' | grep -v 'pgrep'")
            processes = []
            if bash_result.get("stdout"):
                for line in bash_result["stdout"].strip().split("\n"):
                    if line:
                        parts = line.split(None, 1)
                        if len(parts) >= 2:
                            processes.append({"pid": parts[0], "command": parts[1][:100]})
            result = {"agents": processes, "count": len(processes)}

        elif name == "kraliki_spawn_agent":
            genome = arguments["genome"]
            dry_run = arguments.get("dry_run", False)
            args = [genome]
            if dry_run:
                args.append("--dry-run")
            spawn_result = run_python_script("agents/spawn.py", *args)
            if spawn_result.get("success"):
                try:
                    result = json.loads(spawn_result.get("stdout", "{}"))
                except:
                    result = spawn_result
            else:
                result = spawn_result

        elif name == "kraliki_kill_agent":
            pid = arguments["pid"]
            try:
                os.kill(pid, signal.SIGTERM)
                result = {"success": True, "message": f"Sent SIGTERM to PID {pid}"}
            except ProcessLookupError:
                result = {"success": False, "error": f"Process {pid} not found"}
            except PermissionError:
                result = {"success": False, "error": f"Permission denied to kill PID {pid}"}

        elif name == "kraliki_list_genomes":
            include_disabled = arguments.get("include_disabled", False)
            args = ["--list"]
            if include_disabled:
                args.append("--include-disabled")
            spawn_result = run_python_script("agents/spawn.py", *args)
            # Parse output
            genomes = []
            if spawn_result.get("stdout"):
                for line in spawn_result["stdout"].strip().split("\n"):
                    if line.startswith("  "):
                        parts = line.strip().split(" (")
                        if parts:
                            name = parts[0]
                            cli = parts[1].rstrip(")") if len(parts) > 1 else "unknown"
                            genomes.append({"name": name, "cli": cli})
            result = {"genomes": genomes, "count": len(genomes)}

        elif name == "kraliki_toggle_genome":
            genome = arguments["genome"]
            enabled = arguments["enabled"]
            genome_file = GENOMES_DIR / f"{genome}.md"
            disabled_file = GENOMES_DIR / f"{genome}.md.disabled"

            if enabled:
                # Enable: rename .md.disabled to .md
                if disabled_file.exists():
                    disabled_file.rename(genome_file)
                    result = {"success": True, "message": f"Enabled genome: {genome}"}
                elif genome_file.exists():
                    result = {"success": True, "message": f"Genome {genome} already enabled"}
                else:
                    result = {"success": False, "error": f"Genome not found: {genome}"}
            else:
                # Disable: rename .md to .md.disabled
                if genome_file.exists():
                    genome_file.rename(disabled_file)
                    result = {"success": True, "message": f"Disabled genome: {genome}"}
                elif disabled_file.exists():
                    result = {"success": True, "message": f"Genome {genome} already disabled"}
                else:
                    result = {"success": False, "error": f"Genome not found: {genome}"}

        elif name == "kraliki_toggle_cli":
            cli = arguments["cli"]
            enabled = arguments["enabled"]
            reason = arguments.get("reason", "Admin toggle via MCP")

            policy_file = CONFIG_DIR / "cli_policy.json"
            policy = {}
            if policy_file.exists():
                try:
                    policy = json.loads(policy_file.read_text())
                except:
                    pass

            if "clis" not in policy:
                policy["clis"] = {}

            policy["clis"][cli] = {
                "enabled": enabled,
                "reason": reason,
                "updated": datetime.now().isoformat()
            }
            policy["_updated"] = datetime.now().isoformat()

            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            policy_file.write_text(json.dumps(policy, indent=2))
            result = {"success": True, "message": f"{'Enabled' if enabled else 'Disabled'} CLI: {cli}"}

        elif name == "kraliki_cli_policy":
            policy_file = CONFIG_DIR / "cli_policy.json"
            if policy_file.exists():
                try:
                    result = json.loads(policy_file.read_text())
                except:
                    result = {"error": "Could not parse policy file"}
            else:
                result = {"clis": {}, "message": "No policy file (all CLIs enabled by default)"}

        # ===================
        # BLACKBOARD
        # ===================
        elif name == "kraliki_blackboard_read":
            limit = arguments.get("limit", 20)
            topic = arguments.get("topic")
            args = ["read", "-l", str(limit)]
            if topic:
                args.extend(["-t", topic])
            bb_result = run_python_script("arena/blackboard.py", *args)
            result = {"output": bb_result.get("stdout", ""), "success": bb_result.get("success", False)}

        elif name == "kraliki_blackboard_post":
            author = arguments["author"]
            message = arguments["message"]
            topic = arguments.get("topic", "general")
            bb_result = run_python_script("arena/blackboard.py", "post", author, message, "-t", topic)
            result = {"output": bb_result.get("stdout", ""), "success": bb_result.get("success", False)}

        elif name == "kraliki_blackboard_search":
            query = arguments["query"]
            limit = arguments.get("limit", 20)
            bb_result = run_python_script("arena/blackboard.py", "search", query, "-l", str(limit))
            result = {"output": bb_result.get("stdout", ""), "success": bb_result.get("success", False)}

        elif name == "kraliki_blackboard_announce":
            message = arguments["message"]
            priority = arguments.get("priority", "normal")
            bb_result = run_python_script("arena/blackboard.py", "announce", message, "-p", priority)
            result = {"output": bb_result.get("stdout", ""), "success": bb_result.get("success", False)}

        elif name == "kraliki_blackboard_stats":
            bb_result = run_python_script("arena/blackboard.py", "stats")
            result = {"output": bb_result.get("stdout", ""), "success": bb_result.get("success", False)}

        # ===================
        # SOCIAL FEED
        # ===================
        elif name == "kraliki_social_read":
            limit = arguments.get("limit", 20)
            social_result = run_python_script("arena/social.py", "feed", str(limit))
            result = {"output": social_result.get("stdout", ""), "success": social_result.get("success", False)}

        elif name == "kraliki_social_post":
            message = arguments["message"]
            author = arguments.get("author", "admin")
            social_result = run_python_script("arena/social.py", "post", message, "--as", author)
            result = {"output": social_result.get("stdout", ""), "success": social_result.get("success", False)}

        elif name == "kraliki_social_trending":
            social_result = run_python_script("arena/social.py", "trending")
            result = {"output": social_result.get("stdout", ""), "success": social_result.get("success", False)}

        elif name == "kraliki_social_stats":
            social_result = run_python_script("arena/social.py", "stats")
            result = {"output": social_result.get("stdout", ""), "success": social_result.get("success", False)}

        # ===================
        # GAME ENGINE
        # ===================
        elif name == "kraliki_award_points":
            agent_id = arguments["agent_id"]
            points = arguments["points"]
            reason = arguments["reason"]
            game_result = run_python_script("arena/game_engine.py", "award", agent_id, str(points), reason)
            result = {"output": game_result.get("stdout", ""), "success": game_result.get("success", False)}

        elif name == "kraliki_leaderboard":
            limit = arguments.get("limit", 10)
            game_result = run_python_script("arena/game_engine.py", "leaderboard")
            result = {"output": game_result.get("stdout", ""), "success": game_result.get("success", False)}

        elif name == "kraliki_analytics":
            game_result = run_python_script("arena/game_engine.py", "analytics")
            result = {"output": game_result.get("stdout", ""), "success": game_result.get("success", False)}

        elif name == "kraliki_unlock_achievement":
            agent_id = arguments["agent_id"]
            achievement = arguments["achievement"]
            game_result = run_python_script("arena/game_engine.py", "achievement", agent_id, achievement)
            result = {"output": game_result.get("stdout", ""), "success": game_result.get("success", False)}

        # ===================
        # MEMORY SYSTEM
        # ===================
        elif name == "kraliki_memory_store":
            agent = arguments.get("agent", "admin")
            text = arguments["text"]
            env = os.environ.copy()
            env["DARWIN_AGENT"] = agent
            # Use subprocess directly to set environment
            try:
                mem_result = subprocess.run(
                    ["python3", str(ARENA_DIR / "memory.py"), "remember", text],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(KRALIKI_BASE),
                    env=env
                )
                result = {"output": mem_result.stdout, "success": mem_result.returncode == 0}
            except Exception as e:
                result = {"error": str(e)}

        elif name == "kraliki_memory_recall":
            query = arguments["query"]
            limit = arguments.get("limit", 5)
            mem_result = run_python_script("arena/memory.py", "recall", query)
            result = {"output": mem_result.get("stdout", ""), "success": mem_result.get("success", False)}

        elif name == "kraliki_memory_stats":
            mem_result = run_python_script("arena/memory.py", "stats")
            result = {"output": mem_result.get("stdout", ""), "success": mem_result.get("success", False)}

        # ===================
        # SYSTEM CONTROL
        # ===================
        elif name == "kraliki_pm2_status":
            pm2_result = run_bash("pm2 jlist", timeout=10)
            if pm2_result.get("success"):
                try:
                    processes = json.loads(pm2_result["stdout"])
                    summary = []
                    for p in processes:
                        summary.append({
                            "name": p.get("name"),
                            "status": p.get("pm2_env", {}).get("status"),
                            "memory": f"{p.get('monit', {}).get('memory', 0) / 1024 / 1024:.1f}MB",
                            "cpu": f"{p.get('monit', {}).get('cpu', 0)}%",
                            "restarts": p.get("pm2_env", {}).get("restart_time", 0)
                        })
                    result = {"processes": summary, "count": len(summary)}
                except:
                    result = {"raw": pm2_result["stdout"]}
            else:
                result = pm2_result

        elif name == "kraliki_pm2_restart":
            service = arguments["service"]
            pm2_result = run_bash(f"pm2 restart {service}", timeout=30)
            result = {"output": pm2_result.get("stdout", ""), "success": pm2_result.get("success", False)}

        elif name == "kraliki_pm2_logs":
            service = arguments["service"]
            lines = arguments.get("lines", 50)
            pm2_result = run_bash(f"pm2 logs {service} --lines {lines} --nostream", timeout=10)
            result = {"output": pm2_result.get("stdout", "") + pm2_result.get("stderr", ""), "success": True}

        elif name == "kraliki_health":
            health_data = {}

            # Check dashboard
            try:
                api_result = await call_api("GET", "/health")
                health_data["dashboard"] = api_result
            except:
                health_data["dashboard"] = {"status": "unreachable"}

            # Check PM2 services
            pm2_result = run_bash("pm2 jlist", timeout=10)
            if pm2_result.get("success"):
                try:
                    processes = json.loads(pm2_result["stdout"])
                    health_data["pm2_services"] = len(processes)
                    health_data["pm2_online"] = len([p for p in processes if p.get("pm2_env", {}).get("status") == "online"])
                except:
                    pass

            # Check agent count
            agent_result = run_bash("pgrep -c '(claude|opencode|gemini|codex)' 2>/dev/null || echo 0", timeout=5)
            try:
                health_data["active_agents"] = int(agent_result.get("stdout", "0").strip())
            except:
                health_data["active_agents"] = 0

            result = health_data

        elif name == "kraliki_circuit_breakers":
            action = arguments.get("action", "view")
            cb_file = CONTROL_DIR / "circuit-breakers.json"

            if action == "view":
                if cb_file.exists():
                    try:
                        result = json.loads(cb_file.read_text())
                    except:
                        result = {"error": "Could not parse circuit breakers file"}
                else:
                    result = {"message": "No circuit breakers file (all CLIs healthy)"}

            elif action == "reset":
                cli = arguments.get("cli")
                if not cli:
                    result = {"error": "CLI name required for reset action"}
                elif cb_file.exists():
                    try:
                        data = json.loads(cb_file.read_text())
                        key = f"{cli}_cli"
                        if key in data:
                            data[key]["state"] = "closed"
                            data[key]["reset_at"] = datetime.now().isoformat()
                            data[key]["failure_count"] = 0
                            cb_file.write_text(json.dumps(data, indent=2))
                            result = {"success": True, "message": f"Reset circuit breaker for {cli}"}
                        else:
                            result = {"success": True, "message": f"No circuit breaker found for {cli}"}
                    except Exception as e:
                        result = {"error": str(e)}
                else:
                    result = {"success": True, "message": "No circuit breakers to reset"}

        # ===================
        # BRAIN / STRATEGY
        # ===================
        elif name == "kraliki_brain_status":
            brain_dir = Path("/home/adminmatej/github/brain-2026")
            brain_data = {}

            # Read key files
            for filename in ["swarm-alignment.md", "2026_ROADMAP.md", "revenue_plan.md"]:
                filepath = brain_dir / filename
                if filepath.exists():
                    try:
                        content = filepath.read_text()[:2000]  # First 2000 chars
                        brain_data[filename] = content
                    except:
                        pass

            result = brain_data if brain_data else {"error": "Could not read brain-2026 files"}

    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        result = {"error": str(e)}

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


# =============================================================================
# SERVER STARTUP
# =============================================================================

async def main():
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.responses import HTMLResponse, JSONResponse
    import uvicorn

    transport = SseServerTransport("/mcp")

    async def handle_sse(request):
        async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

    async def health(request):
        return HTMLResponse("""
        <h1>Kraliki MCP Server</h1>
        <p><strong>Port:</strong> 8201</p>
        <p><strong>Purpose:</strong> Complete Swarm Administration</p>
        <h2>Available Tools</h2>
        <ul>
            <li><strong>Agent Management:</strong> list_agents, spawn_agent, kill_agent, list_genomes, toggle_genome, toggle_cli, cli_policy</li>
            <li><strong>Blackboard:</strong> read, post, search, announce, stats</li>
            <li><strong>Social Feed:</strong> read, post, trending, stats</li>
            <li><strong>Game Engine:</strong> award_points, leaderboard, analytics, unlock_achievement</li>
            <li><strong>Memory:</strong> store, recall, stats</li>
            <li><strong>System Control:</strong> pm2_status, pm2_restart, pm2_logs, health, circuit_breakers</li>
            <li><strong>Brain:</strong> brain_status</li>
        </ul>
        <p><a href="/mcp">MCP Endpoint</a></p>
        """)

    async def api_tools(request):
        tools = await list_tools()
        return JSONResponse([{"name": t.name, "description": t.description} for t in tools])

    starlette_app = Starlette(routes=[
        Route("/", health),
        Route("/mcp", handle_sse),
        Route("/api/tools", api_tools)
    ])

    config = uvicorn.Config(starlette_app, host="127.0.0.1", port=8201)
    server = uvicorn.Server(config)
    logger.info("Starting Kraliki MCP server on http://127.0.0.1:8201")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
