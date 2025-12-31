#!/usr/bin/env python3
"""Check running agents from registry.

Usage:
  python3 check_running_agents.py                # Show all running agents
  python3 check_running_agents.py codex           # Show codex agents only
  python3 check_running_agents.py --cleanup       # Clean up dead agents
  python3 check_running_agents.py --count        # Just show count
"""

import sys
import json
from pathlib import Path

KRALIKI_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(KRALIKI_DIR))

from agents.spawn import get_running_agents, cleanup_dead_agents


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check running Kraliki agents")
    parser.add_argument(
        "cli", nargs="?", help="Filter by CLI (codex, claude, opencode, gemini)"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Remove dead agents from registry"
    )
    parser.add_argument("--count", action="store_true", help="Just show count")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.cleanup:
        dead_count = cleanup_dead_agents()
        if args.json:
            print(json.dumps({"cleaned": dead_count}))
        else:
            print(f"Cleaned up {dead_count} dead agents from registry")
        return

    result = get_running_agents(filter_cli=args.cli)

    if args.count:
        print(result["count"])
        return

    if args.json:
        print(json.dumps(result, indent=2))
        return

    running = result["running"]
    dead = result["dead"]

    if not running and not dead:
        print("No agents in registry")
        return

    print(f"Running agents: {result['count']}\n")

    if running:
        for agent_id, data in sorted(running.items()):
            cli = data.get("cli", "unknown")
            genome = data.get("genome", "unknown")
            pid = data.get("pid", "?")
            print(f"  ✓ {agent_id}")
            print(f"    CLI: {cli} | Genome: {genome} | PID: {pid}")
            print()

    if dead:
        print(f"Dead agents (cleanup with --cleanup): {len(dead)}\n")
        for agent_id, data in sorted(dead.items()):
            cli = data.get("cli", "unknown")
            genome = data.get("genome", "unknown")
            pid = data.get("pid", "?")
            print(f"  ✗ {agent_id}")
            print(f"    CLI: {cli} | Genome: {genome} | PID: {pid}")
            print()


if __name__ == "__main__":
    main()
