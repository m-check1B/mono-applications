#!/usr/bin/env python3
"""Agent Monitor - Watches for completed agents and triggers hooks.

This monitor:
1. Polls running_agents.json for registered agents
2. Checks if their PIDs are still running
3. When an agent finishes, parses its log for DARWIN_RESULT
4. Triggers agent_complete hook with status

VD-477: Fix agent_complete hook never being triggered
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

KRALIKI_DIR = Path(__file__).parent.parent
CONTROL_DIR = KRALIKI_DIR / "control"
RUNNING_AGENTS_FILE = CONTROL_DIR / "running_agents.json"
LOGS_DIR = KRALIKI_DIR / "logs" / "agents"

# Add kraliki to path for imports
sys.path.insert(0, str(KRALIKI_DIR))

# Poll interval in seconds
POLL_INTERVAL = 10


def is_pid_running(pid: int) -> bool:
    """Check if a process with given PID is still running."""
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it
        return True


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
    RUNNING_AGENTS_FILE.write_text(json.dumps(data, indent=2))


def parse_darwin_result(log_file: str) -> dict:
    """Parse DARWIN_RESULT from agent log file.

    Expected format:
    DARWIN_RESULT:
      genome: darwin-claude-patcher
      task: VD-123
      status: success
      points_earned: 100

    Returns dict with status and points.
    """
    result = {
        "status": "unknown",
        "task": None,
        "points_earned": 0,
        "genome": None,
    }

    try:
        log_path = Path(log_file)
        if not log_path.exists():
            return result

        content = log_path.read_text()

        # Look for DARWIN_RESULT block
        darwin_match = re.search(
            r'DARWIN_RESULT:?\s*\n((?:\s+\w+:.*\n?)+)',
            content,
            re.IGNORECASE
        )

        if darwin_match:
            block = darwin_match.group(1)

            # Parse individual fields
            status_match = re.search(r'status:\s*(\w+)', block, re.IGNORECASE)
            if status_match:
                result["status"] = status_match.group(1).lower()

            task_match = re.search(r'task:\s*([\w-]+)', block, re.IGNORECASE)
            if task_match:
                result["task"] = task_match.group(1)

            points_match = re.search(r'points_earned:\s*(\d+)', block, re.IGNORECASE)
            if points_match:
                result["points_earned"] = int(points_match.group(1))

            genome_match = re.search(r'genome:\s*([\w-]+)', block, re.IGNORECASE)
            if genome_match:
                result["genome"] = genome_match.group(1)
        else:
            # Fallback: check for common success/failure indicators
            if "error" in content.lower() and "fatal" in content.lower():
                result["status"] = "error"
            elif "+100" in content or "+200" in content or "DONE:" in content:
                result["status"] = "success"
                # Try to extract points
                points_match = re.search(r'\+(\d+)pts', content)
                if points_match:
                    result["points_earned"] = int(points_match.group(1))

    except Exception as e:
        print(f"Error parsing log {log_file}: {e}")

    return result


def trigger_agent_complete(agent_id: str, agent_data: dict, darwin_result: dict):
    """Trigger the agent_complete hook."""
    try:
        from extensions.hooks import trigger_sync

        spawn_time = datetime.fromisoformat(agent_data.get("spawned_at", ""))
        duration_seconds = int((datetime.now() - spawn_time).total_seconds())

        status = darwin_result.get("status", "unknown")

        trigger_sync(
            "agent_complete",
            agent_id=agent_id,
            status=status,
            genome=agent_data.get("genome"),
            cli=agent_data.get("cli"),
            duration_seconds=duration_seconds,
            points=darwin_result.get("points_earned", 0),
            task_id=darwin_result.get("task"),
            log_file=agent_data.get("log_file"),
        )

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Triggered agent_complete for {agent_id}: {status}")

    except Exception as e:
        print(f"Error triggering agent_complete for {agent_id}: {e}")


def check_agents():
    """Check all registered agents and handle completed ones."""
    data = load_running_agents()
    agents = data.get("agents", {})

    if not agents:
        return 0

    completed_count = 0
    agents_to_remove = []

    for agent_id, agent_data in agents.items():
        pid = agent_data.get("pid")
        if not pid:
            continue

        if not is_pid_running(pid):
            # Agent has finished
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent {agent_id} (PID {pid}) has completed")

            # Parse log for result
            log_file = agent_data.get("log_file", "")
            darwin_result = parse_darwin_result(log_file)

            # Trigger completion hook
            trigger_agent_complete(agent_id, agent_data, darwin_result)

            agents_to_remove.append(agent_id)
            completed_count += 1

    # Remove completed agents from registry
    for agent_id in agents_to_remove:
        data["agents"].pop(agent_id, None)

    if agents_to_remove:
        data["last_updated"] = datetime.now().isoformat()
        save_running_agents(data)

    return completed_count


def cleanup_stale_agents(max_age_hours: int = 24):
    """Remove agents that have been running too long (likely stale entries)."""
    data = load_running_agents()
    agents = data.get("agents", {})

    now = datetime.now()
    stale = []

    for agent_id, agent_data in agents.items():
        try:
            spawned_at = datetime.fromisoformat(agent_data.get("spawned_at", ""))
            age_hours = (now - spawned_at).total_seconds() / 3600

            if age_hours > max_age_hours:
                # Also check if PID is still running
                pid = agent_data.get("pid")
                if not is_pid_running(pid):
                    stale.append(agent_id)
                    print(f"Cleaning stale agent {agent_id} (age: {age_hours:.1f}h)")
        except Exception:
            pass

    for agent_id in stale:
        data["agents"].pop(agent_id, None)

    if stale:
        data["last_updated"] = datetime.now().isoformat()
        save_running_agents(data)

    return len(stale)


def main():
    """Main monitoring loop."""
    print(f"Agent Monitor started. Polling every {POLL_INTERVAL}s")
    print(f"Running agents file: {RUNNING_AGENTS_FILE}")

    # Initial cleanup
    stale = cleanup_stale_agents()
    if stale:
        print(f"Cleaned up {stale} stale agents")

    while True:
        try:
            completed = check_agents()
            if completed > 0:
                print(f"Processed {completed} completed agents")
        except KeyboardInterrupt:
            print("\nAgent Monitor stopped")
            break
        except Exception as e:
            print(f"Error in monitor loop: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kraliki Agent Monitor")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--cleanup", action="store_true", help="Only cleanup stale agents")
    parser.add_argument("--status", action="store_true", help="Show current running agents")

    args = parser.parse_args()

    if args.status:
        data = load_running_agents()
        agents = data.get("agents", {})
        print(f"Running agents: {len(agents)}")
        for agent_id, info in agents.items():
            pid = info.get("pid")
            running = "RUNNING" if is_pid_running(pid) else "STOPPED"
            print(f"  {agent_id}: PID {pid} [{running}]")
    elif args.cleanup:
        stale = cleanup_stale_agents()
        print(f"Cleaned {stale} stale agents")
    elif args.once:
        completed = check_agents()
        print(f"Processed {completed} completed agents")
    else:
        main()
