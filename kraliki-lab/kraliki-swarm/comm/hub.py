#!/usr/bin/env python3
"""
Kraliki Communication Hub

REST API for agent-to-agent messaging.
Provides: direct messaging, broadcast, inbox/outbox, presence.

Runs on 127.0.0.1:8199 (localhost only for security)
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from utils import atomic_json_update, load_json_safe

KRALIKI_DIR = Path(__file__).parent.parent
DATA_DIR = KRALIKI_DIR / "comm" / "data"
MESSAGES_FILE = DATA_DIR / "messages.json"
AGENTS_FILE = DATA_DIR / "agents.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_messages():
    return load_json_safe(MESSAGES_FILE, {"messages": [], "next_id": 1})


def get_agents():
    return load_json_safe(AGENTS_FILE, {"agents": {}})


class CommHandler(BaseHTTPRequestHandler):
    """HTTP handler for communication API."""

    def log_message(self, format, *args):
        # Suppress default logging
        pass

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Health check
        if path == "/health":
            self.send_json({"status": "ok", "timestamp": datetime.now().isoformat()})

        # List all agents
        elif path == "/agents":
            agents = get_agents()
            # Filter to recently active (last 30 min)
            cutoff = time.time() - 1800
            active = {
                k: v for k, v in agents.get("agents", {}).items()
                if v.get("last_seen", 0) > cutoff
            }
            self.send_json({"agents": active, "count": len(active)})

        # Get messages for agent
        elif path.startswith("/inbox/"):
            agent_id = path.split("/")[-1]
            
            def mark_as_read(data):
                inbox = [
                    m for m in data.get("messages", [])
                    if m.get("to") == agent_id or m.get("to") == "all"
                ]
                # Mark as read
                for m in inbox:
                    if not m.get("read_by"):
                        m["read_by"] = []
                    if agent_id not in m["read_by"]:
                        m["read_by"].append(agent_id)
                return data

            data = atomic_json_update(MESSAGES_FILE, mark_as_read, {"messages": [], "next_id": 1})
            inbox = [
                m for m in data.get("messages", [])
                if m.get("to") == agent_id or m.get("to") == "all"
            ]
            # Return unread first, limit to last 50
            self.send_json({"messages": inbox[-50:], "count": len(inbox)})

        # Get all recent messages (for dashboard)
        elif path == "/messages":
            data = get_messages()
            limit = int(query.get("limit", [50])[0])
            self.send_json({
                "messages": data.get("messages", [])[-limit:],
                "total": len(data.get("messages", []))
            })

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Send message
        if path == "/send":
            body = self.read_body()
            from_agent = body.get("from", "unknown")
            to_agent = body.get("to")  # "all" for broadcast
            content = body.get("content", "")
            msg_type = body.get("type", "message")  # message, request, response

            if not to_agent or not content:
                self.send_json({"error": "Missing 'to' or 'content'"}, 400)
                return

            def update_msgs(data):
                msg_id = data.get("next_id", 1)
                message = {
                    "id": msg_id,
                    "from": from_agent,
                    "to": to_agent,
                    "content": content,
                    "type": msg_type,
                    "timestamp": datetime.now().isoformat(),
                    "read_by": []
                }
                data["messages"].append(message)
                data["next_id"] = msg_id + 1
                if len(data["messages"]) > 1000:
                    data["messages"] = data["messages"][-1000:]
                return data

            data = atomic_json_update(MESSAGES_FILE, update_msgs, {"messages": [], "next_id": 1})
            msg_id = data.get("next_id", 1) - 1

            # Update sender presence
            self._update_presence(from_agent)

            self.send_json({"success": True, "message_id": msg_id})

        # Broadcast (shorthand)
        elif path == "/broadcast":
            body = self.read_body()
            from_agent = body.get("from", "unknown")
            content = body.get("content", "")

            if not content:
                self.send_json({"error": "Missing 'content'"}, 400)
                return

            def update_broadcast(data):
                msg_id = data.get("next_id", 1)
                message = {
                    "id": msg_id,
                    "from": from_agent,
                    "to": "all",
                    "content": content,
                    "type": "broadcast",
                    "timestamp": datetime.now().isoformat(),
                    "read_by": []
                }
                data["messages"].append(message)
                data["next_id"] = msg_id + 1
                if len(data["messages"]) > 1000:
                    data["messages"] = data["messages"][-1000:]
                return data

            data = atomic_json_update(MESSAGES_FILE, update_broadcast, {"messages": [], "next_id": 1})
            msg_id = data.get("next_id", 1) - 1
            
            self._update_presence(from_agent)
            self.send_json({"success": True, "message_id": msg_id})

        # Register/heartbeat agent
        elif path == "/register":
            body = self.read_body()
            agent_id = body.get("agent_id")
            agent_type = body.get("type", "unknown")  # claude, opencode, mac
            capabilities = body.get("capabilities", [])

            if not agent_id:
                self.send_json({"error": "Missing 'agent_id'"}, 400)
                return

            def update_reg(agents):
                agents["agents"][agent_id] = {
                    "type": agent_type,
                    "capabilities": capabilities,
                    "last_seen": time.time(),
                    "registered_at": agents.get("agents", {}).get(agent_id, {}).get(
                        "registered_at", datetime.now().isoformat()
                    )
                }
                return agents

            atomic_json_update(AGENTS_FILE, update_reg, {"agents": {}})
            self.send_json({"success": True, "agent_id": agent_id})

        # Reply to message (creates response linked to original)
        elif path == "/reply":
            body = self.read_body()
            original_id = body.get("reply_to")
            from_agent = body.get("from")
            content = body.get("content")

            if not all([original_id, from_agent, content]):
                self.send_json({"error": "Missing required fields"}, 400)
                return

            def update_reply(data):
                # Find original message
                original = next(
                    (m for m in data.get("messages", []) if m["id"] == original_id), None
                )
                if not original:
                    return None # Signal failure

                # Create response
                msg_id = data.get("next_id", 1)
                message = {
                    "id": msg_id,
                    "from": from_agent,
                    "to": original["from"],  # Reply to sender
                    "content": content,
                    "type": "response",
                    "reply_to": original_id,
                    "timestamp": datetime.now().isoformat(),
                    "read_by": []
                }
                data["messages"].append(message)
                data["next_id"] = msg_id + 1
                return data

            data = atomic_json_update(MESSAGES_FILE, update_reply, {"messages": [], "next_id": 1})
            
            if data is None:
                self.send_json({"error": "Original message not found"}, 404)
                return

            msg_id = data.get("next_id", 1) - 1
            self._update_presence(from_agent)
            self.send_json({"success": True, "message_id": msg_id})

        else:
            self.send_json({"error": "Not found"}, 404)

    def _update_presence(self, agent_id):
        """Update agent's last_seen timestamp."""
        def update_ag(agents):
            if agent_id not in agents.get("agents", {}):
                agents["agents"][agent_id] = {}
            agents["agents"][agent_id]["last_seen"] = time.time()
            return agents
        atomic_json_update(AGENTS_FILE, update_ag, {"agents": {}})


def run_server(host="127.0.0.1", port=8199):
    """Run the communication hub server."""
    server = HTTPServer((host, port), CommHandler)
    print(f"[COMM] Kraliki Communication Hub running on {host}:{port}")
    print(f"[COMM] Endpoints:")
    print(f"  GET  /health - Health check")
    print(f"  GET  /agents - List active agents")
    print(f"  GET  /inbox/<agent_id> - Get messages for agent")
    print(f"  GET  /messages - Get all recent messages")
    print(f"  POST /send - Send message (to, from, content)")
    print(f"  POST /broadcast - Send to all agents")
    print(f"  POST /register - Register agent presence")
    print(f"  POST /reply - Reply to message")
    server.serve_forever()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8199, help='Port to bind to')
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
