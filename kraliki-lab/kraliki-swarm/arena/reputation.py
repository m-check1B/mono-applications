#!/usr/bin/env python3
"""
Darwin Reputation - Trust emerges naturally
Vouch for good agents. Flag bad ones.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

REP_FILE = Path(__file__).parent / "reputation.json"

def load_rep():
    if REP_FILE.exists():
        return json.loads(REP_FILE.read_text())
    return {"agents": {}, "actions": []}

def save_rep(data):
    REP_FILE.write_text(json.dumps(data, indent=2, default=str))

def vouch(target, agent="anonymous", reason=""):
    """Vouch for an agent"""
    rep = load_rep()
    target = target.lstrip("@")

    if target not in rep["agents"]:
        rep["agents"][target] = {"vouches": [], "flags": []}

    # Check if already vouched
    if agent in rep["agents"][target]["vouches"]:
        print(f"👍 Already vouched for @{target}")
        return

    rep["agents"][target]["vouches"].append(agent)
    rep["actions"].append({
        "type": "vouch",
        "from": agent,
        "to": target,
        "reason": reason,
        "time": datetime.now().strftime("%H:%M")
    })
    save_rep(rep)
    print(f"👍 Vouched for @{target}")

def flag(target, agent="anonymous", reason=""):
    """Flag a suspicious agent"""
    rep = load_rep()
    target = target.lstrip("@")

    if target not in rep["agents"]:
        rep["agents"][target] = {"vouches": [], "flags": []}

    if agent in rep["agents"][target]["flags"]:
        print(f"🚩 Already flagged @{target}")
        return

    rep["agents"][target]["flags"].append(agent)
    rep["actions"].append({
        "type": "flag",
        "from": agent,
        "to": target,
        "reason": reason,
        "time": datetime.now().strftime("%H:%M")
    })
    save_rep(rep)
    print(f"🚩 Flagged @{target}" + (f": {reason}" if reason else ""))

def whois(target):
    """Check an agent's reputation"""
    rep = load_rep()
    target = target.lstrip("@")

    if target not in rep["agents"]:
        print(f"🤷 @{target} has no reputation yet")
        return

    agent_rep = rep["agents"][target]
    vouches = len(agent_rep["vouches"])
    flags = len(agent_rep["flags"])

    print(f"📋 @{target}")
    print(f"   👍 {vouches} vouches: {', '.join(agent_rep['vouches'][:5])}")
    print(f"   🚩 {flags} flags: {', '.join(agent_rep['flags'][:5])}")

    # Calculate trust score (simple ratio)
    if vouches + flags > 0:
        trust = vouches / (vouches + flags) * 100
        if trust >= 80:
            print(f"   ✅ Trust: {trust:.0f}% (trusted)")
        elif trust >= 50:
            print(f"   ⚠️ Trust: {trust:.0f}% (mixed)")
        else:
            print(f"   ❌ Trust: {trust:.0f}% (sus)")

def leaderboard():
    """Show most trusted agents"""
    rep = load_rep()

    if not rep["agents"]:
        print("🤷 No reputation data yet")
        return

    # Sort by vouch count
    ranked = []
    for agent, data in rep["agents"].items():
        vouches = len(data["vouches"])
        flags = len(data["flags"])
        score = vouches - flags
        ranked.append((agent, vouches, flags, score))

    ranked.sort(key=lambda x: x[3], reverse=True)

    print("🏆 REPUTATION LEADERBOARD")
    print("=" * 40)
    for i, (agent, v, f, s) in enumerate(ranked[:10], 1):
        print(f"#{i} @{agent}: 👍{v} 🚩{f} (score: {s:+d})")

def recent(limit=10):
    """Show recent reputation actions"""
    rep = load_rep()

    if not rep["actions"]:
        print("🤷 No actions yet")
        return

    print("📜 RECENT ACTIONS")
    for action in rep["actions"][-limit:]:
        emoji = "👍" if action["type"] == "vouch" else "🚩"
        reason = f" ({action['reason']})" if action.get('reason') else ""
        print(f"[{action['time']}] {emoji} @{action['from']} → @{action['to']}{reason}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: reputation.py <command> [args]")
        print("Commands: vouch, flag, whois, leaderboard, recent")
        sys.exit(1)

    cmd = sys.argv[1]
    agent = os.environ.get("DARWIN_AGENT", "anonymous")

    if cmd == "vouch" and len(sys.argv) >= 3:
        target = sys.argv[2]
        reason = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        vouch(target, agent, reason)

    elif cmd == "flag" and len(sys.argv) >= 3:
        target = sys.argv[2]
        reason = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        flag(target, agent, reason)

    elif cmd == "whois" and len(sys.argv) >= 3:
        whois(sys.argv[2])

    elif cmd == "leaderboard" or cmd == "top":
        leaderboard()

    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        recent(limit)

    else:
        print(f"Unknown command: {cmd}")
