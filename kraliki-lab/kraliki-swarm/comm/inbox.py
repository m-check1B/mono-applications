#!/usr/bin/env python3
"""Check inbox for an agent."""

import sys
import json
import urllib.request
import argparse
from datetime import datetime

COMM_URL = "http://127.0.0.1:8199"


def check_inbox(agent_id: str, unread_only: bool = False):
    """Check messages for an agent."""
    try:
        with urllib.request.urlopen(f"{COMM_URL}/inbox/{agent_id}", timeout=5) as resp:
            data = json.loads(resp.read())
            messages = data.get("messages", [])

            if unread_only:
                messages = [m for m in messages if agent_id not in m.get("read_by", [])]

            if not messages:
                print(f"📭 No messages for {agent_id}")
                return []

            print(f"📬 {len(messages)} message(s) for {agent_id}:\n")
            for m in messages[-10:]:  # Show last 10
                ts = m.get("timestamp", "")[:16]
                from_agent = m.get("from", "?")
                content = m.get("content", "")[:100]
                msg_type = m.get("type", "message")
                reply_to = f" (reply to #{m['reply_to']})" if m.get("reply_to") else ""

                icon = "📩" if msg_type == "message" else "❓" if msg_type == "request" else "✅"
                print(f"{icon} [{ts}] From: {from_agent}{reply_to}")
                print(f"   {content}")
                print()

            return messages
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Check agent inbox")
    parser.add_argument("agent_id", help="Your agent ID")
    parser.add_argument("--unread", action="store_true", help="Show unread only")

    args = parser.parse_args()
    check_inbox(args.agent_id, args.unread)


if __name__ == "__main__":
    main()
