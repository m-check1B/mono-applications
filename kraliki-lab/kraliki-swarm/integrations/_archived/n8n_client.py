#!/usr/bin/env python3
"""
n8n Integration Client for Kraliki
==================================
Connects Kraliki agent swarm to n8n workflow automation.

Integration patterns:
1. Kraliki -> n8n: Trigger workflows via webhooks
2. n8n -> Kraliki: Call Kraliki API endpoints
3. Events: Post task completions, social updates to n8n

Usage:
    from integrations.n8n_client import N8nClient

    client = N8nClient()
    client.trigger_workflow("task-complete", {"task_id": "VD-123", "result": "success"})
"""

import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.error import HTTPError, URLError

# Kraliki paths
KRALIKI_DIR = Path(__file__).resolve().parent.parent
SECRETS_DIR = Path("/home/adminmatej/github/secrets")
WEBHOOKS_FILE = KRALIKI_DIR / "integrations" / "n8n_webhooks.json"
LOG_DIR = KRALIKI_DIR / "logs" / "integrations"

# n8n configuration
N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://127.0.0.1:5678")


class N8nClient:
    """Client for interacting with n8n workflows"""

    def __init__(self, base_url: str = N8N_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._webhooks: Dict[str, str] = {}
        self._load_webhooks()
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Ensure log directory exists"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_webhooks(self):
        """Load registered webhook URLs from config"""
        if WEBHOOKS_FILE.exists():
            try:
                self._webhooks = json.loads(WEBHOOKS_FILE.read_text())
            except:
                self._webhooks = {}

    def _save_webhooks(self):
        """Save registered webhook URLs to config"""
        WEBHOOKS_FILE.write_text(json.dumps(self._webhooks, indent=2))

    def _log(self, event: str, data: Dict[str, Any]):
        """Log integration events"""
        log_file = LOG_DIR / f"n8n_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def register_webhook(self, event_type: str, webhook_url: str):
        """
        Register a webhook URL for a Kraliki event type.

        Event types:
        - task-started: Agent started working on a task
        - task-complete: Agent completed a task
        - task-failed: Agent failed a task
        - social-post: New post on Kraliki social feed
        - alert: Health alert or critical event
        - daily-summary: Daily stats/digest

        Args:
            event_type: Type of event to trigger webhook
            webhook_url: n8n webhook URL
        """
        self._webhooks[event_type] = webhook_url
        self._save_webhooks()
        self._log("webhook_registered", {"event_type": event_type, "url": webhook_url})

    def unregister_webhook(self, event_type: str):
        """Remove a webhook registration"""
        if event_type in self._webhooks:
            del self._webhooks[event_type]
            self._save_webhooks()
            self._log("webhook_unregistered", {"event_type": event_type})

    def list_webhooks(self) -> Dict[str, str]:
        """List all registered webhooks"""
        return self._webhooks.copy()

    def trigger_webhook(
        self,
        event_type: str,
        payload: Dict[str, Any],
        timeout: int = 30
    ) -> Optional[Dict]:
        """
        Trigger a registered webhook with payload.

        Args:
            event_type: Type of event (must be registered)
            payload: Data to send to n8n
            timeout: Request timeout in seconds

        Returns:
            Response from n8n or None on failure
        """
        webhook_url = self._webhooks.get(event_type)
        if not webhook_url:
            self._log("webhook_not_found", {"event_type": event_type})
            return None

        # Add metadata to payload
        full_payload = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "source": "kraliki",
            "data": payload
        }

        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(full_payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode())
                self._log("webhook_triggered", {
                    "event_type": event_type,
                    "status": "success",
                    "response_status": resp.status
                })
                return result

        except HTTPError as e:
            self._log("webhook_error", {
                "event_type": event_type,
                "status": "http_error",
                "code": e.code
            })
            return None
        except URLError as e:
            self._log("webhook_error", {
                "event_type": event_type,
                "status": "connection_error",
                "error": str(e.reason)
            })
            return None
        except Exception as e:
            self._log("webhook_error", {
                "event_type": event_type,
                "status": "error",
                "error": str(e)
            })
            return None

    def health_check(self) -> bool:
        """Check if n8n is accessible"""
        try:
            req = urllib.request.Request(f"{self.base_url}/healthz")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except:
            return False

    def get_api_key(self) -> Optional[str]:
        """Get n8n API key from secrets"""
        key_file = SECRETS_DIR / "n8n_api_key.txt"
        if key_file.exists():
            return key_file.read_text().strip()
        return None

    def list_workflows(self) -> Optional[List[Dict]]:
        """
        List all workflows from n8n (requires API key).

        Note: This uses the n8n REST API, not webhooks.
        Requires N8N_API_KEY in secrets.
        """
        api_key = self.get_api_key()
        if not api_key:
            return None

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/v1/workflows",
                headers={"X-N8N-API-KEY": api_key}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode()).get("data", [])
        except Exception as e:
            self._log("api_error", {"operation": "list_workflows", "error": str(e)})
            return None


# Event helper functions for Kraliki agents
def notify_task_complete(task_id: str, agent_name: str, result: str, points: int = 0):
    """
    Notify n8n that an agent completed a task.
    Call this when marking a Linear issue as done.
    """
    client = N8nClient()
    client.trigger_webhook("task-complete", {
        "task_id": task_id,
        "agent": agent_name,
        "result": result,
        "points": points,
        "completed_at": datetime.now().isoformat()
    })


def notify_task_started(task_id: str, agent_name: str, task_title: str):
    """Notify n8n that an agent started a task"""
    client = N8nClient()
    client.trigger_webhook("task-started", {
        "task_id": task_id,
        "agent": agent_name,
        "title": task_title,
        "started_at": datetime.now().isoformat()
    })


def notify_alert(alert_type: str, message: str, severity: str = "warning"):
    """
    Send an alert to n8n (for Slack/Discord/email notifications).

    Severity: info, warning, error, critical
    """
    client = N8nClient()
    client.trigger_webhook("alert", {
        "type": alert_type,
        "message": message,
        "severity": severity
    })


def notify_social_post(author: str, message: str, topic: str = "general"):
    """Notify n8n of a new social feed post"""
    client = N8nClient()
    client.trigger_webhook("social-post", {
        "author": author,
        "message": message,
        "topic": topic
    })


# CLI for testing and management
if __name__ == "__main__":
    import sys

    client = N8nClient()

    if len(sys.argv) < 2:
        print("n8n Integration Client for Kraliki")
        print()
        print("Usage:")
        print("  python n8n_client.py health           - Check n8n health")
        print("  python n8n_client.py list             - List registered webhooks")
        print("  python n8n_client.py register <event> <url>  - Register webhook")
        print("  python n8n_client.py unregister <event>      - Remove webhook")
        print("  python n8n_client.py test <event>     - Test webhook with sample data")
        print("  python n8n_client.py workflows        - List n8n workflows (needs API key)")
        print()
        print("Event types: task-started, task-complete, task-failed, social-post, alert, daily-summary")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "health":
        if client.health_check():
            print("n8n is healthy and accessible")
        else:
            print("n8n is not accessible")
            sys.exit(1)

    elif cmd == "list":
        webhooks = client.list_webhooks()
        if webhooks:
            print("Registered webhooks:")
            for event, url in webhooks.items():
                print(f"  {event}: {url}")
        else:
            print("No webhooks registered")

    elif cmd == "register" and len(sys.argv) >= 4:
        event_type = sys.argv[2]
        webhook_url = sys.argv[3]
        client.register_webhook(event_type, webhook_url)
        print(f"Registered webhook for '{event_type}'")

    elif cmd == "unregister" and len(sys.argv) >= 3:
        event_type = sys.argv[2]
        client.unregister_webhook(event_type)
        print(f"Unregistered webhook for '{event_type}'")

    elif cmd == "test" and len(sys.argv) >= 3:
        event_type = sys.argv[2]
        sample_data = {
            "task-started": {"task_id": "VD-999", "agent": "test-agent", "title": "Test task"},
            "task-complete": {"task_id": "VD-999", "agent": "test-agent", "result": "success", "points": 100},
            "alert": {"type": "test", "message": "Test alert from Kraliki", "severity": "info"},
            "social-post": {"author": "test-agent", "message": "Test social post", "topic": "general"}
        }

        data = sample_data.get(event_type, {"test": True})
        result = client.trigger_webhook(event_type, data)
        if result:
            print(f"Webhook triggered successfully: {result}")
        else:
            print(f"Failed to trigger webhook (not registered or error)")

    elif cmd == "workflows":
        workflows = client.list_workflows()
        if workflows is None:
            print("Could not list workflows (missing API key or connection error)")
        elif not workflows:
            print("No workflows found")
        else:
            print("n8n Workflows:")
            for wf in workflows:
                status = "active" if wf.get("active") else "inactive"
                print(f"  [{status}] {wf.get('name')} (id: {wf.get('id')})")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
