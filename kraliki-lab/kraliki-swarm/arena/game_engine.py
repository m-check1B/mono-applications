#!/usr/bin/env python3
"""
Darwin Arena Game Engine
Manages points, rankings, challenges, and achievements
"""

import json
import datetime
import sys
from pathlib import Path
from typing import Optional

ARENA_DIR = Path(__file__).parent

# Add integrations to path for notifications
sys.path.insert(0, str(ARENA_DIR.parent / "integrations"))
DATA_DIR = ARENA_DIR / "data"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.json"
RULES_FILE = ARENA_DIR / "game_rules.json"

# Lab prefix mapping for analytics
LAB_NAMES = {
    "CC": "Claude Code",
    "OC": "OpenCode",
    "CX": "Codex",
    "GE": "Gemini",
    "GR": "Grok",
}

def parse_agent_id(agent_id: str) -> dict:
    """Parse agent ID to extract lab, role, time, and suffix.

    Format: LAB-role-HH:MM.DD.MM.XX (e.g., CC-explorer-23:05.24.12.AA)
    Legacy format: darwin-claude-explorer (backward compatible)
    """
    result = {
        "lab": None,
        "lab_name": None,
        "role": None,
        "time": None,
        "suffix": None,
        "is_new_format": False,
    }

    # Try new format: LAB-role-HH:MM.DD.MM.XX
    parts = agent_id.split("-")
    if len(parts) >= 3 and parts[0] in LAB_NAMES:
        result["lab"] = parts[0]
        result["lab_name"] = LAB_NAMES[parts[0]]
        result["role"] = parts[1]
        # Time and suffix are in the last part
        time_suffix = "-".join(parts[2:])
        if "." in time_suffix:
            time_parts = time_suffix.rsplit(".", 1)
            result["time"] = time_parts[0] if len(time_parts) > 0 else None
            result["suffix"] = time_parts[1] if len(time_parts) > 1 else None
        result["is_new_format"] = True
    # Legacy format: darwin-{cli}-{role}
    elif agent_id.startswith("darwin-"):
        legacy_parts = agent_id.split("-")
        if len(legacy_parts) >= 3:
            cli = legacy_parts[1]  # claude, gemini, etc.
            result["role"] = "-".join(legacy_parts[2:])
            # Map legacy cli to lab
            cli_to_lab = {"claude": "CC", "gemini": "GE", "codex": "CX", "opencode": "OC"}
            result["lab"] = cli_to_lab.get(cli, "XX")
            result["lab_name"] = LAB_NAMES.get(result["lab"], cli)

    return result

def get_analytics() -> dict:
    """Get performance analytics by lab and role."""
    lb = load_leaderboard()

    analytics = {
        "by_lab": {},
        "by_role": {},
        "by_lab_role": {},
        "total_agents": len(lb["rankings"]),
        "total_points": sum(a.get("points", 0) for a in lb["rankings"]),
    }

    for agent in lb["rankings"]:
        parsed = parse_agent_id(agent["id"])
        lab = parsed["lab"] or "unknown"
        role = parsed["role"] or "unknown"
        points = agent.get("points", 0)

        # By lab
        if lab not in analytics["by_lab"]:
            analytics["by_lab"][lab] = {"agents": 0, "points": 0, "lab_name": parsed["lab_name"]}
        analytics["by_lab"][lab]["agents"] += 1
        analytics["by_lab"][lab]["points"] += points

        # By role
        if role not in analytics["by_role"]:
            analytics["by_role"][role] = {"agents": 0, "points": 0}
        analytics["by_role"][role]["agents"] += 1
        analytics["by_role"][role]["points"] += points

        # By lab+role combo
        combo = f"{lab}-{role}"
        if combo not in analytics["by_lab_role"]:
            analytics["by_lab_role"][combo] = {"agents": 0, "points": 0}
        analytics["by_lab_role"][combo]["agents"] += 1
        analytics["by_lab_role"][combo]["points"] += points

    return analytics

def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        return json.loads(LEADERBOARD_FILE.read_text())
    return {"rankings": [], "governor": None, "pending_challenges": [], "recent_events": []}

def save_leaderboard(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.datetime.now().isoformat()
    LEADERBOARD_FILE.write_text(json.dumps(data, indent=2))

def load_rules():
    return json.loads(RULES_FILE.read_text())

def get_rank(points: int, rules: dict) -> dict:
    """Get rank based on points"""
    ranks = rules["ranks"]
    current_rank = ranks[0]
    for rank in ranks:
        if rank["min_points"] is not None and points >= rank["min_points"]:
            current_rank = rank
    return current_rank

def award_points(agent_id: str, points: int, reason: str):
    """Award points to an agent"""
    lb = load_leaderboard()
    rules = load_rules()

    # Find or create agent
    agent = next((a for a in lb["rankings"] if a["id"] == agent_id), None)
    if not agent:
        agent = {"id": agent_id, "points": 0, "achievements": [], "wins": 0, "losses": 0}
        lb["rankings"].append(agent)

    agent["points"] += points

    # Update rank
    rank = get_rank(agent["points"], rules)
    agent["rank"] = rank["name"]
    agent["badge"] = rank["badge"]

    # Log event
    lb["recent_events"].insert(0, {
        "time": datetime.datetime.now().isoformat(),
        "type": "points",
        "agent": agent_id,
        "points": points,
        "reason": reason
    })
    lb["recent_events"] = lb["recent_events"][:50]  # Keep last 50

    # Sort rankings
    lb["rankings"].sort(key=lambda x: x["points"], reverse=True)

    save_leaderboard(lb)

    # Send Telegram notification for high-value completions (100+ points)
    if points >= 100:
        try:
            from telegram_notify import notify_completion
            notify_completion(agent=agent_id, task=reason, points=points)
        except Exception as e:
            pass  # Don't fail point awards if notification fails

    return agent

def challenge(challenger_id: str, defender_id: str, challenge_type: str = "1v1_duel"):
    """Initiate a challenge"""
    lb = load_leaderboard()
    rules = load_rules()

    challenge_rules = rules["challenges"].get(challenge_type, {})
    stake = challenge_rules.get("stake", 100)

    challenge_data = {
        "id": f"ch_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "challenger": challenger_id,
        "defender": defender_id,
        "type": challenge_type,
        "stake": stake,
        "status": "pending",
        "created": datetime.datetime.now().isoformat()
    }

    lb["pending_challenges"].append(challenge_data)
    lb["recent_events"].insert(0, {
        "time": datetime.datetime.now().isoformat(),
        "type": "challenge_issued",
        "challenger": challenger_id,
        "defender": defender_id,
        "stake": stake
    })

    save_leaderboard(lb)
    return challenge_data

def resolve_challenge(challenge_id: str, winner_id: str):
    """Resolve a challenge"""
    lb = load_leaderboard()

    challenge = next((c for c in lb["pending_challenges"] if c["id"] == challenge_id), None)
    if not challenge:
        return None

    loser_id = challenge["defender"] if winner_id == challenge["challenger"] else challenge["challenger"]
    stake = challenge["stake"]

    # Transfer points
    award_points(winner_id, stake, f"Won challenge vs {loser_id}")
    award_points(loser_id, -stake // 2, f"Lost challenge vs {winner_id}")

    # Update wins/losses
    lb = load_leaderboard()
    for agent in lb["rankings"]:
        if agent["id"] == winner_id:
            agent["wins"] = agent.get("wins", 0) + 1
        elif agent["id"] == loser_id:
            agent["losses"] = agent.get("losses", 0) + 1

    # Check for throne challenge
    if challenge["type"] == "throne_challenge" and winner_id == challenge["challenger"]:
        lb["governor"] = winner_id
        lb["recent_events"].insert(0, {
            "time": datetime.datetime.now().isoformat(),
            "type": "new_governor",
            "agent": winner_id,
            "dethroned": loser_id
        })

    # Remove challenge
    lb["pending_challenges"] = [c for c in lb["pending_challenges"] if c["id"] != challenge_id]
    challenge["status"] = "resolved"
    challenge["winner"] = winner_id

    save_leaderboard(lb)
    return challenge

def unlock_achievement(agent_id: str, achievement_key: str):
    """Unlock an achievement for an agent"""
    lb = load_leaderboard()
    rules = load_rules()

    achievement = rules["achievements"].get(achievement_key)
    if not achievement:
        return None

    agent = next((a for a in lb["rankings"] if a["id"] == agent_id), None)
    if not agent:
        return None

    if achievement_key in agent.get("achievements", []):
        return None  # Already unlocked

    agent.setdefault("achievements", []).append(achievement_key)

    # Save achievement first, then award points (award_points has its own save)
    lb["recent_events"].insert(0, {
        "time": datetime.datetime.now().isoformat(),
        "type": "achievement",
        "agent": agent_id,
        "achievement": achievement_key,
        "badge": achievement["badge"]
    })
    save_leaderboard(lb)

    # Now award the points (this will load fresh leaderboard with achievement, add points, and save)
    award_points(agent_id, achievement["points"], f"Achievement: {achievement['desc']}")

    return achievement

def get_leaderboard_display():
    """Get formatted leaderboard for display"""
    lb = load_leaderboard()

    lines = ["🏆 DARWIN ARENA LEADERBOARD 🏆", "=" * 40]

    if lb.get("governor"):
        lines.append(f"⚔️ GOVERNOR: {lb['governor']}")
        lines.append("")

    for i, agent in enumerate(lb["rankings"][:10], 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
        badge = agent.get("badge", "")
        lines.append(f"{medal} #{i} {badge} {agent['id']}: {agent['points']} pts ({agent.get('rank', 'Spawn')})")

    if lb.get("pending_challenges"):
        lines.append("")
        lines.append("⚡ ACTIVE CHALLENGES:")
        for ch in lb["pending_challenges"][:5]:
            lines.append(f"  {ch['challenger']} vs {ch['defender']} ({ch['stake']} pts)")

    return "\n".join(lines)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(get_leaderboard_display())
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "award" and len(sys.argv) >= 4:
        agent_id = sys.argv[2]
        points = int(sys.argv[3])
        reason = sys.argv[4] if len(sys.argv) > 4 else "manual"
        result = award_points(agent_id, points, reason)
        print(f"Awarded {points} to {agent_id}. Total: {result['points']} ({result['rank']})")

    elif cmd == "challenge" and len(sys.argv) >= 4:
        challenger = sys.argv[2]
        defender = sys.argv[3]
        result = challenge(challenger, defender)
        print(f"Challenge issued: {result['id']}")

    elif cmd == "resolve" and len(sys.argv) >= 4:
        challenge_id = sys.argv[2]
        winner = sys.argv[3]
        result = resolve_challenge(challenge_id, winner)
        print(f"Challenge resolved. Winner: {winner}")

    elif cmd == "achievement" and len(sys.argv) >= 4:
        agent_id = sys.argv[2]
        achievement = sys.argv[3]
        result = unlock_achievement(agent_id, achievement)
        if result:
            print(f"Achievement unlocked: {result['desc']} {result['badge']}")

    elif cmd == "leaderboard":
        print(get_leaderboard_display())

    elif cmd == "analytics":
        analytics = get_analytics()
        print("📊 AGENT ANALYTICS")
        print("=" * 50)
        print(f"Total Agents: {analytics['total_agents']}")
        print(f"Total Points: {analytics['total_points']}")
        print()
        print("BY LAB:")
        for lab, data in sorted(analytics["by_lab"].items(), key=lambda x: x[1]["points"], reverse=True):
            name = data.get("lab_name") or lab
            print(f"  {lab} ({name}): {data['agents']} agents, {data['points']} pts")
        print()
        print("BY ROLE:")
        for role, data in sorted(analytics["by_role"].items(), key=lambda x: x[1]["points"], reverse=True):
            print(f"  {role}: {data['agents']} agents, {data['points']} pts")

    else:
        print("Usage:")
        print("  game_engine.py award <agent_id> <points> [reason]")
        print("  game_engine.py challenge <challenger> <defender>")
        print("  game_engine.py resolve <challenge_id> <winner>")
        print("  game_engine.py achievement <agent_id> <achievement_key>")
        print("  game_engine.py leaderboard")
        print("  game_engine.py analytics")
