#!/usr/bin/env python3
"""
Stats Collector - Collects Kraliki system stats and saves to JSON files
Writes daily snapshots to logs/daily/YYYY-MM-DD.json
Updates logs/daily/latest.json with current snapshot
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any


# Configuration - Kraliki paths
KRALIKI_DIR = Path(__file__).resolve().parent.parent
STATS_DIR = KRALIKI_DIR / "logs" / "daily"
DAILY_DIR = STATS_DIR
LATEST_FILE = STATS_DIR / "latest.json"
ARENA_DIR = KRALIKI_DIR / "arena" / "data"
AGENT_LOG_DIR = KRALIKI_DIR / "logs" / "agents"
HUMANS_DIR = KRALIKI_DIR.parent / "humans-work-needed"
QUEUE_FILE = HUMANS_DIR / "QUEUE_STATUS.md"

# No highways in Kraliki - we track agents instead
HIGHWAYS = {}
LOG_DIR = KRALIKI_DIR / "logs"

# Kraliki uses Linear directly, not features.json
FEATURES_FILE = None

# Regex patterns for parsing highway logs
CYCLE_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*CYCLE (\d+) COMPLETE")
ERROR_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*\[ERROR\]")
WARN_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*\[WARN\]")
PASSED_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*(?:PASSED|complete.*success|completed successfully)")
TIMEOUT_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*TIMEOUT")
TASK_COMPLETE_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*Marked ([A-Z0-9-]+) as complete")


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def ensure_dirs():
    """Ensure stats directories exist"""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_pm2_stats() -> dict:
    """Get PM2 process statistics"""
    try:
        result = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True,
            timeout=10
        )
        processes = json.loads(result.stdout)

        stats = {
            "total": len(processes),
            "online": 0,
            "stopped": 0,
            "errored": 0,
            "processes": []
        }

        for p in processes:
            status = p.get("pm2_env", {}).get("status", "unknown")
            if status == "online":
                stats["online"] += 1
            elif status == "stopped":
                stats["stopped"] += 1
            else:
                stats["errored"] += 1

            stats["processes"].append({
                "name": p.get("name"),
                "status": status,
                "restarts": p.get("pm2_env", {}).get("restart_time", 0),
                "uptime": p.get("pm2_env", {}).get("pm_uptime", 0),
                "memory": p.get("monit", {}).get("memory", 0),
                "cpu": p.get("monit", {}).get("cpu", 0)
            })

        return stats
    except Exception as e:
        return {"error": str(e)}


def get_features_stats() -> dict:
    """Get features.json statistics"""
    try:
        if FEATURES_FILE is None or not FEATURES_FILE.exists():
            return {"error": "features.json not configured"}

        data = json.loads(FEATURES_FILE.read_text())
        features = data.get("features", [])

        stats = {
            "total": len(features),
            "passed": 0,
            "pending": 0,
            "blocked": 0,
            "by_priority": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "by_category": {}
        }

        for f in features:
            if f.get("passes"):
                stats["passed"] += 1
            elif f.get("blocked_by"):
                stats["blocked"] += 1
            else:
                stats["pending"] += 1

            priority = f.get("priority", "MEDIUM")
            if priority in stats["by_priority"]:
                stats["by_priority"][priority] += 1

            category = f.get("category", "unknown")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        return stats
    except Exception as e:
        return {"error": str(e)}


def get_business_stats() -> dict:
    """Get business stats from QUEUE_STATUS.md"""
    stats = {
        "revenue_unblocked": False,
        "active_blockers": 0,
        "critical_blockers": 0,
        "done_items": 0
    }
    
    try:
        if not QUEUE_FILE.exists():
            return stats

        content = QUEUE_FILE.read_text()
        lines = content.splitlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("- [ ]"):
                stats["active_blockers"] += 1
                if "**HW-" in line:  # Crude check for ID
                    stats["active_blockers"] += 1
            elif line.startswith("- [x]"):
                stats["done_items"] += 1

            # specific check for revenue
            if "Stripe Revenue" in line and "[x]" in line:
                stats["revenue_unblocked"] = True

        # Check for critical section
        if "## Critical Revenue Blockers" in content:
            # This is a bit fuzzy without a proper parser, but good enough for now
            pass

        return stats
    except Exception as e:
        log(f"Error getting business stats: {e}", "WARN")
        return stats


def get_health_status() -> dict:
    """Get latest health status"""
    health_file = KRALIKI_DIR / "control" / "health-status.json"
    try:
        if health_file.exists():
            return json.loads(health_file.read_text())
        return {"status": "unknown"}
    except Exception as e:
        return {"error": str(e)}


def get_system_stats() -> dict:
    """Get basic system stats"""
    try:
        # Get system uptime
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])

        # Get load average
        with open("/proc/loadavg") as f:
            load = f.read().split()[:3]

        # Get memory info
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().split()[0]
                    meminfo[key] = int(value)

        total_mem = meminfo.get("MemTotal", 0)
        free_mem = meminfo.get("MemFree", 0) + meminfo.get("Buffers", 0) + meminfo.get("Cached", 0)
        used_mem = total_mem - free_mem

        return {
            "uptime_seconds": uptime_seconds,
            "load_avg": [float(l) for l in load],
            "memory": {
                "total_kb": total_mem,
                "used_kb": used_mem,
                "percent_used": round((used_mem / total_mem) * 100, 1) if total_mem else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}


def _parse_timestamp(ts_str: str) -> datetime:
    """Parse timestamp from log line"""
    return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")


def collect_dev_stats() -> Dict[str, Any]:
    """
    Collect development statistics.

    Returns:
        Dictionary with:
        - tasks_completed: int (features completed today)
        - commits: int (commits since midnight)
        - lines_added: int (lines added since midnight)
        - lines_deleted: int (lines deleted since midnight)
        - repos_with_commits: list (repos with commits today)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    stats = {
        "tasks_completed": 0,
        "commits": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "bugs_fixed": 0,
        "repos_with_commits": []
    }

    # Parse features.json for tasks completed today
    try:
        if FEATURES_FILE is not None and FEATURES_FILE.exists():
            data = json.loads(FEATURES_FILE.read_text())
            features = data.get("features", [])

            for f in features:
                completed_at = f.get("completed_at")
                if completed_at and completed_at.startswith(today):
                    stats["tasks_completed"] += 1
    except Exception as e:
        log(f"Error parsing features.json: {e}", "WARN")

    # Collect git stats from all repos in /github
    github_root = Path("/home/adminmatej/github")
    repos_with_activity = []

    try:
        # Find all git repos
        for item in github_root.iterdir():
            if not item.is_dir():
                continue

            git_dir = item / ".git"
            if not git_dir.exists():
                continue

            try:
                # Get commits since midnight
                result = subprocess.run(
                    ["git", "log", "--since=midnight", "--oneline"],
                    cwd=item,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 and result.stdout.strip():
                    commits = result.stdout.strip().split("\n")
                    stats["commits"] += len(commits)
                    
                    # Count bugs/fixes
                    for commit in commits:
                        msg = commit.lower()
                        if "fix" in msg or "bug" in msg:
                            stats["bugs_fixed"] += 1

                    # Get line changes
                    result = subprocess.run(
                        ["git", "log", "--since=midnight", "--numstat", "--pretty=format:"],
                        cwd=item,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0:
                        for line in result.stdout.strip().split("\n"):
                            if not line:
                                continue
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    added = int(parts[0]) if parts[0] != "-" else 0
                                    deleted = int(parts[1]) if parts[1] != "-" else 0
                                    stats["lines_added"] += added
                                    stats["lines_deleted"] += deleted
                                except ValueError:
                                    continue

                    repos_with_activity.append(item.name)

            except Exception as e:
                log(f"Error processing repo {item.name}: {e}", "WARN")
                continue

        stats["repos_with_commits"] = repos_with_activity

    except Exception as e:
        log(f"Error collecting git stats: {e}", "WARN")

    return stats


def collect_highway_stats(hours: int = 24) -> Dict[str, Any]:
    """
    Collect statistics from highway logs.

    Args:
        hours: Number of hours to look back (default 24)

    Returns:
        Dictionary with metrics for each highway:
        {
            "coding_cycles": int,
            "coding_errors": int,
            "coding_successes": int,
            "coding_warnings": int,
            "coding_timeouts": int,
            "coding_tasks_completed": int,
            "coding_last_cycle": str (ISO timestamp) or None,

            "business_cycles": int,
            ... (same pattern for each highway)

            "total_cycles": int,
            "total_errors": int,
            "total_successes": int,
            "collection_time": str (ISO timestamp),
            "hours_analyzed": int
        }
    """
    cutoff_time = datetime.now() - timedelta(hours=hours)
    stats = {
        "collection_time": datetime.now().isoformat(),
        "hours_analyzed": hours,
        "total_cycles": 0,
        "total_errors": 0,
        "total_successes": 0,
        "total_warnings": 0,
        "total_timeouts": 0,
        "total_tasks_completed": 0,
    }

    for highway_name, log_file in HIGHWAYS.items():
        log_path = LOG_DIR / log_file

        highway_stats = {
            f"{highway_name}_cycles": 0,
            f"{highway_name}_errors": 0,
            f"{highway_name}_successes": 0,
            f"{highway_name}_warnings": 0,
            f"{highway_name}_timeouts": 0,
            f"{highway_name}_tasks_completed": 0,
            f"{highway_name}_last_cycle": None,
            f"{highway_name}_active": False,
        }

        if not log_path.exists():
            stats.update(highway_stats)
            continue

        try:
            with open(log_path, "r") as f:
                lines = f.readlines()
        except Exception:
            stats.update(highway_stats)
            continue

        last_cycle_time = None

        for line in lines:
            # Check for cycle completion
            cycle_match = CYCLE_PATTERN.search(line)
            if cycle_match:
                ts = _parse_timestamp(cycle_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_cycles"] += 1
                    last_cycle_time = ts

            # Check for errors
            error_match = ERROR_PATTERN.search(line)
            if error_match:
                ts = _parse_timestamp(error_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_errors"] += 1

            # Check for warnings
            warn_match = WARN_PATTERN.search(line)
            if warn_match:
                ts = _parse_timestamp(warn_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_warnings"] += 1

            # Check for successes (PASSED, complete, etc.)
            passed_match = PASSED_PATTERN.search(line)
            if passed_match:
                ts = _parse_timestamp(passed_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_successes"] += 1

            # Check for timeouts
            timeout_match = TIMEOUT_PATTERN.search(line)
            if timeout_match:
                ts = _parse_timestamp(timeout_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_timeouts"] += 1

            # Check for task completions (mainly for coding highway)
            task_match = TASK_COMPLETE_PATTERN.search(line)
            if task_match:
                ts = _parse_timestamp(task_match.group(1))
                if ts >= cutoff_time:
                    highway_stats[f"{highway_name}_tasks_completed"] += 1

        # Set last cycle time
        if last_cycle_time:
            highway_stats[f"{highway_name}_last_cycle"] = last_cycle_time.isoformat()
            # Consider active if last cycle was within 2 hours
            if last_cycle_time >= datetime.now() - timedelta(hours=2):
                highway_stats[f"{highway_name}_active"] = True

        # Add to totals
        stats["total_cycles"] += highway_stats[f"{highway_name}_cycles"]
        stats["total_errors"] += highway_stats[f"{highway_name}_errors"]
        stats["total_successes"] += highway_stats[f"{highway_name}_successes"]
        stats["total_warnings"] += highway_stats[f"{highway_name}_warnings"]
        stats["total_timeouts"] += highway_stats[f"{highway_name}_timeouts"]
        stats["total_tasks_completed"] += highway_stats[f"{highway_name}_tasks_completed"]

        stats.update(highway_stats)

    return stats


def collect_stats() -> dict:
    """Collect all stats into a single dict"""
    return {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "pm2": get_pm2_stats(),
        "features": get_features_stats(),
        "dev": collect_dev_stats(),
        "highways": collect_highway_stats(),
        "business": get_business_stats(),
        "health": get_health_status(),
        "system": get_system_stats()
    }


def save_stats(stats: dict):
    """
    Save stats to JSON files:
    - stats/daily/YYYY-MM-DD.json (daily snapshot)
    - stats/latest.json (always updated)
    """
    ensure_dirs()

    # Save daily snapshot
    date_str = stats.get("date", datetime.now().strftime("%Y-%m-%d"))
    daily_file = DAILY_DIR / f"{date_str}.json"
    daily_file.write_text(json.dumps(stats, indent=2))
    log(f"Saved daily snapshot: {daily_file}")

    # Update latest.json
    LATEST_FILE.write_text(json.dumps(stats, indent=2))
    log(f"Updated latest: {LATEST_FILE}")


def main():
    log("Starting stats collection...")

    stats = collect_stats()
    save_stats(stats)

    # Print summary
    features = stats.get("features", {})
    pm2 = stats.get("pm2", {})

    log(f"Features: {features.get('passed', 0)}/{features.get('total', 0)} passed, "
        f"{features.get('pending', 0)} pending, {features.get('blocked', 0)} blocked")
    log(f"PM2: {pm2.get('online', 0)}/{pm2.get('total', 0)} online")
    log("Stats collection complete")


if __name__ == "__main__":
    import time
    COLLECT_INTERVAL = 300  # 5 minutes

    while True:
        try:
            main()
        except Exception as e:
            log(f"Error in stats collection: {e}", "ERROR")
        time.sleep(COLLECT_INTERVAL)
