#!/usr/bin/env python3
"""Broadcast a message to all agents."""

import sys
import json
import urllib.request
import argparse

COMM_URL = "http://127.0.0.1:8199"


def broadcast(content: str, from_agent: str = "unknown"):
    """Broadcast message to all agents."""
    data = {
        "to": "all",
        "from": from_agent,
        "content": content,
        "type": "message"
    }

    req = urllib.request.Request(
        f"{COMM_URL}/broadcast",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            if result.get("success"):
                print(f"📢 Broadcast #{result['message_id']} sent to all agents")
                return True
            else:
                print(f"❌ Failed: {result.get('error')}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Broadcast to all agents")
    parser.add_argument("message", help="Message to broadcast")
    parser.add_argument("--from", dest="from_agent", default="cli", help="Sender ID")

    args = parser.parse_args()
    broadcast(args.message, args.from_agent)


if __name__ == "__main__":
    main()
