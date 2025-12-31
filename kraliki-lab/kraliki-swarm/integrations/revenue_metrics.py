#!/usr/bin/env python3
"""
Revenue App Metrics Collector
=============================
Collects metrics from all revenue-generating apps and exposes them for Kraliki dashboard.

Apps tracked:
1. Sense by Kraliki (Telegram bot) - €500/audit potential
2. Speak by Kraliki (SvelteKit + FastAPI) - €400/mo B2G/B2B
3. Voice by Kraliki (SvelteKit) - B2C subscriptions
4. Focus by Kraliki (SvelteKit) - B2C freemium
5. Lab by Kraliki (Multi-AI) - €299/mo B2B

Metrics collected:
- Health status (up/down)
- Container status (Docker)
- API response time
- Last activity timestamp

Usage:
    python3 revenue_metrics.py           # Collect once
    python3 revenue_metrics.py --daemon  # Run continuously (every 60s)
"""

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Sequence

# Configuration
KRALIKI_DIR = Path(__file__).resolve().parent.parent
METRICS_FILE = KRALIKI_DIR / "data" / "revenue-metrics.json"
COLLECT_INTERVAL = 60  # seconds

# Revenue app definitions
# Note: Apps are accessed via Traefik reverse proxy, not direct localhost ports
KRALIKI_APP_DOMAIN = os.getenv("KRALIKI_APP_DOMAIN", "verduona.dev")
VERDUONA_APP_DOMAIN = os.getenv("VERDUONA_APP_DOMAIN", "verduona.dev")

REVENUE_APPS = {
    "sense_kraliki": {
        "name": "Sense by Kraliki",
        "type": "telegram_bot",
        "revenue": "€500/audit",
        "docker_filter": ["sense-kraliki"],
        "health_url": None,  # Telegram bot, no HTTP endpoint
        "external_url": f"https://sense.{KRALIKI_APP_DOMAIN}",
        "description": "Workflow audit and optimization"
    },
    "speak_kraliki": {
        "name": "Speak by Kraliki",
        "type": "web_app",
        "revenue": "€400/mo",
        "docker_filter": ["speak-kraliki"],
        "health_url": None,  # Internal port not exposed
        "external_url": f"https://speak.{KRALIKI_APP_DOMAIN}",
        "description": "Employee feedback and sentiment"
    },
    "voice_kraliki": {
        "name": "Voice by Kraliki",
        "type": "web_app",
        "revenue": "subscription",
        "docker_filter": ["voice-kraliki"],
        "health_url": None,  # Internal port not exposed
        "external_url": f"https://voice.{KRALIKI_APP_DOMAIN}",
        "description": "AI call center platform"
    },
    "focus_kraliki": {
        "name": "Focus by Kraliki",
        "type": "web_app",
        "revenue": "freemium",
        "docker_filter": ["focus-kraliki"],
        "health_url": None,  # Internal port not exposed
        "external_url": f"https://focus.{KRALIKI_APP_DOMAIN}",
        "description": "AI productivity and task management"
    },
    "lab_kraliki": {
        "name": "Lab by Kraliki",
        "type": "cli_tool",
        "revenue": "€299/mo",
        "docker_filter": None,
        "health_url": None,
        "external_url": f"https://lab.{KRALIKI_APP_DOMAIN}",
        "description": "B2B deployment platform"
    },
    "tldr_bot": {
        "name": "TL;DR Bot",
        "type": "telegram_bot",
        "revenue": "$20/mo",
        "docker_filter": "tldr",
        "health_url": None,
        "external_url": f"https://tldr.{VERDUONA_APP_DOMAIN}",
        "description": "Content summarization Telegram bot"
    },
    "learn_kraliki": {
        "name": "Learn by Kraliki",
        "type": "web_app",
        "revenue": "B2C edu",
        "docker_filter": ["learn-kraliki"],
        "health_url": None,
        "external_url": f"https://learn.{KRALIKI_APP_DOMAIN}",
        "description": "AI Academy and onboarding"
    }
}


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


def check_docker_containers(filters: str | Sequence[str]) -> Dict[str, Any]:
    """Check Docker container status for an app (supports legacy names)."""
    filter_list = [filters] if isinstance(filters, str) else list(filters)
    try:
        containers = []
        all_healthy = True
        container_names = set()

        for filter_name in filter_list:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={filter_name}", "--format",
                 "{{.Names}}|{{.Status}}|{{.State}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    parts = line.split("|")
                    if len(parts) >= 3:
                        name, status, state = parts[0], parts[1], parts[2]
                        if name in container_names:
                            continue
                        container_names.add(name)
                        is_healthy = "healthy" in status.lower() or state == "running"
                        containers.append({
                            "name": name,
                            "status": status,
                            "state": state,
                            "healthy": is_healthy
                        })
                        if not is_healthy:
                            all_healthy = False

        return {
            "containers": containers,
            "count": len(containers),
            "all_healthy": all_healthy if containers else False,
            "status": "up" if containers and all_healthy else "down" if not containers else "degraded"
        }
    except Exception as e:
        return {"error": str(e), "status": "unknown", "containers": [], "count": 0}


def check_http_health(url: str, timeout: int = 5) -> Dict[str, Any]:
    """Check HTTP health endpoint"""
    try:
        start = time.time()
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            response_time = (time.time() - start) * 1000  # ms
            body = resp.read().decode()[:500]
            return {
                "status": "healthy",
                "http_code": resp.getcode(),
                "response_time_ms": round(response_time, 2),
                "response": body[:100]
            }
    except urllib.error.HTTPError as e:
        return {
            "status": "error",
            "http_code": e.code,
            "error": str(e.reason)
        }
    except Exception as e:
        return {
            "status": "unreachable",
            "error": str(e)
        }


def check_external_url(url: str) -> Dict[str, Any]:
    """Check external URL (public-facing)"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}:%{time_total}",
             "-L", "--max-time", "10", url],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split(":")
            http_code = int(parts[0]) if parts else 0
            response_time = float(parts[1]) if len(parts) > 1 else 0

            return {
                "status": "reachable" if http_code in [200, 301, 302, 307] else "error",
                "http_code": http_code,
                "response_time_s": round(response_time, 2)
            }
        return {"status": "unreachable", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def collect_app_metrics(app_id: str, app_config: Dict) -> Dict[str, Any]:
    """Collect all metrics for a single app"""
    metrics = {
        "id": app_id,
        "name": app_config["name"],
        "type": app_config["type"],
        "revenue": app_config.get("revenue", "unknown"),
        "description": app_config.get("description", ""),
        "checked_at": datetime.now().isoformat(),
        "overall_status": "unknown"
    }

    # Check Docker containers
    docker_filter = app_config.get("docker_filter")
    if docker_filter:
        metrics["docker"] = check_docker_containers(docker_filter)

    # Check internal health endpoint
    health_url = app_config.get("health_url")
    if health_url:
        metrics["health"] = check_http_health(health_url)

    # Check external URL
    external_url = app_config.get("external_url")
    if external_url:
        metrics["external"] = check_external_url(external_url)

    # Determine overall status
    docker_ok = metrics.get("docker", {}).get("status") in ["up", None]
    health_ok = metrics.get("health", {}).get("status") == "healthy" if health_url else True
    external_ok = metrics.get("external", {}).get("status") == "reachable" if external_url else True

    if docker_ok and health_ok and external_ok:
        metrics["overall_status"] = "healthy"
    elif not docker_ok:
        metrics["overall_status"] = "down"
    else:
        metrics["overall_status"] = "degraded"

    return metrics


def collect_all_metrics() -> Dict[str, Any]:
    """Collect metrics from all revenue apps"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "collection_time_s": 0,
        "apps": {},
        "summary": {
            "total": 0,
            "healthy": 0,
            "degraded": 0,
            "down": 0,
            "unknown": 0
        }
    }

    start = time.time()

    for app_id, app_config in REVENUE_APPS.items():
        metrics = collect_app_metrics(app_id, app_config)
        result["apps"][app_id] = metrics

        # Update summary
        result["summary"]["total"] += 1
        status = metrics.get("overall_status", "unknown")
        if status in result["summary"]:
            result["summary"][status] += 1

    result["collection_time_s"] = round(time.time() - start, 2)

    return result


def save_metrics(metrics: Dict):
    """Save metrics to JSON file"""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2))


def main():
    """Run metrics collection once"""
    log("Starting revenue app metrics collection...")

    metrics = collect_all_metrics()
    save_metrics(metrics)

    # Print summary
    summary = metrics["summary"]
    log(f"Collected metrics for {summary['total']} apps: "
        f"{summary['healthy']} healthy, {summary['degraded']} degraded, "
        f"{summary['down']} down, {summary['unknown']} unknown")

    # Print per-app status
    for app_id, app_data in metrics["apps"].items():
        status = app_data.get("overall_status", "unknown")
        emoji = {"healthy": "✅", "degraded": "⚠️", "down": "❌", "unknown": "❓"}.get(status, "❓")
        log(f"  {emoji} {app_data['name']}: {status}")

    log(f"Metrics saved to {METRICS_FILE}")
    return metrics


def daemon():
    """Run metrics collection continuously"""
    log(f"Starting metrics daemon (interval: {COLLECT_INTERVAL}s)")

    while True:
        try:
            main()
        except Exception as e:
            log(f"Error collecting metrics: {e}", "ERROR")
        time.sleep(COLLECT_INTERVAL)


if __name__ == "__main__":
    import sys

    if "--daemon" in sys.argv:
        daemon()
    else:
        main()
