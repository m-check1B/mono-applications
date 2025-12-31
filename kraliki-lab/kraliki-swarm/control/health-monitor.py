#!/usr/bin/env python3
"""
Health Monitor - Checks bot health endpoints and sends alerts
Runs as a cron job every 5 minutes
"""

import json
import re
import subprocess
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import time

# Configuration - Kraliki endpoints
HEALTH_ENDPOINTS = [
    {
        "name": "Kraliki Swarm",
        "url": "http://127.0.0.1:8099/health",
        "expected_status": 200
    }
]

# Dynamically determine Kraliki directory relative to this script
KRALIKI_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = KRALIKI_DIR / "logs" / "agents"
ALERT_LOG = KRALIKI_DIR / "logs" / "health-alerts.json"
STATUS_FILE = KRALIKI_DIR / "control" / "health-status.json"
CIRCUIT_BREAKER_FILE = KRALIKI_DIR / "control" / "circuit-breakers.json"
LOG_SCAN_STATE_FILE = KRALIKI_DIR / "control" / "log-scan-state.json"

# API Error patterns
API_ERRORS = {
    "claude": ["You've hit your limit", "resets 5pm"],
    "codex": ["429 Too Many Requests", "usage_limit_reached"],
    "gemini": ["429 Too Many Requests", "Resource has been exhausted"]
}

# Agent prefix to CLI map
PREFIX_MAP = {
    "CC": "claude",
    "CX": "codex",
    "OC": "opencode",  # Often maps to Claude or specialized
    "GE": "gemini"
}

CLI_BREAKERS = ["claude_cli", "codex_cli", "gemini_cli", "opencode_cli"]
UNBLOCKED_KEYWORDS = ["unblocked", "unlimited tier enabled"]
RATE_LIMIT_RE = re.compile(r"Rate limited until (?P<ts>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})")
CLI_COOLDOWN_MINUTES = 90
CLI_FAILURE_THRESHOLD = 3
CLI_FAILURE_WINDOW_SECONDS = 600
CLI_FAILURE_SUPPRESS_SECONDS = 600
LOG_SCAN_WINDOW_SECONDS = 600
MAX_LOG_BYTES = 50_000
TUNING_OPEN_WINDOW_HOURS = 6
TUNING_DECAY_WINDOW_HOURS = 24
TUNING_MAX_THRESHOLD = 8
TUNING_MIN_THRESHOLD = 2
TUNING_MAX_COOLDOWN_MINUTES = 240
TUNING_MIN_COOLDOWN_MINUTES = 45
CLI_CALIBRATION_WINDOW_MINUTES = 60
CLI_CALIBRATION_MIN_SAMPLES = 6
CLI_MAX_HISTORY = 500


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def update_circuit_breaker(cli_tool: str, state: str, reason: str = None):
    """Update circuit breaker state."""
    breakers = {}
    if CIRCUIT_BREAKER_FILE.exists():
        try:
            breakers = json.loads(CIRCUIT_BREAKER_FILE.read_text())
        except Exception:
            pass

    key = f"{cli_tool}_cli"
    current = breakers.get(key, {"state": "closed"})
    current.setdefault("success_times", [])
    current.setdefault("failure_times", [])
    current.setdefault("recovery_durations", [])
    current.setdefault("last_open_time", None)
    now = datetime.now().isoformat()

    state_changed = current.get("state") != state
    if state == "open":
        current["last_failure_time"] = now
        current["failure_count"] = current.get("failure_count", 0) + 1
        if reason:
            current["last_failure_reason"] = reason
    elif state == "closed":
        current["last_success_time"] = now
        current["failure_count"] = 0
        if current.get("last_open_time"):
            try:
                opened_at = datetime.fromisoformat(current["last_open_time"])
                duration = (datetime.fromisoformat(now) - opened_at).total_seconds()
                current["recovery_durations"].append(duration)
            except ValueError:
                pass
            current["last_open_time"] = None
        current.pop("last_failure_reason", None)

    if state_changed or reason:
        current["state"] = state
        current["last_update"] = now
        if reason:
            log(f"Circuit breaker {state.upper()} for {cli_tool}: {reason}", "WARN")
        else:
            log(f"Circuit breaker {state.upper()} for {cli_tool}", "INFO")

        breakers[key] = current
        CIRCUIT_BREAKER_FILE.write_text(json.dumps(breakers, indent=2))


def load_log_scan_state() -> dict:
    """Load log scan offsets for incremental parsing."""
    if LOG_SCAN_STATE_FILE.exists():
        try:
            return json.loads(LOG_SCAN_STATE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_log_scan_state(state: dict) -> None:
    """Persist log scan offsets."""
    LOG_SCAN_STATE_FILE.write_text(json.dumps(state, indent=2))


def read_new_log_content(log_file: Path, state: dict) -> str:
    """Read only new log content since last scan."""
    try:
        stat = log_file.stat()
    except FileNotFoundError:
        return ""

    entry = state.get(log_file.name, {})
    last_size = entry.get("size", 0)
    last_mtime = entry.get("mtime", 0)
    size = stat.st_size
    mtime = stat.st_mtime

    if size < last_size or mtime < last_mtime:
        start = max(0, size - MAX_LOG_BYTES)
    else:
        start = last_size

    if size - start > MAX_LOG_BYTES:
        start = max(0, size - MAX_LOG_BYTES)

    if size <= start:
        state[log_file.name] = {"size": size, "mtime": mtime}
        return ""

    with open(log_file, "rb") as handle:
        handle.seek(start)
        data = handle.read(size - start)

    state[log_file.name] = {"size": size, "mtime": mtime}
    return data.decode("utf-8", errors="ignore")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def prune_timestamps(entries: list, now: datetime, max_age_hours: int) -> list:
    """Drop timestamps older than max_age_hours."""
    cutoff = now - timedelta(hours=max_age_hours)
    pruned = []
    for ts in entries:
        parsed = parse_iso(ts)
        if parsed and parsed >= cutoff:
            pruned.append(ts)
    return pruned


def tune_on_open(current: dict, now: datetime) -> None:
    """Track open events and recalibrate."""
    open_events = prune_timestamps(current.get("open_events", []), now, TUNING_DECAY_WINDOW_HOURS)
    open_events.append(now.isoformat())
    current["open_events"] = open_events
    calibrate_cli_breaker(current, now)


def tune_on_close(current: dict, now: datetime) -> None:
    """Recalibrate after recovery."""
    open_events = prune_timestamps(current.get("open_events", []), now, TUNING_DECAY_WINDOW_HOURS)
    current["open_events"] = open_events
    calibrate_cli_breaker(current, now)


def calibrate_cli_breaker(current: dict, now: datetime) -> None:
    """Self-calibrate thresholds using observed activity and recovery time."""
    current.setdefault("success_times", [])
    current.setdefault("failure_times", [])
    current.setdefault("open_events", [])
    current.setdefault("recovery_durations", [])
    current.setdefault("adaptive_threshold", CLI_FAILURE_THRESHOLD)
    current.setdefault("adaptive_cooldown_minutes", CLI_COOLDOWN_MINUTES)

    current["success_times"] = prune_timestamps(current["success_times"], now, TUNING_DECAY_WINDOW_HOURS)
    current["failure_times"] = prune_timestamps(current["failure_times"], now, TUNING_DECAY_WINDOW_HOURS)
    current["open_events"] = prune_timestamps(current["open_events"], now, TUNING_DECAY_WINDOW_HOURS)

    current["success_times"] = current["success_times"][-CLI_MAX_HISTORY:]
    current["failure_times"] = current["failure_times"][-CLI_MAX_HISTORY:]
    current["recovery_durations"] = current["recovery_durations"][-50:]

    window_cutoff = now - timedelta(minutes=CLI_CALIBRATION_WINDOW_MINUTES)
    recent_success = [
        ts for ts in current["success_times"]
        if parse_iso(ts) and parse_iso(ts) >= window_cutoff
    ]
    recent_fail = [
        ts for ts in current["failure_times"]
        if parse_iso(ts) and parse_iso(ts) >= window_cutoff
    ]

    total = len(recent_success) + len(recent_fail)
    if total < CLI_CALIBRATION_MIN_SAMPLES:
        return

    failure_rate = len(recent_fail) / max(total, 1)
    calls_per_minute = total / max(CLI_CALIBRATION_WINDOW_MINUTES, 1)

    base_threshold = 2 + min(int(round(calls_per_minute)), 6)
    if failure_rate < 0.08:
        multiplier = 1.25
    elif failure_rate < 0.25:
        multiplier = 1.0
    else:
        multiplier = 0.7

    adaptive_threshold = int(round(base_threshold * multiplier))
    adaptive_threshold = max(TUNING_MIN_THRESHOLD, min(TUNING_MAX_THRESHOLD, adaptive_threshold))

    if current["recovery_durations"]:
        sorted_durations = sorted(current["recovery_durations"][-12:])
        median_seconds = sorted_durations[len(sorted_durations) // 2]
        adaptive_cooldown = int(round((median_seconds / 60) * 1.5))
    else:
        adaptive_cooldown = int(round(CLI_COOLDOWN_MINUTES * (1 + failure_rate * 2)))

    adaptive_cooldown = max(
        TUNING_MIN_COOLDOWN_MINUTES,
        min(TUNING_MAX_COOLDOWN_MINUTES, adaptive_cooldown)
    )

    current["adaptive_threshold"] = adaptive_threshold
    current["adaptive_cooldown_minutes"] = adaptive_cooldown
    current["last_tuned_at"] = now.isoformat()


def record_cli_failure(cli_tool: str, reason: str, immediate: bool = False) -> None:
    """Record a CLI failure and open breaker if threshold is met."""
    breakers = {}
    if CIRCUIT_BREAKER_FILE.exists():
        try:
            breakers = json.loads(CIRCUIT_BREAKER_FILE.read_text())
        except Exception:
            breakers = {}

    key = f"{cli_tool}_cli"
    current = breakers.get(key, {"state": "closed"})
    now = datetime.now()
    current.setdefault("success_times", [])
    current.setdefault("failure_times", [])
    current.setdefault("recovery_durations", [])
    current.setdefault("last_open_time", None)

    last_update = parse_iso(current.get("last_update"))
    if (
        current.get("state") == "open"
        and last_update
        and now - last_update < timedelta(seconds=CLI_FAILURE_SUPPRESS_SECONDS)
    ):
        return

    failure_times = current.get("failure_times", [])
    window_cutoff = now - timedelta(seconds=CLI_FAILURE_WINDOW_SECONDS)
    trimmed_times = []
    for ts in failure_times:
        parsed = parse_iso(ts)
        if parsed and parsed >= window_cutoff:
            trimmed_times.append(ts)

    trimmed_times.append(now.isoformat())
    current["failure_times"] = trimmed_times
    current["failure_times"] = current["failure_times"][-CLI_MAX_HISTORY:]
    current["failure_count"] = len(trimmed_times)
    current["last_failure_time"] = now.isoformat()
    current["last_failure_reason"] = reason

    threshold = current.get("adaptive_threshold", CLI_FAILURE_THRESHOLD)
    if immediate:
        threshold = 1
    if current["failure_count"] >= threshold:
        state_changed = current.get("state") != "open"
        current["state"] = "open"
        current["last_update"] = now.isoformat()
        if state_changed:
            log(f"Circuit breaker OPEN for {cli_tool}: {reason}", "WARN")
            current["last_open_time"] = now.isoformat()
            tune_on_open(current, now)
    else:
        current.setdefault("state", "closed")
        current["last_update"] = now.isoformat()
        if "adaptive_threshold" not in current:
            current["adaptive_threshold"] = CLI_FAILURE_THRESHOLD
        if "adaptive_cooldown_minutes" not in current:
            current["adaptive_cooldown_minutes"] = CLI_COOLDOWN_MINUTES
        calibrate_cli_breaker(current, now)

    breakers[key] = current
    CIRCUIT_BREAKER_FILE.write_text(json.dumps(breakers, indent=2))


def record_cli_success(cli_tool: str) -> None:
    """Record a CLI success observation for calibration."""
    breakers = {}
    if CIRCUIT_BREAKER_FILE.exists():
        try:
            breakers = json.loads(CIRCUIT_BREAKER_FILE.read_text())
        except Exception:
            breakers = {}

    key = f"{cli_tool}_cli"
    current = breakers.get(key, {"state": "closed"})
    now = datetime.now()

    current.setdefault("success_times", [])
    current.setdefault("failure_times", [])
    current.setdefault("recovery_durations", [])

    current["success_times"].append(now.isoformat())
    current["success_times"] = current["success_times"][-CLI_MAX_HISTORY:]
    current["last_success_time"] = now.isoformat()

    calibrate_cli_breaker(current, now)

    breakers[key] = current
    CIRCUIT_BREAKER_FILE.write_text(json.dumps(breakers, indent=2))


def reset_cli_breakers():
    """Auto-close stale CLI breakers when limits should be cleared."""
    if not CIRCUIT_BREAKER_FILE.exists():
        return

    try:
        breakers = json.loads(CIRCUIT_BREAKER_FILE.read_text())
    except Exception:
        return

    now = datetime.now()
    updated = False

    for key in CLI_BREAKERS:
        current = breakers.get(key)
        if not current or current.get("state") != "open":
            continue

        note_source = f"{current.get('note', '')} {current.get('last_failure_reason', '')}"
        note = note_source.lower()
        if any(keyword in note for keyword in UNBLOCKED_KEYWORDS):
            current["state"] = "closed"
            current["failure_count"] = 0
            current["last_success_time"] = now.isoformat()
            current["note"] = "Auto-closed: CLI unblocked"
            current.pop("last_failure_reason", None)
            current["last_update"] = now.isoformat()
            current.setdefault("recovery_durations", [])
            if current.get("last_open_time"):
                try:
                    opened_at = datetime.fromisoformat(current["last_open_time"])
                    current["recovery_durations"].append((now - opened_at).total_seconds())
                except ValueError:
                    pass
                current["last_open_time"] = None
            tune_on_close(current, now)
            updated = True
            continue

        match = RATE_LIMIT_RE.search(note_source)
        if match:
            try:
                until = datetime.strptime(match.group("ts"), "%Y-%m-%d %H:%M:%S")
                if now >= until:
                    current["state"] = "closed"
                    current["failure_count"] = 0
                    current["last_success_time"] = now.isoformat()
                    current["note"] = "Auto-closed: rate limit window passed"
                    current.pop("last_failure_reason", None)
                    current["last_update"] = now.isoformat()
                    current.setdefault("recovery_durations", [])
                    if current.get("last_open_time"):
                        try:
                            opened_at = datetime.fromisoformat(current["last_open_time"])
                            current["recovery_durations"].append((now - opened_at).total_seconds())
                        except ValueError:
                            pass
                        current["last_open_time"] = None
                    tune_on_close(current, now)
                    updated = True
            except ValueError:
                pass
            continue

        last_failure_time = current.get("last_failure_time")
        if last_failure_time:
            try:
                last_failure = datetime.fromisoformat(last_failure_time)
                cooldown_minutes = current.get("adaptive_cooldown_minutes", CLI_COOLDOWN_MINUTES)
                if now - last_failure > timedelta(minutes=cooldown_minutes):
                    current["state"] = "closed"
                    current["failure_count"] = 0
                    current["last_success_time"] = now.isoformat()
                    current["note"] = "Auto-closed: cooldown passed"
                    current.pop("last_failure_reason", None)
                    current["last_update"] = now.isoformat()
                    current.setdefault("recovery_durations", [])
                    if current.get("last_open_time"):
                        try:
                            opened_at = datetime.fromisoformat(current["last_open_time"])
                            current["recovery_durations"].append((now - opened_at).total_seconds())
                        except ValueError:
                            pass
                        current["last_open_time"] = None
                    tune_on_close(current, now)
                    updated = True
            except ValueError:
                pass

    if updated:
        CIRCUIT_BREAKER_FILE.write_text(json.dumps(breakers, indent=2))


def check_agent_logs():
    """Scan recent agent logs for API errors."""
    try:
        scan_state = load_log_scan_state()
        scan_state_dirty = False
        now = time.time()
        activity_by_cli = {}
        error_by_cli = {}
        recent_logs = []
        for log_file in LOGS_DIR.glob("*.log"):
            if now - log_file.stat().st_mtime < LOG_SCAN_WINDOW_SECONDS:
                recent_logs.append(log_file)
        
        for log_file in recent_logs:
            # Determine CLI from prefix
            prefix = log_file.name[:2]
            cli = PREFIX_MAP.get(prefix)
            
            # Map OC to claude for now as it uses Anthropic mostly
            if prefix == "OC":
                cli = "claude"
                
            if not cli:
                continue
                
            # Check for errors
            try:
                content = read_new_log_content(log_file, scan_state)
                scan_state_dirty = True
                if not content:
                    continue
                activity_by_cli[cli] = True
                errors = API_ERRORS.get(cli, [])
                found_error = False
                for error in errors:
                    if error in content:
                        record_cli_failure(cli, f"Found '{error}' in {log_file.name}", immediate=True)
                        error_by_cli[cli] = True
                        found_error = True
                        break
                if not found_error:
                    error_by_cli.setdefault(cli, False)
            except Exception:
                pass

        for cli, had_activity in activity_by_cli.items():
            if had_activity and not error_by_cli.get(cli, False):
                record_cli_success(cli)

        if scan_state_dirty:
            save_log_scan_state(scan_state)
                
    except Exception as e:
        log(f"Error checking logs: {e}", "ERROR")


def check_endpoint(endpoint: dict) -> dict:
    """Check a single endpoint"""
    result = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "error": None
    }

    try:
        req = urllib.request.Request(endpoint["url"], method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result["status_code"] = resp.status
            if resp.status == endpoint["expected_status"]:
                result["status"] = "healthy"
            else:
                result["status"] = "degraded"
    except urllib.error.URLError as e:
        result["status"] = "down"
        result["error"] = str(e.reason)
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def get_pm2_path() -> str:
    """Find the PM2 executable path"""
    # Common locations
    paths = [
        "/home/adminmatej/.nvm/versions/node/v22.14.0/bin/pm2",
        "/usr/local/bin/pm2",
        "/usr/bin/pm2"
    ]
    for p in paths:
        if Path(p).exists():
            return p
    return "pm2"  # Fallback to PATH


def check_pm2_processes() -> list:
    """Check PM2 process status"""
    pm2_path = get_pm2_path()
    try:
        # Explicitly set PM2_HOME to ensure we see the right processes in cron
        import os
        env = os.environ.copy()
        env["PM2_HOME"] = "/home/adminmatej/.pm2"
        
        result = subprocess.run(
            [pm2_path, "jlist"],
            capture_output=True,
            text=True,
            timeout=15,
            env=env
        )
        
        if not result.stdout or not result.stdout.strip():
            return [{"name": "pm2", "error": f"Empty output from pm2 jlist. Stderr: {result.stderr[:100]}"}]

        processes = json.loads(result.stdout)

        unhealthy = []
        for p in processes:
            status = p.get("pm2_env", {}).get("status", "unknown")
            if status != "online":
                unhealthy.append({
                    "name": p.get("name"),
                    "status": status,
                    "restarts": p.get("pm2_env", {}).get("restart_time", 0)
                })
        return unhealthy
    except Exception as e:
        return [{"name": "pm2", "error": str(e)}]


def send_alert(message: str):
    """Send alert (could integrate with Slack, Discord, etc.)"""
    # For now, log to file
    alerts = []
    if ALERT_LOG.exists():
        try:
            alerts = json.loads(ALERT_LOG.read_text())
        except:
            alerts = []

    alerts.append({
        "timestamp": datetime.now().isoformat(),
        "message": message
    })

    # Keep last 100 alerts
    alerts = alerts[-100:]
    ALERT_LOG.write_text(json.dumps(alerts, indent=2))

    log(f"ALERT: {message}", "ALERT")


def main():
    log("Starting health check...")

    all_healthy = True
    results = []

    # Check HTTP endpoints
    for endpoint in HEALTH_ENDPOINTS:
        result = check_endpoint(endpoint)
        results.append(result)

        if result["status"] != "healthy":
            all_healthy = False
            send_alert(f"{result['name']} is {result['status']}: {result.get('error', 'unknown error')}")
        else:
            log(f"{result['name']}: healthy")

    # Check PM2 processes
    unhealthy_procs = check_pm2_processes()
    if unhealthy_procs:
        all_healthy = False
        for proc in unhealthy_procs:
            send_alert(f"PM2 process {proc['name']} is {proc.get('status', 'unknown')}")
    else:
        log("PM2 processes: all healthy")

    # Check Agent Logs for API limits
    check_agent_logs()
    reset_cli_breakers()

    # Save status
    status = {
        "timestamp": datetime.now().isoformat(),
        "overall": "healthy" if all_healthy else "degraded",
        "endpoints": results,
        "pm2_issues": unhealthy_procs
    }
    STATUS_FILE.write_text(json.dumps(status, indent=2))

    log(f"Health check complete: {status['overall']}")


if __name__ == "__main__":
    import time
    CHECK_INTERVAL = 30  # seconds

    while True:
        try:
            main()
        except Exception as e:
            log(f"Error in health check: {e}", "ERROR")
        time.sleep(CHECK_INTERVAL)
