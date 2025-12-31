#!/usr/bin/env python3
"""Send a message to another agent."""

import sys
import json
import urllib.request
import argparse

COMM_URL = "http://127.0.0.1:8199"


def send_message(to_agent: str, content: str, from_agent: str = "unknown", msg_type: str = "message"):
    """Send a message to an agent."""
    data = {
        "to": to_agent,
        "from": from_agent,
        "content": content,
        "type": msg_type
    }

    req = urllib.request.Request(
        f"{COMM_URL}/send",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            if result.get("success"):
                print(f"✉️  Message #{result['message_id']} sent to {to_agent}")
                return True
            else:
                print(f"❌ Failed: {result.get('error')}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send message to agent")
    parser.add_argument("to", help="Recipient agent ID (or 'all' for broadcast)")
    parser.add_argument("message", help="Message content")
    parser.add_argument("--from", dest="from_agent", default="cli", help="Sender ID")
    parser.add_argument("--type", default="message", choices=["message", "request", "alert"])

    args = parser.parse_args()
    send_message(args.to, args.message, args.from_agent, args.type)


if __name__ == "__main__":
    main()
