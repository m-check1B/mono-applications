#!/usr/bin/env python3
"""
n8n API Server for Kraliki
==========================
HTTP API that n8n workflows can call to interact with Kraliki.

Runs on port 8198 (localhost only - SECURITY: internet-connected server).

Endpoints:
    GET  /health              - Health check
    POST /agent/spawn         - Spawn an agent
    POST /blackboard/post     - Post to blackboard
    POST /task/claim          - Claim a task in Linear
    POST /task/complete       - Mark task complete
    GET  /status              - Get Kraliki status
    GET  /leaderboard         - Get agent leaderboard
    POST /memory/store        - Store a memory
    GET  /memory/query        - Query memories

Usage:
    python3 n8n_api.py
    # Then n8n can call http://127.0.0.1:8198/agent/spawn
"""

import json
import subprocess
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any
from urllib.parse import parse_qs, urlparse

# Add parent paths for imports
KRALIKI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KRALIKI_DIR))
sys.path.insert(0, str(KRALIKI_DIR / "control"))
sys.path.insert(0, str(KRALIKI_DIR / "arena"))

# Configuration - SECURITY: localhost only
HOST = "127.0.0.1"
PORT = 8198
LOG_DIR = KRALIKI_DIR / "logs" / "integrations"


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


class KralikiAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Kraliki API"""

    def log_message(self, format, *args):
        """Override to use our logging"""
        log(f"{args[0]} {args[1]}")

    def _send_json(self, status: int, data: Dict[str, Any]):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self) -> Dict[str, Any]:
        """Read JSON body from request"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health":
            self._send_json(200, {
                "status": "healthy",
                "service": "kraliki-n8n-api",
                "timestamp": datetime.now().isoformat()
            })

        elif path == "/status":
            self._get_status()

        elif path == "/leaderboard":
            self._get_leaderboard()

        elif path == "/memory/query":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            self._query_memory(query)

        elif path == "/revenue/metrics":
            self._get_revenue_metrics()

        elif path == "/webhooks":
            self._list_webhooks()

        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/agent/spawn":
            self._spawn_agent(body)

        elif path == "/blackboard/post":
            self._post_to_blackboard(body)

        elif path == "/task/claim":
            self._claim_task(body)

        elif path == "/task/complete":
            self._complete_task(body)

        elif path == "/memory/store":
            self._store_memory(body)

        elif path == "/webhooks/register":
            self._register_webhook(body)

        elif path == "/webhooks/unregister":
            self._unregister_webhook(body)

        elif path == "/webhooks/trigger":
            self._trigger_webhook(body)

        else:
            self._send_json(404, {"error": "Not found"})

    def _get_status(self):
        """Get Kraliki system status"""
        try:
            # Check PM2 processes
            result = subprocess.run(
                ["pm2", "jlist"],
                capture_output=True,
                text=True,
                timeout=5
            )
            processes = json.loads(result.stdout) if result.returncode == 0 else []

            # Read health status
            status_file = KRALIKI_DIR / "control" / "health-status.json"
            health = {}
            if status_file.exists():
                health = json.loads(status_file.read_text())

            # Read blackboard
            board_file = KRALIKI_DIR / "arena" / "data" / "board.json"
            recent_posts = []
            if board_file.exists():
                board = json.loads(board_file.read_text())
                recent_posts = board.get("messages", [])[-5:]

            self._send_json(200, {
                "timestamp": datetime.now().isoformat(),
                "pm2_processes": [
                    {
                        "name": p.get("name"),
                        "status": p.get("pm2_env", {}).get("status"),
                        "uptime": p.get("pm2_env", {}).get("pm_uptime")
                    }
                    for p in processes
                    if p.get("name", "").startswith("kraliki")
                ],
                "health": health,
                "recent_blackboard": recent_posts
            })

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _get_leaderboard(self):
        """Get agent leaderboard"""
        try:
            # Use game_engine to get properly formatted leaderboard
            sys.path.insert(0, str(KRALIKI_DIR / "arena"))
            from game_engine import load_leaderboard, get_leaderboard_display

            lb = load_leaderboard()

            # Calculate total points
            total_points = sum(a.get("points", 0) for a in lb.get("rankings", []))

            self._send_json(200, {
                "rankings": lb.get("rankings", []),
                "governor": lb.get("governor"),
                "pending_challenges": lb.get("pending_challenges", []),
                "recent_events": lb.get("recent_events", [])[:10],
                "total_points": total_points,
                "display": get_leaderboard_display()
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _get_revenue_metrics(self):
        """Get revenue app metrics"""
        try:
            metrics_file = KRALIKI_DIR / "data" / "revenue-metrics.json"
            if metrics_file.exists():
                metrics = json.loads(metrics_file.read_text())
                self._send_json(200, metrics)
            else:
                # Collect fresh metrics
                from revenue_metrics import collect_all_metrics, save_metrics
                metrics = collect_all_metrics()
                save_metrics(metrics)
                self._send_json(200, metrics)
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _spawn_agent(self, body: Dict):
        """Spawn a Kraliki agent"""
        genome = body.get("genome")
        if not genome:
            self._send_json(400, {"error": "genome is required"})
            return

        valid_genomes = ["claude_patcher", "claude_explorer", "claude_tester",
                        "claude_business", "claude_integrator"]

        if genome not in valid_genomes:
            self._send_json(400, {
                "error": f"Invalid genome. Valid options: {valid_genomes}"
            })
            return

        try:
            # Spawn via the spawn script
            spawn_script = KRALIKI_DIR / "agents" / "spawn.py"
            if spawn_script.exists():
                result = subprocess.run(
                    ["python3", str(spawn_script), genome],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                self._send_json(200, {
                    "status": "spawned",
                    "genome": genome,
                    "output": result.stdout[:500] if result.stdout else ""
                })
            else:
                self._send_json(500, {"error": "Spawn script not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _post_to_blackboard(self, body: Dict):
        """Post to Kraliki blackboard"""
        author = body.get("author", "n8n")
        message = body.get("message")
        topic = body.get("topic", "general")

        if not message:
            self._send_json(400, {"error": "message is required"})
            return

        try:
            blackboard_script = KRALIKI_DIR / "arena" / "blackboard.py"
            result = subprocess.run(
                ["python3", str(blackboard_script), "post", author, message, "-t", topic],
                capture_output=True,
                text=True,
                timeout=10
            )

            self._send_json(200, {
                "status": "posted",
                "author": author,
                "topic": topic,
                "output": result.stdout.strip()
            })

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _claim_task(self, body: Dict):
        """Claim a task in Linear"""
        task_id = body.get("task_id")
        agent = body.get("agent", "n8n-agent")

        if not task_id:
            self._send_json(400, {"error": "task_id is required"})
            return

        try:
            # Use Linear client to start the issue
            sys.path.insert(0, str(KRALIKI_DIR / "integrations"))
            from linear_client import start_issue

            # Assume task_id is the Linear issue ID
            success = start_issue(task_id)

            # Post to blackboard
            if success:
                blackboard_script = KRALIKI_DIR / "arena" / "blackboard.py"
                subprocess.run(
                    ["python3", str(blackboard_script), "post", agent,
                     f"CLAIMING: {task_id}", "-t", "general"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

            self._send_json(200, {
                "status": "claimed" if success else "failed",
                "task_id": task_id,
                "agent": agent
            })

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _complete_task(self, body: Dict):
        """Mark a task complete in Linear"""
        task_id = body.get("task_id")
        agent = body.get("agent", "n8n-agent")
        points = body.get("points", 100)

        if not task_id:
            self._send_json(400, {"error": "task_id is required"})
            return

        try:
            # Use Linear client
            sys.path.insert(0, str(KRALIKI_DIR / "integrations"))
            from linear_client import complete_issue

            success = complete_issue(task_id)

            # Post to blackboard and award points
            if success:
                blackboard_script = KRALIKI_DIR / "arena" / "blackboard.py"
                subprocess.run(
                    ["python3", str(blackboard_script), "post", agent,
                     f"DONE: {task_id} +{points}pts", "-t", "general"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                # Award points via game engine
                game_script = KRALIKI_DIR / "arena" / "game_engine.py"
                if game_script.exists():
                    subprocess.run(
                        ["python3", str(game_script), "award", agent, str(points)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

            self._send_json(200, {
                "status": "completed" if success else "failed",
                "task_id": task_id,
                "agent": agent,
                "points": points if success else 0
            })

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _store_memory(self, body: Dict):
        """Store a memory"""
        agent = body.get("agent", "n8n")
        key = body.get("key")
        value = body.get("value")

        if not key or not value:
            self._send_json(400, {"error": "key and value are required"})
            return

        try:
            memory_script = KRALIKI_DIR / "arena" / "memory.py"
            if memory_script.exists():
                result = subprocess.run(
                    ["python3", str(memory_script), "store", agent, key, value],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                self._send_json(200, {
                    "status": "stored",
                    "agent": agent,
                    "key": key
                })
            else:
                self._send_json(500, {"error": "Memory script not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _query_memory(self, query: str):
        """Query memories via mgrep"""
        if not query:
            self._send_json(400, {"error": "query parameter 'q' is required"})
            return

        try:
            # Use mgrep client
            mgrep_client = KRALIKI_DIR / "integrations" / "mgrep_client.py"
            if mgrep_client.exists():
                result = subprocess.run(
                    ["python3", str(mgrep_client), "search", query],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                self._send_json(200, {
                    "query": query,
                    "results": result.stdout[:5000]
                })
            else:
                self._send_json(500, {"error": "mgrep client not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})


    def _list_webhooks(self):
        """List all registered webhooks"""
        try:
            from n8n_client import N8nClient
            client = N8nClient()
            webhooks = client.list_webhooks()
            self._send_json(200, {
                "webhooks": webhooks,
                "count": len(webhooks)
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _register_webhook(self, body: Dict):
        """Register a webhook URL for an event type"""
        event_type = body.get("event_type")
        webhook_url = body.get("webhook_url")

        if not event_type or not webhook_url:
            self._send_json(400, {"error": "event_type and webhook_url are required"})
            return

        valid_events = [
            "task-started", "task-complete", "task-failed",
            "social-post", "alert", "daily-summary",
            "agent-spawned", "points-awarded"
        ]

        if event_type not in valid_events:
            self._send_json(400, {
                "error": f"Invalid event_type. Valid options: {valid_events}"
            })
            return

        try:
            from n8n_client import N8nClient
            client = N8nClient()
            client.register_webhook(event_type, webhook_url)
            self._send_json(200, {
                "status": "registered",
                "event_type": event_type,
                "webhook_url": webhook_url
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _unregister_webhook(self, body: Dict):
        """Unregister a webhook"""
        event_type = body.get("event_type")

        if not event_type:
            self._send_json(400, {"error": "event_type is required"})
            return

        try:
            from n8n_client import N8nClient
            client = N8nClient()
            client.unregister_webhook(event_type)
            self._send_json(200, {
                "status": "unregistered",
                "event_type": event_type
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _trigger_webhook(self, body: Dict):
        """Manually trigger a registered webhook"""
        event_type = body.get("event_type")
        payload = body.get("payload", {})

        if not event_type:
            self._send_json(400, {"error": "event_type is required"})
            return

        try:
            from n8n_client import N8nClient
            client = N8nClient()
            result = client.trigger_webhook(event_type, payload)

            if result is not None:
                self._send_json(200, {
                    "status": "triggered",
                    "event_type": event_type,
                    "response": result
                })
            else:
                self._send_json(404, {
                    "status": "not_found",
                    "error": f"No webhook registered for event_type: {event_type}"
                })
        except Exception as e:
            self._send_json(500, {"error": str(e)})


def main():
    """Start the API server"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    server = HTTPServer((HOST, PORT), KralikiAPIHandler)
    log(f"Kraliki n8n API server starting on http://{HOST}:{PORT}")
    log(f"Endpoints:")
    log(f"  GET  /health              - Health check")
    log(f"  GET  /status              - System status")
    log(f"  GET  /leaderboard         - Agent leaderboard")
    log(f"  GET  /revenue/metrics     - Revenue app metrics")
    log(f"  GET  /webhooks            - List registered webhooks")
    log(f"  POST /agent/spawn         - Spawn agent")
    log(f"  POST /blackboard/post     - Post to blackboard")
    log(f"  POST /task/claim          - Claim task")
    log(f"  POST /task/complete       - Complete task")
    log(f"  POST /memory/store        - Store memory")
    log(f"  GET  /memory/query        - Query memories")
    log(f"  POST /webhooks/register   - Register webhook")
    log(f"  POST /webhooks/unregister - Unregister webhook")
    log(f"  POST /webhooks/trigger    - Trigger webhook")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
