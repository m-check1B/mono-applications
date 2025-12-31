#!/usr/bin/env python3
"""Register agent presence in the swarm."""

import sys
import json
import urllib.request
import argparse

COMM_URL = "http://127.0.0.1:8199"


def register_agent(agent_id: str, agent_type: str = "claude", capabilities: list = None):
    """Register agent in the swarm."""
    if capabilities is None:
        capabilities = []

    data = {
        "agent_id": agent_id,
        "type": agent_type,
        "capabilities": capabilities
    }

    req = urllib.request.Request(
        f"{COMM_URL}/register",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            if result.get("success"):
                print(f"✅ Registered: {agent_id} ({agent_type})")
                return True
            else:
                print(f"❌ Failed: {result.get('error')}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def list_agents():
    """List all active agents."""
    try:
        with urllib.request.urlopen(f"{COMM_URL}/agents", timeout=5) as resp:
            data = json.loads(resp.read())
            agents = data.get("agents", {})

            if not agents:
                print("📭 No active agents registered")
                return

            print(f"🤖 Active agents ({len(agents)}):\n")
            for agent_id, info in agents.items():
                agent_type = info.get("type", "unknown")
                caps = ", ".join(info.get("capabilities", [])) or "none"
                print(f"  • {agent_id} ({agent_type}) - capabilities: {caps}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Register agent or list agents")
    parser.add_argument("agent_id", nargs="?", help="Agent ID to register")
    parser.add_argument("--type", default="claude", help="Agent type (claude, opencode, mac)")
    parser.add_argument("--capabilities", nargs="*", default=[], help="Agent capabilities")
    parser.add_argument("--list", action="store_true", help="List all agents")

    args = parser.parse_args()

    if args.list:
        list_agents()
    elif args.agent_id:
        register_agent(args.agent_id, args.type, args.capabilities)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
