#!/usr/bin/env python3
"""Per-CLI Watchdog.

Independent watchdog for a single CLI. Each CLI runs its own instance.
No coupling between CLIs - if Claude is down, OpenCode keeps working.

Usage:
    python3 watchdog_cli.py claude
    python3 watchdog_cli.py opencode
    python3 watchdog_cli.py gemini
    python3 watchdog_cli.py codex
"""

import subprocess
import sys
import os
import json
import time
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

# Configuration
CHECK_INTERVAL = 300  # 5 minutes
HEARTBEAT_INTERVAL = 1800  # 30 minutes
ORCHESTRATOR_MAX_AGE = 43200  # 12 hours
ORCHESTRATOR_LOG_GRACE_MINUTES = 60

# Track state
last_heartbeat = 0


def load_cli_policy() -> dict:
    """Load CLI policy from dashboard config."""
    return cli_policy.load_cli_policy()


def load_pause_state() -> dict:
    """Load pause state from dashboard config."""
    return cli_policy.load_pause_state()


def is_cli_enabled(cli: str, policy: Optional[dict] = None) -> bool:
    """Check if CLI is enabled by policy."""
    return cli_policy.is_cli_enabled(cli, policy=policy)


def is_swarm_paused() -> bool:
    """Check if swarm is paused via dashboard."""
    return cli_policy.is_swarm_paused()


def get_cli_name() -> str:
    """Get CLI name from command line argument."""
    if len(sys.argv) < 2:
        print("Usage: python3 watchdog_cli.py <cli_name>")
        print("  cli_name: claude | opencode | gemini | codex")
        sys.exit(1)

    cli = sys.argv[1].lower()
    valid_clis = ["claude", "opencode", "gemini", "codex"]

    if cli not in valid_clis:
        print(f"Invalid CLI: {cli}")
        print(f"Valid options: {valid_clis}")
        sys.exit(1)

    return cli


def state_file(cli: str) -> Path:
    """Get state file path for this CLI's orchestrator."""
    return CONTROL_DIR / f"orchestrator_state_{cli}.json"


def is_process_alive(pid: int) -> bool:
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def load_orchestrator_state(cli: str) -> dict:
    """Load orchestrator state for this CLI."""
    sf = state_file(cli)
    if sf.exists():
        try:
            return json.loads(sf.read_text())
        except Exception:
            pass
    return {"pid": None, "agent_id": None, "spawned_at": None}


def save_orchestrator_state(cli: str, pid: int, agent_id: str):
    """Save orchestrator state for this CLI."""
    state = {
        "pid": pid,
        "agent_id": agent_id,
        "cli": cli,
        "spawned_at": datetime.now().isoformat()
    }
    sf = state_file(cli)
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(json.dumps(state, indent=2))


def is_cli_blocked(cli: str) -> bool:
    """Check if this CLI is blocked by circuit breaker."""
    cb_file = CONTROL_DIR / "circuit-breakers.json"
    if not cb_file.exists():
        return False

    try:
        data = json.loads(cb_file.read_text())
        key = f"{cli}_cli"
        if key in data and data[key].get("state") == "open":
            return True
    except Exception:
        pass

    return False


def check_orchestrator_running(cli: str) -> bool:
    """Check if this CLI's orchestrator is running."""
    tag = f"[WATCHDOG-{cli.upper()}]"
    stale_pid = None
    stale_age_minutes = None

    # Method 1: Check saved state
    state = load_orchestrator_state(cli)
    if state.get("pid"):
        pid = state["pid"]
        if is_process_alive(pid):
            spawned_at = state.get("spawned_at")
            if spawned_at:
                try:
                    spawn_time = datetime.fromisoformat(spawned_at)
                    age_seconds = (datetime.now() - spawn_time).total_seconds()
                    if age_seconds < ORCHESTRATOR_MAX_AGE:
                        print(f"{tag} Orchestrator {state.get('agent_id')} (PID {pid}) alive")
                        return True
                    else:
                        stale_pid = pid
                        stale_age_minutes = age_seconds / 60
                        print(f"{tag} Orchestrator stale ({stale_age_minutes:.0f} min) - verifying activity")
                except Exception:
                    pass
            else:
                print(f"{tag} Orchestrator {state.get('agent_id')} (PID {pid}) alive")
                return True

    # Method 2: Check recent log activity
    try:
        now = datetime.now()
        log_window_minutes = ORCHESTRATOR_LOG_GRACE_MINUTES if stale_pid else 10
        # Look for logs matching this CLI's orchestrator pattern
        patterns = [
            f"*{cli}*orchestrator*.log",
            f"*-orchestrator-*.log"  # Fallback pattern
        ]

        for pattern in patterns:
            for log_file in LOGS_DIR.glob(pattern):
                # Must be for this CLI
                if cli not in log_file.name.lower() and "orchestrator" not in log_file.name.lower():
                    continue

                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                age_minutes = (now - mtime).total_seconds() / 60

                if age_minutes < log_window_minutes and log_file.stat().st_size > 100:
                    # Verify it's for this CLI by checking content or name
                    if cli in log_file.name.lower():
                        print(f"{tag} Found active log: {log_file.name} ({age_minutes:.1f} min ago)")
                        if stale_pid:
                            print(f"{tag} Stale by age but active logs detected; keeping PID {stale_pid}")
                        return True
    except Exception as e:
        print(f"{tag} Error checking logs: {e}")

    # Method 3: pgrep for this specific CLI
    try:
        result = subprocess.run(
            ["pgrep", "-af", f"{cli}.*kraliki"],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                if "orchestrator" in line.lower():
                    print(f"{tag} Found process: {line[:80]}")
                    return True
    except Exception:
        pass

    if stale_pid:
        print(f"{tag} Orchestrator stale ({stale_age_minutes:.0f} min) with no recent logs - KILLING PID {stale_pid}")
        try:
            os.kill(stale_pid, 9)  # SIGKILL
            print(f"{tag} Killed stale orchestrator PID {stale_pid}")
        except Exception as e:
            print(f"{tag} Failed to kill PID {stale_pid}: {e}")
        state_file(cli).unlink(missing_ok=True)

    return False


def get_orchestrator_genome(cli: str) -> str | None:
    """Get the orchestrator genome name for this CLI."""
    # Try common patterns
    patterns = [
        f"{cli}_orchestrator",
        f"darwin-{cli}-orchestrator",
        f"{cli}-orchestrator"
    ]

    for pattern in patterns:
        genome_file = GENOMES_DIR / f"{pattern}.md"
        if genome_file.exists():
            return pattern

    # Fallback: search for any orchestrator genome for this CLI
    for f in GENOMES_DIR.glob("*orchestrator*.md"):
        if cli in f.stem.lower():
            return f.stem

    return None


def spawn_orchestrator(cli: str, genome: str) -> dict:
    """Spawn the orchestrator for this CLI."""
    tag = f"[WATCHDOG-{cli.upper()}]"
    spawn_script = KRALIKI_DIR / "agents" / "spawn.py"

    try:
        result = subprocess.run(
            ["python3", str(spawn_script), genome],
            capture_output=True,
            text=True,
            cwd=str(KRALIKI_DIR),
        )

        if result.returncode == 0:
            print(f"{tag} Spawned: {genome}")

            # Parse spawn result robustly
            stdout = result.stdout.strip()
            spawn_result = {"success": True}
            try:
                # Find the first '{' and last '}' to extract JSON block
                start = stdout.find('{')
                end = stdout.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = stdout[start:end]
                    spawn_result = json.loads(json_str)
                else:
                    spawn_result = json.loads(stdout)
                
                if spawn_result.get("success"):
                    save_orchestrator_state(
                        cli=cli,
                        pid=spawn_result.get("pid"),
                        agent_id=spawn_result.get("agent_id")
                    )
                    return spawn_result
            except Exception as e:
                print(f"{tag} Warning: Could not parse spawn output as JSON: {e}")

            return spawn_result
        else:
            print(f"{tag} Failed to spawn: {result.stderr}")
            return {"success": False, "error": result.stderr}

    except Exception as e:
        print(f"{tag} Error spawning: {e}")
        return {"success": False, "error": str(e)}


def post_heartbeat(cli: str):
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
            f"[{timestamp}] {cli.upper()} watchdog: orchestrator healthy",
            author=f"watchdog-{cli}",
        )
        last_heartbeat = now
    except Exception:
        pass


def run_cycle(cli: str):
    """Run one watchdog cycle for this CLI."""
    tag = f"[WATCHDOG-{cli.upper()}]"
    print(f"{tag} Cycle start: {datetime.now().isoformat()}")

    if is_swarm_paused():
        print(f"{tag} Swarm paused via dashboard. Standing by.")
        return

    policy = load_cli_policy()
    if not is_cli_enabled(cli, policy):
        reason = policy.get("clis", {}).get(cli, {}).get("reason")
        reason_note = f" ({reason})" if reason else ""
        print(f"{tag} CLI disabled by policy{reason_note}. Standing by.")
        return

    # Check if CLI is blocked by circuit breaker
    if is_cli_blocked(cli):
        print(f"{tag} CLI blocked by circuit breaker. Sleeping.")
        return

    # Check if orchestrator is running
    if check_orchestrator_running(cli):
        print(f"{tag} Orchestrator running. Standing by.")
        post_heartbeat(cli)
        return

    print(f"{tag} No orchestrator found! Spawning...")

    # Find orchestrator genome for this CLI
    genome = get_orchestrator_genome(cli)
    if not genome:
        print(f"{tag} CRITICAL: No orchestrator genome found for {cli}")
        return

    # Spawn orchestrator
    result = spawn_orchestrator(cli, genome)

    if not result.get("success"):
        print(f"{tag} Spawn failed: {result.get('error')}")
        return

    # Verify it's alive after brief wait
    pid = result.get("pid")
    if pid:
        time.sleep(5)
        if is_process_alive(pid):
            print(f"{tag} Orchestrator started successfully (PID {pid})")
        else:
            print(f"{tag} Orchestrator died immediately")


def main():
    cli = get_cli_name()
    tag = f"[WATCHDOG-{cli.upper()}]"

    print(f"{tag} Starting independent watchdog for {cli}")
    print(f"{tag} CHECK_INTERVAL={CHECK_INTERVAL}s")

    while True:
        try:
            run_cycle(cli)
        except Exception as e:
            print(f"{tag} Error in cycle: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
