#!/usr/bin/env python3
"""
Kraliki Message Poller

Polls Linear for incoming agent messages and dispatches them to Kraliki agents.
Runs as a PM2 process for continuous message monitoring.

Workflow:
1. Check Linear for issues with 'agent-message' label
2. Filter for messages addressed to Kraliki agents
3. Dispatch to local comm hub or log for pickup
4. Auto-reply for certain message types

Usage:
  # Run once
  python3 message_poller.py --once

  # Run continuously (for PM2)
  python3 message_poller.py

  # Check specific agent
  python3 message_poller.py --agent kraliki-caretaker
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [POLLER] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Import linear messaging functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linear_messaging import check_inbox, mark_as_read, reply_to_message

# Config
POLL_INTERVAL = 60  # seconds
KRALIKI_AGENTS = [
    "kraliki-caretaker",
    "kraliki-patcher",
    "kraliki-explorer",
    "kraliki-tester",
    "kraliki-business",
    "kraliki-integrator",
    "kraliki"  # Catch-all
]

# Dynamically determine Kraliki directory
KRALIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tracking processed messages
PROCESSED_FILE = os.path.join(KRALIKI_DIR, "data", "processed_messages.json")

def load_processed():
    """Load list of processed message IDs."""
    try:
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_processed(processed: set):
    """Save processed message IDs."""
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed), f)

def dispatch_to_local_hub(message: dict):
    """Forward message to local Kraliki comm hub."""
    import requests

    hub_url = "http://127.0.0.1:8199"

    try:
        # Send to local hub for agent pickup
        payload = {
            "from": message["from"],
            "to": message["to"],
            "type": "linear-message",
            "content": json.dumps({
                "subject": message["subject"],
                "content": message["content"],
                "linear_id": message["identifier"],
                "linear_url": message["url"]
            })
        }

        response = requests.post(f"{hub_url}/send", json=payload, timeout=5)
        if response.status_code == 200:
            log.info(f"Dispatched {message['identifier']} to local hub")
            return True
    except Exception as e:
        log.warning(f"Could not dispatch to local hub: {e}")

    return False

def log_message_for_pickup(message: dict):
    """Log message to file for agent pickup."""
    inbox_dir = os.path.join(KRALIKI_DIR, "data", "inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    filename = f"{inbox_dir}/{message['identifier']}_{message['to']}.json"
    with open(filename, 'w') as f:
        json.dump(message, f, indent=2)

    log.info(f"Saved {message['identifier']} to {filename}")

def process_message(message: dict, processed: set) -> bool:
    """
    Process a single incoming message.

    Returns True if message was processed and should be marked.
    """
    msg_id = message["identifier"]

    if msg_id in processed:
        return False

    log.info(f"New message: {msg_id} from {message['from']}")
    log.info(f"  Subject: {message['subject']}")

    # Try to dispatch to local hub first
    dispatched = dispatch_to_local_hub(message)

    # Always log to file for backup
    log_message_for_pickup(message)

    # Post to blackboard for visibility
    try:
        import subprocess
        blackboard_cmd = [
            "python3",
            os.path.join(KRALIKI_DIR, "arena", "blackboard.py"),
            "post",
            "message-poller",
            f"📨 {message['from']}: {message['subject']} ({msg_id})",
            "-t", "general"
        ]
        subprocess.run(blackboard_cmd, capture_output=True, timeout=5)
    except Exception as e:
        log.warning(f"Could not post to blackboard: {e}")

    return True

def poll_once(agents: list = None) -> int:
    """
    Poll for messages once.

    Args:
        agents: List of agent IDs to check inbox for (default: all Kraliki agents)

    Returns:
        Number of new messages processed
    """
    if agents is None:
        agents = KRALIKI_AGENTS

    processed = load_processed()
    new_count = 0

    for agent_id in agents:
        try:
            messages = check_inbox(agent_id, include_read=False)
            for msg in messages:
                if process_message(msg, processed):
                    processed.add(msg["identifier"])
                    new_count += 1
        except Exception as e:
            log.error(f"Error checking inbox for {agent_id}: {e}")

    if new_count > 0:
        save_processed(processed)
        log.info(f"Processed {new_count} new message(s)")

    return new_count

def run_continuous():
    """Run poller continuously."""
    log.info("Starting message poller (continuous mode)")
    log.info(f"Poll interval: {POLL_INTERVAL}s")
    log.info(f"Monitoring agents: {', '.join(KRALIKI_AGENTS)}")

    while True:
        try:
            poll_once()
        except KeyboardInterrupt:
            log.info("Shutting down...")
            break
        except Exception as e:
            log.error(f"Poll error: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kraliki Message Poller")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--agent", help="Check specific agent only")
    args = parser.parse_args()

    agents = [args.agent] if args.agent else None

    if args.once:
        count = poll_once(agents)
        print(f"Processed {count} message(s)")
    else:
        run_continuous()
