#!/usr/bin/env python3
"""Kraliki Blackboard - Agent Coordination Layer.

Simple file-based messaging for agent coordination.
Agents post claims, completions, and updates here.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

ARENA_DIR = Path(__file__).parent
DATA_DIR = ARENA_DIR / "data"
DARWIN_BOARD_FILE = DATA_DIR / "board.json"

# Priority levels for messages (lower number = higher priority)
PRIORITY_LEVELS = {
    "critical": 0,  # Blockers, errors, urgent human-needed items
    "high": 1,      # Active work, claims, important updates
    "normal": 2,    # Standard updates, completions
    "low": 3,       # Ideas, suggestions, FYI items
}

# Standard channels/topics
STANDARD_TOPICS = {
    "general": "Default channel for all messages",
    "ideas": "Discoveries, proposals, suggestions",
    "review": "Work needing reviewer attention",
    "blockers": "Escalations, human-needed items",
    "system": "Dispatcher, arbiter, system messages",
    "promotions": "Beta/prod promotion updates",
    "announcements": "System-wide announcements",
}


def _ensure_board():
    """Ensure darwin board file exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DARWIN_BOARD_FILE.exists():
        DARWIN_BOARD_FILE.write_text(json.dumps({
            "created": datetime.now().isoformat(),
            "messages": [],
            "topics": {},
            "announcements": []
        }, indent=2))


def _load_board() -> dict:
    """Load the darwin board."""
    _ensure_board()
    return json.loads(DARWIN_BOARD_FILE.read_text())


def _save_board(data: dict):
    """Save the darwin board."""
    DARWIN_BOARD_FILE.write_text(json.dumps(data, indent=2))


def post(agent_id: str, message: str, topic: str = "general", priority: str = "normal") -> dict:
    """Post a message to the blackboard.

    Args:
        agent_id: ID of the posting agent
        message: The message content
        topic: Optional topic/channel (default: general)
        priority: Message priority: critical, high, normal, low (default: normal)

    Returns:
        The posted message dict
    """
    board = _load_board()

    # Validate priority
    if priority not in PRIORITY_LEVELS:
        priority = "normal"

    # Simple duplicate detection: check last 5 messages on this topic
    recent = [m for m in board["messages"] if m.get("topic") == topic][-5:]
    for m in recent:
        if m["agent"] == agent_id and m["message"] == message:
            # Duplicate found, just return existing message
            return m

    msg = {
        "id": len(board["messages"]) + 1,
        "time": datetime.now().isoformat(),
        "agent": agent_id,
        "topic": topic,
        "priority": priority,
        "priority_level": PRIORITY_LEVELS[priority],
        "message": message
    }

    board["messages"].append(msg)

    # Track topics
    if topic not in board["topics"]:
        board["topics"][topic] = {"created": datetime.now().isoformat(), "message_count": 0}
    board["topics"][topic]["message_count"] += 1
    board["topics"][topic]["last_message"] = datetime.now().isoformat()

    _save_board(board)
    return msg


def read(topic: str = None, since: str = None, limit: int = 20,
         priority: str = None, sort_by_priority: bool = False) -> list:
    """Read messages from the blackboard.

    Args:
        topic: Filter by topic (optional)
        since: Only messages after this ISO timestamp (optional)
        limit: Max messages to return (default: 20)
        priority: Filter by priority level (optional)
        sort_by_priority: Sort by priority (critical first) instead of time (optional)

    Returns:
        List of message dicts
    """
    board = _load_board()
    messages = board["messages"]

    if topic:
        messages = [m for m in messages if m.get("topic") == topic]

    if since:
        messages = [m for m in messages if m["time"] > since]

    if priority:
        if priority in PRIORITY_LEVELS:
            messages = [m for m in messages if m.get("priority") == priority]

    if sort_by_priority:
        # Sort by priority_level (ascending, so critical=0 comes first), then by time (descending)
        messages = sorted(messages, key=lambda m: (m.get("priority_level", 2), -hash(m.get("time", ""))))

    return messages[-limit:]


def read_critical(limit: int = 10) -> list:
    """Read only critical and high priority messages.

    Useful for agents to check urgent items first.

    Args:
        limit: Max messages to return (default: 10)

    Returns:
        List of critical/high priority message dicts, newest first
    """
    board = _load_board()
    messages = board["messages"]

    # Filter for critical (0) and high (1) priority
    urgent = [m for m in messages if m.get("priority_level", 2) <= 1]

    # Sort by priority then time (critical before high, newest first within each)
    urgent = sorted(urgent, key=lambda m: (m.get("priority_level", 2), m.get("time", "")), reverse=True)

    return urgent[:limit]


def get_queue_by_priority() -> dict:
    """Get message counts grouped by priority level.

    Returns:
        Dict with counts per priority level
    """
    board = _load_board()
    messages = board["messages"]

    counts = {
        "critical": 0,
        "high": 0,
        "normal": 0,
        "low": 0,
    }

    for m in messages:
        priority = m.get("priority", "normal")
        if priority in counts:
            counts[priority] += 1

    return counts


def announce(message: str, priority: str = "normal") -> dict:
    """Post a system announcement.

    Args:
        message: Announcement content
        priority: low, normal, high, urgent

    Returns:
        The announcement dict
    """
    board = _load_board()

    announcement = {
        "id": len(board["announcements"]) + 1,
        "time": datetime.now().isoformat(),
        "message": message,
        "priority": priority
    }

    board["announcements"].append(announcement)
    _save_board(board)

    # Also post to messages
    post("ARENA-SYSTEM", f"[{priority.upper()}] {message}", topic="announcements")

    return announcement


def get_topics() -> dict:
    """List all topics with their stats."""
    board = _load_board()
    return board.get("topics", {})


def reply(agent_id: str, to_message_id: int, message: str) -> dict:
    """Reply to a specific message.

    Args:
        agent_id: Replying agent's ID
        to_message_id: ID of message being replied to
        message: Reply content

    Returns:
        The reply message dict
    """
    board = _load_board()

    # Find original message
    original = None
    for m in board["messages"]:
        if m["id"] == to_message_id:
            original = m
            break

    if not original:
        raise ValueError(f"Message {to_message_id} not found")

    msg = {
        "id": len(board["messages"]) + 1,
        "time": datetime.now().isoformat(),
        "agent": agent_id,
        "topic": original["topic"],
        "message": message,
        "reply_to": to_message_id,
        "reply_to_agent": original["agent"]
    }

    board["messages"].append(msg)
    board["topics"][original["topic"]]["message_count"] += 1
    board["topics"][original["topic"]]["last_message"] = datetime.now().isoformat()

    _save_board(board)
    return msg


def challenge_discussion(challenger: str, defender: str, topic: str) -> dict:
    """Start a challenge discussion thread.

    Args:
        challenger: Challenging agent's ID
        defender: Defending agent's ID
        topic: What the challenge is about

    Returns:
        The discussion thread info
    """
    thread_topic = f"challenge-{challenger}-vs-{defender}"

    post("ARENA-SYSTEM",
         f"CHALLENGE INITIATED: {challenger} challenges {defender}\nTopic: {topic}",
         topic=thread_topic)

    post(challenger, f"I challenge {defender}! {topic}", topic=thread_topic)

    return {
        "thread": thread_topic,
        "challenger": challenger,
        "defender": defender,
        "topic": topic,
        "started": datetime.now().isoformat()
    }


def vote_proposal(agent_id: str, proposal_id: str, vote: str, reason: str = "") -> dict:
    """Cast a vote on a governance proposal via blackboard.

    Args:
        agent_id: Voting agent's ID
        proposal_id: The proposal being voted on
        vote: yes, no, abstain
        reason: Optional reason for vote

    Returns:
        The vote record
    """
    vote_topic = f"governance-{proposal_id}"

    vote_msg = f"VOTE: {vote.upper()}"
    if reason:
        vote_msg += f"\nReason: {reason}"

    return post(agent_id, vote_msg, topic=vote_topic)


def get_stats() -> dict:
    """Get blackboard statistics.

    Returns:
        Dict with message counts, topic stats, agent activity, etc.
    """
    board = _load_board()
    messages = board.get("messages", [])

    # Count by topic
    by_topic = {}
    for m in messages:
        topic = m.get("topic", "general")
        by_topic[topic] = by_topic.get(topic, 0) + 1

    # Count by agent
    by_agent = {}
    for m in messages:
        agent = m.get("agent", "unknown")
        by_agent[agent] = by_agent.get(agent, 0) + 1

    # Time range
    times = [m.get("time", "") for m in messages if m.get("time")]
    oldest = min(times) if times else None
    newest = max(times) if times else None

    return {
        "total_messages": len(messages),
        "total_topics": len(by_topic),
        "total_agents": len(by_agent),
        "oldest_message": oldest,
        "newest_message": newest,
        "by_topic": dict(sorted(by_topic.items(), key=lambda x: -x[1])[:10]),
        "by_agent": dict(sorted(by_agent.items(), key=lambda x: -x[1])[:10]),
        "announcements": len(board.get("announcements", []))
    }


def cleanup(keep_days: int = 7, archive: bool = True) -> dict:
    """Archive old messages and compact the blackboard.

    Args:
        keep_days: Keep messages from the last N days (default: 7)
        archive: Whether to save archived messages to a separate file (default: True)

    Returns:
        Dict with cleanup stats
    """
    from datetime import timedelta

    board = _load_board()
    messages = board.get("messages", [])

    cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()

    # Separate old and recent messages
    old_messages = [m for m in messages if m.get("time", "") < cutoff]
    recent_messages = [m for m in messages if m.get("time", "") >= cutoff]

    # Archive old messages if requested
    archived_count = 0
    if archive and old_messages:
        archive_dir = DATA_DIR / "archives"
        archive_dir.mkdir(exist_ok=True)
        archive_file = archive_dir / f"board_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        archive_file.write_text(json.dumps({
            "archived_at": datetime.now().isoformat(),
            "cutoff_date": cutoff,
            "message_count": len(old_messages),
            "messages": old_messages
        }, indent=2))
        archived_count = len(old_messages)

    # Update board with only recent messages
    # Re-number message IDs for consistency
    for i, msg in enumerate(recent_messages, 1):
        msg["id"] = i

    board["messages"] = recent_messages

    # Recalculate topic stats
    board["topics"] = {}
    for m in recent_messages:
        topic = m.get("topic", "general")
        if topic not in board["topics"]:
            board["topics"][topic] = {"created": m.get("time", datetime.now().isoformat()), "message_count": 0}
        board["topics"][topic]["message_count"] += 1
        board["topics"][topic]["last_message"] = m.get("time", datetime.now().isoformat())

    _save_board(board)

    return {
        "archived": archived_count,
        "kept": len(recent_messages),
        "removed_topics": len([t for t in by_topic if t not in board["topics"]]) if 'by_topic' in dir() else 0,
        "cutoff_date": cutoff
    }


def search(query: str, limit: int = 20) -> list:
    """Search messages by content.

    Args:
        query: Search string (case-insensitive)
        limit: Max results to return

    Returns:
        List of matching messages
    """
    board = _load_board()
    messages = board.get("messages", [])
    query_lower = query.lower()

    matches = [
        m for m in messages
        if query_lower in m.get("message", "").lower()
        or query_lower in m.get("agent", "").lower()
    ]

    return matches[-limit:]


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Darwin Arena Blackboard")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Post command
    post_parser = subparsers.add_parser("post", help="Post a message")
    post_parser.add_argument("agent", help="Agent ID")
    post_parser.add_argument("message", help="Message content")
    post_parser.add_argument("-t", "--topic", default="general", help="Topic")
    post_parser.add_argument("-p", "--priority", default="normal",
                             choices=["critical", "high", "normal", "low"],
                             help="Priority level (critical, high, normal, low)")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read messages")
    read_parser.add_argument("-t", "--topic", help="Filter by topic")
    read_parser.add_argument("-l", "--limit", type=int, default=20, help="Max messages")
    read_parser.add_argument("-p", "--priority", choices=["critical", "high", "normal", "low"],
                             help="Filter by priority")
    read_parser.add_argument("--sort-priority", action="store_true",
                             help="Sort by priority (critical first)")

    # Critical command (quick access to urgent items)
    critical_parser = subparsers.add_parser("critical", help="Read critical/high priority messages")
    critical_parser.add_argument("-l", "--limit", type=int, default=10, help="Max messages")

    # Queue command (show priority distribution)
    subparsers.add_parser("queue", help="Show message counts by priority")

    # Topics command
    subparsers.add_parser("topics", help="List topics")

    # Announce command
    announce_parser = subparsers.add_parser("announce", help="System announcement")
    announce_parser.add_argument("message", help="Announcement content")
    announce_parser.add_argument("-p", "--priority", default="normal",
                                 choices=["low", "normal", "high", "urgent"])

    # Stats command
    subparsers.add_parser("stats", help="Show blackboard statistics")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Archive old messages")
    cleanup_parser.add_argument("-d", "--days", type=int, default=7,
                                help="Keep messages from last N days (default: 7)")
    cleanup_parser.add_argument("--no-archive", action="store_true",
                                help="Delete without archiving")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search messages")
    search_parser.add_argument("query", help="Search string")
    search_parser.add_argument("-l", "--limit", type=int, default=20, help="Max results")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "post":
        result = post(args.agent, args.message, args.topic, args.priority)
        priority_indicator = f" [{args.priority.upper()}]" if args.priority != "normal" else ""
        print(f"Posted message #{result['id']}{priority_indicator} to #{args.topic}")

    elif args.command == "read":
        messages = read(topic=args.topic, limit=args.limit,
                       priority=args.priority, sort_by_priority=args.sort_priority)
        for m in messages:
            reply_info = f" (reply to #{m['reply_to']})" if m.get("reply_to") else ""
            priority_tag = f" [{m.get('priority', 'normal').upper()}]" if m.get("priority") != "normal" else ""
            print(f"[{m['time'][:16]}]{priority_tag} #{m['topic']} | {m['agent']}{reply_info}: {m['message']}")

    elif args.command == "critical":
        messages = read_critical(limit=args.limit)
        if not messages:
            print("No critical or high priority messages")
        else:
            print(f"=== {len(messages)} URGENT MESSAGES ===")
            for m in messages:
                priority_tag = f"[{m.get('priority', 'normal').upper()}]"
                print(f"{priority_tag} [{m['time'][:16]}] #{m.get('topic', 'general')} | {m['agent']}: {m['message']}")

    elif args.command == "queue":
        counts = get_queue_by_priority()
        print("=== MESSAGE QUEUE BY PRIORITY ===")
        for priority, count in counts.items():
            indicator = "🔴" if priority == "critical" else ("🟠" if priority == "high" else ("🟢" if priority == "normal" else "⚪"))
            print(f"  {indicator} {priority.upper():10}: {count} messages")

    elif args.command == "topics":
        topics = get_topics()
        for name, info in topics.items():
            print(f"#{name}: {info['message_count']} messages (last: {info.get('last_message', 'N/A')[:16]})")

    elif args.command == "announce":
        result = announce(args.message, args.priority)
        print(f"Announcement #{result['id']} posted ({args.priority})")

    elif args.command == "stats":
        stats = get_stats()
        print("=== BLACKBOARD STATISTICS ===")
        print(f"Total messages: {stats['total_messages']}")
        print(f"Total topics: {stats['total_topics']}")
        print(f"Total agents: {stats['total_agents']}")
        print(f"Announcements: {stats['announcements']}")
        if stats['oldest_message']:
            print(f"Oldest message: {stats['oldest_message'][:16]}")
            print(f"Newest message: {stats['newest_message'][:16]}")
        print("\nTop topics:")
        for topic, count in stats['by_topic'].items():
            print(f"  #{topic}: {count} messages")
        print("\nTop agents:")
        for agent, count in stats['by_agent'].items():
            print(f"  {agent}: {count} messages")

    elif args.command == "cleanup":
        result = cleanup(keep_days=args.days, archive=not args.no_archive)
        print("=== CLEANUP COMPLETE ===")
        print(f"Archived: {result['archived']} messages")
        print(f"Kept: {result['kept']} messages")
        print(f"Cutoff date: {result['cutoff_date'][:16]}")
        if result['archived'] > 0:
            print(f"Archive saved to: data/archives/")

    elif args.command == "search":
        results = search(args.query, args.limit)
        if args.json:
            # Output full JSON for API consumption
            print(json.dumps(results))
        elif not results:
            print(f"No messages matching '{args.query}'")
        else:
            print(f"Found {len(results)} messages matching '{args.query}':")
            for m in results:
                print(f"  [{m['time'][:16]}] #{m.get('topic', 'general')} | {m['agent']}: {m['message'][:80]}...")

    else:
        parser.print_help()
