#!/usr/bin/env python3
"""
Kraliki Swarm Operations Monitor
Runs every 20 minutes to detect anomalies and file Linear issues
"""

import json
import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
KRALIKI_DIR = Path(__file__).resolve().parent.parent
ALERTS_FILE = KRALIKI_DIR / "logs" / "kraliki-alerts.json"
STATE_FILE = KRALIKI_DIR / "control" / "kraliki-monitor-state.json"
HEALTH_ALERTS_FILE = KRALIKI_DIR / "logs" / "health-alerts.json"
BOARD_FILE = KRALIKI_DIR / "arena" / "data" / "board.json"
RUNNING_AGENTS_FILE = KRALIKI_DIR / "control" / "running_agents.json"
MONITOR_LOG = KRALIKI_DIR / "logs" / "kraliki-monitor.log"
LINEAR_SYNC_ISSUE = "VD-551"  # Known Linear API issue
RESTART_LOOP_PAUSE_FILE = KRALIKI_DIR / "control" / "restart_loop_paused.json"

# Thresholds
MAX_RESTARTS = 3
MAX_CPU_PERCENT = 80
MAX_MEM_MB = 500
MIN_AGENTS = 3
CHECK_WINDOW_MINUTES = 20
RESTART_LOOP_PAUSE_DURATION = 3600  # 1 hour in seconds


def pause_restart_loop_process(process_name: str) -> bool:
    """Pause a process that's in a restart loop."""
    try:
        # Check if already paused
        paused = load_paused_processes()
        if process_name in paused:
            return False

        # Stop the process
        subprocess.run(["pm2", "stop", process_name], timeout=10, capture_output=True)

        # Record pause
        paused[process_name] = datetime.now().isoformat()
        RESTART_LOOP_PAUSE_FILE.write_text(json.dumps(paused, indent=2))

        # Post to blackboard
        subprocess.run(
            [
                "python3",
                str(KRALIKI_DIR / "arena" / "blackboard.py"),
                "SYSTEM",
                f"RESTART_LOOP: Paused {process_name} due to excessive restarts. Auto-resume in 1 hour.",
                "-t",
                "alerts",
            ],
            timeout=10,
            capture_output=True,
        )

        return True
    except Exception as e:
        log(f"Failed to pause {process_name}: {e}", "ERROR")
        return False


def load_paused_processes() -> Dict:
    """Load list of processes paused due to restart loops."""
    if RESTART_LOOP_PAUSE_FILE.exists():
        try:
            return json.loads(RESTART_LOOP_PAUSE_FILE.read_text())
        except Exception:
            pass
    return {}


def resume_paused_processes():
    """Resume processes that were paused for restart loops."""
    paused = load_paused_processes()
    now = datetime.now()

    to_resume = []
    for proc_name, paused_at in paused.items():
        try:
            paused_dt = datetime.fromisoformat(paused_at)
            elapsed_seconds = (now - paused_dt).total_seconds()

            if elapsed_seconds > RESTART_LOOP_PAUSE_DURATION:
                to_resume.append(proc_name)
        except Exception as e:
            log(f"Failed to parse paused time for {proc_name}: {e}", "ERROR")

    for proc_name in to_resume:
        try:
            subprocess.run(["pm2", "start", proc_name], timeout=10, capture_output=True)
            del paused[proc_name]

            subprocess.run(
                [
                    "python3",
                    str(KRALIKI_DIR / "arena" / "blackboard.py"),
                    "SYSTEM",
                    f"RESTART_LOOP: Resumed {proc_name} after 1 hour pause.",
                    "-t",
                    "alerts",
                ],
                timeout=10,
                capture_output=True,
            )

            log(f"Resumed paused process: {proc_name}", "INFO")
        except Exception as e:
            log(f"Failed to resume {proc_name}: {e}", "ERROR")

    if to_resume:
        RESTART_LOOP_PAUSE_FILE.write_text(json.dumps(paused, indent=2))


def log(msg: str, level: str = "INFO"):
    """Log to file and stdout"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}\n"
    print(line, end="")
    MONITOR_LOG.open("a").write(line)


def load_state() -> dict:
    """Load previous monitoring state"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_check": None, "pm2_state": {}, "agent_count": 0, "issues_created": []}


def save_state(state: dict):
    """Save monitoring state"""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_pm2_status() -> Dict:
    """Get PM2 process status"""
    try:
        result = subprocess.run(
            ["pm2", "jlist"], capture_output=True, text=True, timeout=10
        )
        processes = json.loads(result.stdout)
        return {
            "total": len(processes),
            "online": sum(
                1 for p in processes if p.get("pm2_env", {}).get("status") == "online"
            ),
            "stopped": sum(
                1 for p in processes if p.get("pm2_env", {}).get("status") == "stopped"
            ),
            "errored": sum(
                1 for p in processes if p.get("pm2_env", {}).get("status") == "errored"
            ),
            "processes": processes,
        }
    except Exception as e:
        log(f"Failed to get PM2 status: {e}", "ERROR")
        return {"error": str(e), "processes": []}


def check_pm2_anomalies(pm2_status: Dict, prev_state: Dict) -> List[str]:
    """Check for PM2 process anomalies"""
    anomalies = []
    prev_pm2 = prev_state.get("pm2_state", {})

    # Check for stopped processes that should be running
    if "processes" in pm2_status:
        for proc in pm2_status["processes"]:
            name = proc.get("name", "unknown")
            status = proc.get("pm2_env", {}).get("status", "unknown")
            restarts = proc.get("pm2_env", {}).get("restart_time", 0)
            pid = proc.get("pid", 0)

            # Kraliki services that should always be online
            critical_services = [
                "kraliki-health",
                "kraliki-agent-board",
                "kraliki-comm",
                "kraliki-comm-ws",
                "kraliki-linear-sync",
                "kraliki-events-bridge",
                "kraliki-mcp",
            ]

            if name in critical_services and status != "online":
                anomalies.append(f"CRITICAL: {name} is {status} (should be online)")

            # Check for excessive restarts
            if restarts > MAX_RESTARTS:
                prev_restarts = 0
                if prev_pm2.get("processes"):
                    for p in prev_pm2["processes"]:
                        if p.get("name") == name:
                            prev_restarts = p.get("pm2_env", {}).get("restart_time", 0)
                            break

                if restarts - prev_restarts > MAX_RESTARTS:
                    anomaly_msg = f"WARNING: {name} restarted {restarts - prev_restarts} times (threshold: {MAX_RESTARTS})"
                    anomalies.append(anomaly_msg)

                    # Auto-pause if excessive restarts (> 10 in one check)
                    if restarts - prev_restarts > 10:
                        if pause_restart_loop_process(name):
                            anomalies.append(
                                f"ACTION: Paused {name} due to restart loop ({restarts - prev_restarts} restarts in {CHECK_WINDOW_MINUTES}min)"
                            )

    # Check total process count
    if pm2_status.get("online", 0) < 20:
        anomalies.append(
            f"WARNING: Only {pm2_status.get('online')} PM2 processes online (expected ~20+)"
        )

    return anomalies


def check_agent_activity(state: Dict) -> List[str]:
    """Check agent activity and count"""
    anomalies = []

    # Check running agents
    if RUNNING_AGENTS_FILE.exists():
        try:
            running = json.loads(RUNNING_AGENTS_FILE.read_text())
            agent_count = len(running.get("agents", {}))

            if agent_count < MIN_AGENTS:
                anomalies.append(
                    f"WARNING: Only {agent_count} agents running (minimum: {MIN_AGENTS})"
                )

            # Check for stale agents (older than 2 hours)
            now = datetime.now()
            for name, info in running.get("agents", {}).items():
                spawned_at = info.get("spawned_at", "")
                if spawned_at:
                    try:
                        age = (now - datetime.fromisoformat(spawned_at)).total_seconds()
                        if age > 7200:  # 2 hours
                            anomalies.append(
                                f"WARNING: Agent {name} has been running for {age / 60:.0f} minutes"
                            )
                    except ValueError:
                        pass
        except Exception as e:
            log(f"Failed to check running agents: {e}", "ERROR")

    return anomalies


def check_health_alerts(prev_state: Dict) -> List[str]:
    """Check health alert log for new issues"""
    anomalies = []

    if not HEALTH_ALERTS_FILE.exists():
        return anomalies

    try:
        alerts = json.loads(HEALTH_ALERTS_FILE.read_text())
        last_check = prev_state.get("last_check")

        if last_check:
            try:
                last_check_dt = datetime.fromisoformat(last_check)
                new_alerts = [
                    a
                    for a in alerts
                    if datetime.fromisoformat(a["timestamp"]) > last_check_dt
                ]

                if new_alerts:
                    # Count alert types
                    alert_types = {}
                    for alert in new_alerts:
                        msg = alert.get("message", "")
                        if "stopped" in msg:
                            alert_types["stopped"] = alert_types.get("stopped", 0) + 1
                        elif "waiting restart" in msg:
                            alert_types["restart_loop"] = (
                                alert_types.get("restart_loop", 0) + 1
                            )

                    for alert_type, count in alert_types.items():
                        anomalies.append(
                            f"HEALTH ALERT: {count} {alert_type} event(s) since last check"
                        )
            except ValueError:
                pass
    except Exception as e:
        log(f"Failed to check health alerts: {e}", "ERROR")

    return anomalies


def check_blackboard_activity() -> List[str]:
    """Check blackboard for activity"""
    anomalies = []

    if not BOARD_FILE.exists():
        return anomalies

    try:
        board = json.loads(BOARD_FILE.read_text())
        channels = board.get("channels", {})

        # Check last activity
        for channel_name, channel_data in channels.items():
            last_message = channel_data.get("last_message", "")
            if last_message:
                try:
                    last_time = datetime.fromisoformat(last_message)
                    age_minutes = (datetime.now() - last_time).total_seconds() / 60

                    # Critical channels should have recent activity
                    critical_channels = ["events", "critical", "alerts"]
                    if channel_name in critical_channels and age_minutes > 30:
                        anomalies.append(
                            f"WARNING: No activity on critical channel '{channel_name}' for {age_minutes:.0f} minutes"
                        )
                except ValueError:
                    pass
    except Exception as e:
        log(f"Failed to check blackboard: {e}", "ERROR")

    return anomalies


def file_linear_issue(title: str, description: str, labels: List[str]) -> Optional[str]:
    """File an issue in Linear using CLI"""
    try:
        # Try using gh command or Linear CLI if available
        # For now, just log it
        log(f"WOULD FILE LINEAR ISSUE: {title}", "INFO")
        log(f"  Description: {description}", "INFO")
        log(f"  Labels: {', '.join(labels)}", "INFO")
        return None
    except Exception as e:
        log(f"Failed to file Linear issue: {e}", "ERROR")
        return None


def main():
    """Main monitoring loop"""
    now = datetime.now()
    state = load_state()

    log("Starting Kraliki Swarm operations monitor check", "INFO")

    anomalies = []

    # Resume any paused processes that have completed their pause duration
    resume_paused_processes()

    # Check PM2 status
    pm2_status = get_pm2_status()
    anomalies.extend(check_pm2_anomalies(pm2_status, state))

    # Check agent activity
    anomalies.extend(check_agent_activity(state))

    # Check health alerts
    anomalies.extend(check_health_alerts(state))

    # Check blackboard
    anomalies.extend(check_blackboard_activity())

    # Report findings
    if anomalies:
        log(f"Found {len(anomalies)} anomaly(s):", "WARN")
        for anomaly in anomalies:
            log(f"  - {anomaly}", "WARN")

        # Aggregate and file critical issues
        critical = [a for a in anomalies if "CRITICAL" in a]
        if critical:
            summary = "\n".join(critical)
            file_linear_issue(
                f"Kraliki Swarm Critical Alert - {now.strftime('%Y-%m-%d %H:%M')}",
                f"Critical anomalies detected:\n\n{summary}",
                ["kraliki-swarm", "critical", "monitoring"],
            )
    else:
        log("No anomalies detected", "INFO")

    # Update state
    state["last_check"] = now.isoformat()
    state["pm2_state"] = pm2_status
    save_state(state)

    log("Monitoring check complete", "INFO")


if __name__ == "__main__":
    main()
