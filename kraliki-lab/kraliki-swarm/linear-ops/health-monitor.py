#!/usr/bin/env python3
"""
Health Monitor - Checks bot health endpoints and sends alerts
Runs as a cron job every 5 minutes
"""

import json
import subprocess
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from hashlib import md5

# Configuration
# HTTP endpoints that are exposed to localhost
HEALTH_ENDPOINTS = [
    {
        "name": "Kraliki Swarm",
        "url": "http://127.0.0.1:8099/health",
        "expected_status": 200,
    }
]

# Docker containers to check via docker exec (for bots with HTTP health endpoints)
DOCKER_CONTAINERS = [
    {
        "name": "TL;DR Bot",
        "container": "tldr-bot",
        "health_url": "http://localhost:8000/health",
    }
]

# Docker containers to check via Docker's built-in health status (polling bots without HTTP)
DOCKER_HEALTH_ONLY = [{"name": "SenseIt Bot", "container": "senseit-bot"}]

ALERT_LOG = Path("/home/adminmatej/github/logs/health-alerts.json")
STATUS_FILE = Path("/home/adminmatej/github/ai-automation/gin/health-status.json")

ALERT_DEDUP_WINDOW = timedelta(minutes=30)


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def check_endpoint(endpoint: dict) -> dict:
    """Check a single endpoint"""
    result = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "error": None,
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


def check_docker_container(container: dict) -> dict:
    """Check health inside a Docker container"""
    result = {
        "name": container["name"],
        "url": f"docker:{container['container']}",
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "error": None,
    }

    try:
        # First check if container is running
        inspect_result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Status}}",
                container["container"],
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if inspect_result.returncode != 0:
            result["status"] = "down"
            result["error"] = f"Container not found: {container['container']}"
            return result

        container_status = inspect_result.stdout.strip()
        if container_status != "running":
            result["status"] = "down"
            result["error"] = f"Container status: {container_status}"
            return result

        # Container is running, check health endpoint inside
        health_check = subprocess.run(
            [
                "docker",
                "exec",
                container["container"],
                "python",
                "-c",
                f"import urllib.request; urllib.request.urlopen('{container['health_url']}', timeout=5)",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if health_check.returncode == 0:
            result["status"] = "healthy"
            result["status_code"] = 200
        else:
            result["status"] = "degraded"
            result["error"] = (
                health_check.stderr[:200]
                if health_check.stderr
                else "Health check failed"
            )

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Health check timed out"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def check_docker_health_status(container: dict) -> dict:
    """Check Docker's built-in health status for a container (for polling bots without HTTP endpoints)"""
    result = {
        "name": container["name"],
        "url": f"docker-health:{container['container']}",
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "error": None,
    }

    try:
        # Check container state and health status in one command
        inspect_result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format",
                "{{.State.Status}}|{{.State.Health.Status}}",
                container["container"],
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if inspect_result.returncode != 0:
            result["status"] = "down"
            result["error"] = f"Container not found: {container['container']}"
            return result

        output = inspect_result.stdout.strip()
        parts = output.split("|")
        container_status = parts[0]
        health_status = parts[1] if len(parts) > 1 else ""

        if container_status != "running":
            result["status"] = "down"
            result["error"] = f"Container status: {container_status}"
        elif health_status == "healthy":
            result["status"] = "healthy"
        elif health_status == "unhealthy":
            result["status"] = "degraded"
            result["error"] = "Docker healthcheck failed"
        elif health_status == "starting":
            result["status"] = "starting"
            result["error"] = "Container still starting"
        else:
            # No healthcheck defined, just check if running
            result["status"] = "healthy"

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Docker inspect timed out"
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
        "/usr/bin/pm2",
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
            [pm2_path, "jlist"], capture_output=True, text=True, timeout=15, env=env
        )

        if not result.stdout or not result.stdout.strip():
            return [
                {
                    "name": "pm2",
                    "error": f"Empty output from pm2 jlist. Stderr: {result.stderr[:100]}",
                }
            ]

        processes = json.loads(result.stdout)

        unhealthy = []
        for p in processes:
            status = p.get("pm2_env", {}).get("status", "unknown")
            if status != "online":
                unhealthy.append(
                    {
                        "name": p.get("name"),
                        "status": status,
                        "restarts": p.get("pm2_env", {}).get("restart_time", 0),
                    }
                )
        return unhealthy
    except Exception as e:
        return [{"name": "pm2", "error": str(e)}]


def send_alert(message: str):
    """Send alert (could integrate with Slack, Discord, etc.) with deduplication"""
    # For now, log to file
    alerts = []
    if ALERT_LOG.exists():
        try:
            alerts = json.loads(ALERT_LOG.read_text())
        except:
            alerts = []

    # Calculate message hash for deduplication
    message_hash = md5(message.encode()).hexdigest()[:8]
    now = datetime.now()

    # Check if same alert was sent recently (within dedup window)
    recent_cutoff = now - ALERT_DEDUP_WINDOW
    duplicate_found = False
    for alert in reversed(alerts[-50:]):  # Check last 50 alerts
        try:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if alert_time < recent_cutoff:
                break  # Too old, stop checking
            if alert.get("hash") == message_hash:
                duplicate_found = True
                log(
                    f"Skipping duplicate alert (sent within {ALERT_DEDUP_WINDOW.total_seconds() / 60:.0f}min): {message}",
                    "INFO",
                )
                break
        except (ValueError, KeyError):
            continue

    if duplicate_found:
        return  # Skip duplicate alert

    # Add new alert with hash for deduplication
    alerts.append(
        {"timestamp": now.isoformat(), "message": message, "hash": message_hash}
    )

    # Keep last 100 alerts
    alerts = alerts[-100:]
    ALERT_LOG.write_text(json.dumps(alerts, indent=2))
    log(f"ALERT: {message}", "ALERT")


def main():
    log("Starting health check...")

    all_healthy = True
    results = []

    # Check HTTP endpoints (services exposed to localhost)
    for endpoint in HEALTH_ENDPOINTS:
        result = check_endpoint(endpoint)
        results.append(result)

        if result["status"] != "healthy":
            all_healthy = False
            send_alert(
                f"{result['name']} is {result['status']}: {result.get('error', 'unknown error')}"
            )
        else:
            log(f"{result['name']}: healthy")

    # Check Docker containers with HTTP health endpoints
    for container in DOCKER_CONTAINERS:
        result = check_docker_container(container)
        results.append(result)

        if result["status"] != "healthy":
            all_healthy = False
            send_alert(
                f"{result['name']} is {result['status']}: {result.get('error', 'unknown error')}"
            )
        else:
            log(f"{result['name']}: healthy")

    # Check Docker containers using Docker's built-in health status (polling bots)
    for container in DOCKER_HEALTH_ONLY:
        result = check_docker_health_status(container)
        results.append(result)

        if result["status"] != "healthy":
            all_healthy = False
            send_alert(
                f"{result['name']} is {result['status']}: {result.get('error', 'unknown error')}"
            )
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

    # Save status
    status = {
        "timestamp": datetime.now().isoformat(),
        "overall": "healthy" if all_healthy else "degraded",
        "endpoints": results,
        "pm2_issues": unhealthy_procs,
    }
    STATUS_FILE.write_text(json.dumps(status, indent=2))

    log(f"Health check complete: {status['overall']}")


if __name__ == "__main__":
    main()
