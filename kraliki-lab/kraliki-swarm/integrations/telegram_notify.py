#!/usr/bin/env python3
"""
Kraliki Telegram Notification Integration
==========================================
Sends notifications to Telegram when agents complete high-value tasks.

Usage:
    from integrations.telegram_notify import notify_completion

    notify_completion(
        agent="darwin-claude-patcher",
        task="VD-XXX description",
        points=150
    )

Configuration:
    Set KRALIKI_TELEGRAM_BOT_TOKEN and KRALIKI_TELEGRAM_CHAT_ID in environment
    or /github/secrets/kraliki_telegram.env
"""

import os
import json
from pathlib import Path
from urllib import request
from urllib.error import HTTPError
from typing import Optional

# Default paths
SECRETS_DIR = Path("/home/adminmatej/github/secrets")
ENV_FILE = SECRETS_DIR / "kraliki_telegram.env"

# Cache loaded config
_config: dict = {}


def _load_config() -> dict:
    """Load Telegram config from environment or file."""
    global _config
    if _config:
        return _config

    # Try environment first
    bot_token = os.environ.get("KRALIKI_TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("KRALIKI_TELEGRAM_CHAT_ID")

    # Fall back to env file
    if not bot_token and ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key == "KRALIKI_TELEGRAM_BOT_TOKEN":
                    bot_token = value.strip()
                elif key == "KRALIKI_TELEGRAM_CHAT_ID":
                    chat_id = value.strip()

    _config = {
        "bot_token": bot_token,
        "chat_id": chat_id
    }
    return _config


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send a message to the configured Telegram chat.

    Args:
        text: Message text (supports HTML formatting)
        parse_mode: HTML or Markdown (default: HTML)

    Returns:
        True if sent successfully, False otherwise
    """
    config = _load_config()

    if not config.get("bot_token") or not config.get("chat_id"):
        print("[telegram_notify] Not configured - skipping notification")
        return False

    url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"

    payload = {
        "chat_id": config["chat_id"],
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }

    try:
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)

    except HTTPError as e:
        print(f"[telegram_notify] HTTP error: {e.code}")
        return False
    except Exception as e:
        print(f"[telegram_notify] Error: {e}")
        return False


def notify_completion(
    agent: str,
    task: str,
    points: int,
    issue_id: Optional[str] = None
) -> bool:
    """Send notification when agent completes a high-value task.

    Only sends if points >= 100.

    Args:
        agent: Agent genome name
        task: Task description
        points: Points earned
        issue_id: Optional Linear issue ID (e.g., VD-205)

    Returns:
        True if notification sent
    """
    # Only notify for high-value completions
    if points < 100:
        return False

    # Build message
    lines = [
        "🤖 <b>Kraliki Agent Complete</b>",
        "",
        f"<b>Agent:</b> {agent}",
    ]

    if issue_id:
        lines.append(f"<b>Task:</b> {issue_id} - {task}")
    else:
        lines.append(f"<b>Task:</b> {task}")

    lines.append(f"<b>Points:</b> +{points}")

    return send_message("\n".join(lines))


def notify_alert(message: str, level: str = "info") -> bool:
    """Send a system alert notification.

    Args:
        message: Alert message
        level: info, warning, error, critical

    Returns:
        True if sent
    """
    emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨"
    }.get(level, "ℹ️")

    text = f"{emoji} <b>Kraliki {level.upper()}</b>\n\n{message}"
    return send_message(text)


def notify_leaderboard_update(rankings: list) -> bool:
    """Send daily leaderboard update.

    Args:
        rankings: List of (agent, points) tuples

    Returns:
        True if sent
    """
    lines = ["🏆 <b>Kraliki Daily Leaderboard</b>", ""]

    medals = ["🥇", "🥈", "🥉"]
    for i, (agent, points) in enumerate(rankings[:5]):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{medal} {agent}: {points} pts")

    return send_message("\n".join(lines))


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kraliki Telegram Notifications")
    subparsers = parser.add_subparsers(dest="command")

    # Test command
    test_parser = subparsers.add_parser("test", help="Send test notification")

    # Completion command
    complete_parser = subparsers.add_parser("complete", help="Send completion notification")
    complete_parser.add_argument("--agent", required=True, help="Agent name")
    complete_parser.add_argument("--task", required=True, help="Task description")
    complete_parser.add_argument("--points", type=int, required=True, help="Points earned")
    complete_parser.add_argument("--issue", help="Linear issue ID")

    # Alert command
    alert_parser = subparsers.add_parser("alert", help="Send alert")
    alert_parser.add_argument("message", help="Alert message")
    alert_parser.add_argument("--level", default="info", choices=["info", "warning", "error", "critical"])

    args = parser.parse_args()

    if args.command == "test":
        result = send_message("🧪 <b>Kraliki Test</b>\n\nTelegram integration working!")
        print("Test sent:", result)

    elif args.command == "complete":
        result = notify_completion(
            agent=args.agent,
            task=args.task,
            points=args.points,
            issue_id=args.issue
        )
        print("Notification sent:", result)

    elif args.command == "alert":
        result = notify_alert(args.message, args.level)
        print("Alert sent:", result)

    else:
        parser.print_help()
