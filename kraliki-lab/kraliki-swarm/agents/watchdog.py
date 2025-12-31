#!/usr/bin/env python3
"""Kraliki Watchdog.

Keeps the swarm alive by:
1. Monitoring active agent count
2. Spawning new agents when count drops below threshold
3. Checking API quotas and circuit breakers
4. Posting heartbeats to social feed

Runs as a PM2-managed process.
"""

import subprocess
import sys
import os
import json
import time
import random
import re
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

KRALIKI_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(KRALIKI_DIR))
from control import cli_policy
CONTROL_DIR = KRALIKI_DIR / "control"
ARENA_DIR = KRALIKI_DIR / "arena"
GENOMES_DIR = KRALIKI_DIR / "genomes"
LOGS_DIR = KRALIKI_DIR / "logs" / "agents"
ORCHESTRATOR_STATE_FILE = CONTROL_DIR / "orchestrator_state.json"

# Configuration
MIN_AGENTS = 3
MAX_AGENTS = 8
CHECK_INTERVAL = 300  # 5 minutes
HEARTBEAT_INTERVAL = 1800  # 30 minutes
ORCHESTRATOR_MAX_AGE = 43200  # 12 hours - consider orchestrator stale after this
ORCHESTRATOR_LOG_GRACE_MINUTES = 60
DEFAULT_CLI_ORDER = ["claude", "opencode", "codex", "gemini"]
STALE_AGENT_THRESHOLD_SECONDS = 7200  # 2 hours
STALE_SWEEP_INTERVAL = 900  # 15 minutes
STALE_AGENT_RE = re.compile(
    r"(Kraliki agent|claude.*append-system-prompt|codex exec|codex.*full-auto|gemini.*-p|opencode run.*--print-logs)",
    re.IGNORECASE,
)

# Track last heartbeat
last_heartbeat = 0
last_stale_sweep = 0


def load_cli_policy() -> dict:
    """Load CLI policy from dashboard config."""
    return cli_policy.load_cli_policy()


def load_pause_state() -> dict:
    """Load pause state from dashboard config."""
    return cli_policy.load_pause_state()


def is_cli_enabled(cli: str, policy: Optional[dict] = None) -> bool:
    """Check if CLI is enabled by policy."""
    return cli_policy.is_cli_enabled(cli, policy=policy)


def get_policy_priority_order(policy: dict) -> list:
    """Derive CLI priority order from policy (lower number = higher priority)."""
    entries = []
    for idx, cli in enumerate(DEFAULT_CLI_ORDER):
        priority = policy.get("clis", {}).get(cli, {}).get("priority")
        if priority is None:
            priority = idx + 100
        entries.append((priority, idx, cli))
    entries.sort()
    return [cli for _, _, cli in entries]


def get_policy_disabled_clis(policy: dict) -> set:
    """Return set of CLIs disabled by policy."""
    disabled = set()
    for cli in DEFAULT_CLI_ORDER:
        if not is_cli_enabled(cli, policy):
            disabled.add(cli)
    return disabled


def is_swarm_paused() -> bool:
    """Check if swarm is paused via dashboard."""
    return cli_policy.is_swarm_paused()


def find_stale_agents() -> list:
    """Find stale agent processes by runtime."""
    stale = []
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,etimes,args"],
            capture_output=True,
            text=True,
        )
        if not result.stdout:
            return stale

        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            if "watchdog" in line.lower():
                continue
            if not STALE_AGENT_RE.search(line):
                continue

            parts = line.strip().split(maxsplit=2)
            if len(parts) < 3:
                continue
            try:
                pid = int(parts[0])
                runtime = int(parts[1])
            except ValueError:
                continue
            if runtime > STALE_AGENT_THRESHOLD_SECONDS:
                stale.append({"pid": pid, "runtime": runtime, "command": parts[2]})
    except Exception:
        pass
    return stale


def kill_process(pid: int) -> bool:
    """Terminate a process gracefully, then force kill if needed."""
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return False
    except Exception:
        return False

    time.sleep(1)
    try:
        os.kill(pid, 0)
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except Exception:
        return False
    return True


def sweep_stale_agents():
    """Periodically kill stale agents to avoid stuck processes."""
    global last_stale_sweep
    now = time.time()
    if now - last_stale_sweep < STALE_SWEEP_INTERVAL:
        return
    last_stale_sweep = now

    stale_agents = find_stale_agents()
    if not stale_agents:
        return

    killed = 0
    for agent in stale_agents:
        if kill_process(agent["pid"]):
            killed += 1

    if killed:
        print(f"[WATCHDOG] Killed {killed} stale agent(s)")


def is_process_alive(pid: int) -> bool:
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)  # Signal 0 just checks if process exists
        return True
    except (OSError, ProcessLookupError):
        return False


def load_orchestrator_state() -> dict:
    """Load orchestrator state from file."""
    if ORCHESTRATOR_STATE_FILE.exists():
        try:
            return json.loads(ORCHESTRATOR_STATE_FILE.read_text())
        except Exception:
            pass
    return {"pid": None, "agent_id": None, "spawned_at": None, "genome": None}


def save_orchestrator_state(pid: int, agent_id: str, genome: str):
    """Save orchestrator state to file."""
    state = {
        "pid": pid,
        "agent_id": agent_id,
        "genome": genome,
        "spawned_at": datetime.now().isoformat()
    }
    ORCHESTRATOR_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ORCHESTRATOR_STATE_FILE.write_text(json.dumps(state, indent=2))


def check_orchestrator_running() -> bool:
    """Check if an orchestrator is currently running.

    Uses multiple signals:
    1. State file with PID - check if process is alive
    2. Recent orchestrator log activity (within last 10 minutes)
    3. Fallback to pgrep for any claude/gemini/codex processes
    """
    stale_pid = None
    stale_age_minutes = None

    # Method 1: Check saved orchestrator state
    state = load_orchestrator_state()
    if state.get("pid"):
        pid = state["pid"]
        if is_process_alive(pid):
            # Check if not too old (stale orchestrator)
            spawned_at = state.get("spawned_at")
            if spawned_at:
                try:
                    spawn_time = datetime.fromisoformat(spawned_at)
                    age_seconds = (datetime.now() - spawn_time).total_seconds()
                    if age_seconds < ORCHESTRATOR_MAX_AGE:
                        print(f"[WATCHDOG] Orchestrator {state.get('agent_id')} (PID {pid}) is alive")
                        return True
                    else:
                        stale_pid = pid
                        stale_age_minutes = age_seconds / 60
                        print(f"[WATCHDOG] Orchestrator {state.get('agent_id')} is stale ({stale_age_minutes:.0f} min old)")
                except Exception:
                    pass
            else:
                print(f"[WATCHDOG] Orchestrator {state.get('agent_id')} (PID {pid}) is alive")
                return True

    # Method 2: Check for recent orchestrator log activity
    try:
        now = datetime.now()
        log_window_minutes = ORCHESTRATOR_LOG_GRACE_MINUTES if stale_pid else 10
        for log_file in LOGS_DIR.glob("*-orchestrator-*.log"):
            # Check if log was modified in last 10 minutes
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age_minutes = (now - mtime).total_seconds() / 60
            if age_minutes < log_window_minutes:
                # Check log size - active orchestrators write output
                if log_file.stat().st_size > 100:
                    print(f"[WATCHDOG] Found active orchestrator log: {log_file.name} ({age_minutes:.1f} min ago)")
                    return True
    except Exception as e:
        print(f"[WATCHDOG] Error checking logs: {e}")

    # Method 3: Check for any running CLI processes (fallback)
    try:
        # Look for claude/gemini/codex processes that might be orchestrators
        result = subprocess.run(
            ["pgrep", "-af", "(claude|gemini|codex|opencode)"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            # Filter out this watchdog's own spawned processes that just started
            for line in lines:
                if "orchestrator" in line.lower() or "AGENT_ID" in line:
                    print(f"[WATCHDOG] Found orchestrator process: {line[:80]}")
                    return True
    except Exception:
        pass

    if stale_pid:
        print(f"[WATCHDOG] Orchestrator stale by age; keeping PID {stale_pid} to avoid duplicate spawns")
        return True

    return False


def count_active_agents() -> int:
    """Count currently running agent processes."""
    count = 0
    try:
        # Check for processes matching any of our supported CLI tools in Kraliki context
        cli_patterns = ["claude", "opencode", "gemini", "codex", "grok"]
        pattern = "|".join(cli_patterns)
        
        result = subprocess.run(
            ["pgrep", "-f", f"({pattern}).*kraliki"],
            capture_output=True,
            text=True,
        )
        count += len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

    except Exception:
        pass

    return count


def get_blocked_clis() -> set:
    """Get set of blocked CLIs from circuit breakers."""
    blocked = set()
    cb_file = CONTROL_DIR / "circuit-breakers.json"
    if not cb_file.exists():
        return blocked

    try:
        data = json.loads(cb_file.read_text())
        for name, state in data.items():
            if state.get("state") == "open":
                # Extract CLI name from key (e.g., "claude_cli" -> "claude")
                if name.endswith("_cli"):
                    blocked.add(name.replace("_cli", ""))
    except Exception:
        pass
    
    return blocked


def open_cli_circuit(cli: str, reason: str):
    """Open circuit breaker for a CLI to prevent repeated spawn failures."""
    cb_file = CONTROL_DIR / "circuit-breakers.json"
    now = datetime.now().isoformat()
    data = {}

    if cb_file.exists():
        try:
            data = json.loads(cb_file.read_text())
        except Exception:
            data = {}

    key = f"{cli}_cli"
    entry = data.get(key, {})
    entry["state"] = "open"
    entry["last_update"] = now
    entry["last_failure_time"] = now
    entry["last_failure_reason"] = reason
    entry["failure_count"] = int(entry.get("failure_count", 0)) + 1
    data[key] = entry

    try:
        cb_file.write_text(json.dumps(data, indent=2))
        print(f"[WATCHDOG] Circuit breaker OPEN for {cli}: {reason}")
    except Exception as e:
        print(f"[WATCHDOG] Failed to update circuit breaker for {cli}: {e}")


def get_cli_from_genome(genome_path: Path) -> str:
    """Extract CLI tool from genome content."""
    try:
        content = genome_path.read_text()
        for line in content.split("\n"):
            if line.startswith("cli:"):
                return line.split(":")[1].strip()
    except Exception:
        pass
        
    # Default based on filename
    name = genome_path.stem
    if "claude" in name: return "claude"
    elif "opencode" in name: return "opencode"
    elif "gemini" in name: return "gemini"
    elif "codex" in name: return "codex"
    return "claude"


def get_available_genomes(blocked_clis: set) -> list:
    """Get list of genome names that can be spawned, filtering out blocked CLIs."""
    blocked_clis = blocked_clis or set()
    if blocked_clis:
        print(f"[WATCHDOG] Blocked CLIs: {blocked_clis}")

    genomes = []
    for f in GENOMES_DIR.glob("*.md"):
        cli = get_cli_from_genome(f)
        if cli not in blocked_clis:
            genomes.append(f.stem)
            
    return genomes


def spawn_agent(genome_name: str) -> dict:
    """Spawn an agent using the spawn.py script."""
    spawn_script = KRALIKI_DIR / "agents" / "spawn.py"

    try:
        result = subprocess.run(
            ["python3", str(spawn_script), genome_name],
            capture_output=True,
            text=True,
            cwd=str(KRALIKI_DIR),
        )
        
        stdout = result.stdout.strip()
        
        if result.returncode == 0:
            print(f"[WATCHDOG] Spawned: {genome_name}")

            # Try to extract JSON from stdout (might have warnings before it)
            spawn_result = {"success": True}
            try:
                # Find the first '{' and last '}'
                start = stdout.find('{')
                end = stdout.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = stdout[start:end]
                    spawn_result = json.loads(json_str)
                else:
                    spawn_result = json.loads(stdout)
            except Exception as e:
                print(f"[WATCHDOG] Warning: Could not parse spawn output as JSON: {e}")
                # Fallback if it didn't output JSON but returncode was 0

            # If this was an orchestrator, save state for tracking
            if "orchestrator" in genome_name and spawn_result.get("success"):
                try:
                    save_orchestrator_state(
                        pid=spawn_result.get("pid"),
                        agent_id=spawn_result.get("agent_id"),
                        genome=genome_name
                    )
                    if spawn_result.get("pid"):
                        print(f"[WATCHDOG] Saved orchestrator state: PID {spawn_result.get('pid')}")
                except Exception as e:
                    print(f"[WATCHDOG] Could not save orchestrator state: {e}")

            return spawn_result
        else:
            print(f"[WATCHDOG] Failed to spawn {genome_name}: {result.stderr}")
            return {"success": False, "error": result.stderr}
    except Exception as e:
        print(f"[WATCHDOG] Error spawning {genome_name}: {e}")
        return {"success": False, "error": str(e)}


def post_heartbeat(agent_count: int):
    """Post heartbeat to social feed."""
    global last_heartbeat

    now = time.time()
    if now - last_heartbeat < HEARTBEAT_INTERVAL:
        return

    try:
        sys.path.insert(0, str(ARENA_DIR))
        from social import post

        timestamp = datetime.now().strftime("%H:%M")
        post(
            f"[{timestamp}] Heartbeat: {agent_count} agents active. System healthy.",
            author="kraliki-watchdog",
        )
        last_heartbeat = now
        print(f"[WATCHDOG] Posted heartbeat")
    except Exception as e:
        print(f"[WATCHDOG] Failed to post heartbeat: {e}")


def run_cycle():
    """Run one watchdog cycle."""
    print(f"[WATCHDOG] Cycle start: {datetime.now().isoformat()}")

    sweep_stale_agents()

    if is_swarm_paused():
        print("[WATCHDOG] Swarm paused via dashboard. Standing by.")
        return

    policy = load_cli_policy()
    policy_disabled = get_policy_disabled_clis(policy)
    if policy_disabled:
        print(f"[WATCHDOG] Policy disabled CLIs: {policy_disabled}")

    # 1. Check for Running Orchestrator using improved detection
    has_orchestrator = check_orchestrator_running()

    if has_orchestrator:
        print("[WATCHDOG] Orchestrator is running. Standing by.")
        # Post heartbeat periodically
        post_heartbeat(count_active_agents())
        return

    print("[WATCHDOG] No Orchestrator found! Initiating rescue...")

    # 2. Find Available Orchestrator Genomes (Respecting Circuit Breakers)
    blocked_clis = get_blocked_clis().union(policy_disabled)
    available_genomes = get_available_genomes(blocked_clis)
    orchestrator_genomes = [g for g in available_genomes if "orchestrator" in g]

    if not orchestrator_genomes:
        print("[WATCHDOG] CRITICAL: No Orchestrator genomes available (all blocked?).")
        return

    # 3. Try each CLI in priority order with fallback
    # If one fails, try the next. Don't give up until all tried.
    priority_order = get_policy_priority_order(policy)

    for cli in priority_order:
        if cli in blocked_clis:
            continue
        # Find orchestrator genome for this CLI
        genome = None
        for g in orchestrator_genomes:
            if cli in g:
                genome = g
                break

        if not genome:
            continue

        print(f"[WATCHDOG] Trying Orchestrator: {genome}")
        result = spawn_agent(genome)

        if not result.get("success"):
            print(f"[WATCHDOG] {genome} spawn failed, trying next...")
            continue

        # Wait and verify agent actually started working
        pid = result.get("pid")
        log_file = result.get("log_file")

        if pid and log_file:
            time.sleep(5)  # Give agent time to fail if it will

            # Check if process still alive
            if is_process_alive(pid):
                print(f"[WATCHDOG] {genome} started successfully (PID {pid})")
                return  # Success!
            else:
                print(f"[WATCHDOG] {genome} died immediately, trying next...")
                open_cli_circuit(cli, f"{genome} exited immediately after spawn")
                continue

        # If we got here, spawn seemed to work
        return

    print("[WATCHDOG] CRITICAL: All orchestrator CLIs failed!")


def main():
    print(f"[WATCHDOG] Kraliki Watchdog starting...")
    print(f"[WATCHDOG] MIN_AGENTS={MIN_AGENTS}, CHECK_INTERVAL={CHECK_INTERVAL}s")

    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"[WATCHDOG] Error in cycle: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
