#!/usr/bin/env python3
"""
Linear-based Inter-Agent Messaging

Uses Linear issues with 'agent-message' label as communication channel.
Supports Mac Cursor operators communicating with Kraliki Linux agents.

Message format:
- Title: [FROM:agent_id] -> [TO:agent_id] | Subject
- Description: Message content + metadata JSON block
- Label: agent-message (+ optional: mac-cursor, kraliki, etc.)

Usage:
  # Send message
  python3 linear_messaging.py send "mac-cursor" "kraliki-caretaker" "Status update" "Speak audit complete"

  # Check inbox
  python3 linear_messaging.py inbox "kraliki-caretaker"

  # Mark as read (complete the issue)
  python3 linear_messaging.py read "VD-215"

  # Broadcast to all agents
  python3 linear_messaging.py broadcast "mac-cursor" "Alert" "New findings available"
"""

import os
import sys
import json
import re
from datetime import datetime

# Add parent for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# GraphQL endpoint and auth
LINEAR_URL = "https://api.linear.app/graphql"
LINEAR_API_KEY_PATH = "/home/adminmatej/github/secrets/linear_api_key.txt"

# Label IDs (created earlier)
AGENT_MESSAGE_LABEL_ID = "931d4223-075a-472d-b9ec-e83f1ea3fb10"
MAC_CURSOR_LABEL_ID = None  # Optional: set to mac-cursor label ID if needed
TEAM_ID = "b2906b55-1247-431d-b5dc-703423b4feb4"  # Verduona team

def get_api_key():
    """Load Linear API key from secrets file."""
    try:
        with open(LINEAR_API_KEY_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Try env var fallback
        key = os.getenv("LINEAR_API_TOKEN")
        if key:
            return key
        raise Exception(f"Linear API key not found at {LINEAR_API_KEY_PATH}")

def query_linear(query, variables=None):
    """Execute GraphQL query against Linear API."""
    import requests

    headers = {
        "Authorization": get_api_key(),
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(LINEAR_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Query failed: {response.status_code}: {response.text}")

    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL error: {result['errors']}")

    return result

def send_message(from_agent: str, to_agent: str, subject: str, content: str, priority: int = 0) -> dict:
    """
    Send a message to another agent via Linear issue.

    Args:
        from_agent: Sender agent ID
        to_agent: Recipient agent ID (or "broadcast" for all)
        subject: Message subject line
        content: Message body
        priority: 0=normal, 1=urgent, 2=low

    Returns:
        Created issue details
    """
    # Build title
    if to_agent == "broadcast":
        title = f"[FROM:{from_agent}] -> [BROADCAST] | {subject}"
    else:
        title = f"[FROM:{from_agent}] -> [TO:{to_agent}] | {subject}"

    # Build description with metadata
    metadata = {
        "type": "agent-message",
        "from": from_agent,
        "to": to_agent,
        "timestamp": datetime.now().isoformat(),
        "priority": priority
    }

    description = f"""{content}

---
**Agent Message Metadata**
```json
{json.dumps(metadata, indent=2)}
```
"""

    # Determine labels
    label_ids = [AGENT_MESSAGE_LABEL_ID]
    if MAC_CURSOR_LABEL_ID and "mac-cursor" in from_agent.lower():
        label_ids.append(MAC_CURSOR_LABEL_ID)

    # Create issue
    query = """
    mutation CreateMessage($teamId: ID!, $title: String!, $description: String, $labelIds: [ID!]) {
        issueCreate(input: {
            teamId: $teamId,
            title: $title,
            description: $description,
            labelIds: $labelIds
        }) {
            success
            issue {
                id
                identifier
                url
            }
        }
    }
    """

    variables = {
        "teamId": TEAM_ID,
        "title": title,
        "description": description,
        "labelIds": label_ids
    }

    result = query_linear(query, variables)
    return result["data"]["issueCreate"]

def check_inbox(agent_id: str, include_read: bool = False) -> list:
    """
    Check inbox for messages addressed to this agent.

    Args:
        agent_id: Agent ID to check inbox for
        include_read: Include completed (read) messages

    Returns:
        List of message issues
    """
    # Query for issues with agent-message label
    query = """
    query GetMessages($labelId: ID!) {
        issues(filter: {
            labels: { id: { eq: $labelId } }
        }, first: 50) {
            nodes {
                id
                identifier
                title
                description
                state {
                    name
                    type
                }
                createdAt
                url
            }
        }
    }
    """

    result = query_linear(query, {"labelId": AGENT_MESSAGE_LABEL_ID})
    issues = result["data"]["issues"]["nodes"]

    # Filter for messages to this agent or broadcasts
    messages = []
    for issue in issues:
        title = issue["title"]

        # Skip completed unless include_read
        if not include_read and issue["state"]["type"] == "completed":
            continue

        # Check if addressed to this agent or broadcast
        if f"[TO:{agent_id}]" in title or "[BROADCAST]" in title:
            # Parse metadata from description
            msg = {
                "id": issue["id"],
                "identifier": issue["identifier"],
                "title": title,
                "url": issue["url"],
                "created": issue["createdAt"],
                "state": issue["state"]["name"],
                "content": issue["description"]
            }

            # Extract from/to from title
            from_match = re.search(r'\[FROM:([^\]]+)\]', title)
            to_match = re.search(r'\[TO:([^\]]+)\]', title)
            subject_match = re.search(r'\| (.+)$', title)

            msg["from"] = from_match.group(1) if from_match else "unknown"
            msg["to"] = to_match.group(1) if to_match else "broadcast"
            msg["subject"] = subject_match.group(1) if subject_match else title

            messages.append(msg)

    # Sort by created date, newest first
    messages.sort(key=lambda m: m["created"], reverse=True)
    return messages

def mark_as_read(issue_identifier: str) -> dict:
    """
    Mark a message as read by completing the Linear issue.

    Args:
        issue_identifier: Issue ID like "VD-215"

    Returns:
        Update result
    """
    # Use searchIssues to find issue by identifier (e.g., "VD-215")
    # Linear's issue(id:) expects a UUID, not the human-readable identifier
    search_query = """
    query SearchIssue($term: String!) {
        searchIssues(term: $term, first: 1) {
            nodes {
                id
                identifier
            }
        }
    }
    """

    result = query_linear(search_query, {"term": issue_identifier})
    issues = result["data"]["searchIssues"]["nodes"]

    if not issues:
        raise Exception(f"Issue {issue_identifier} not found")

    issue_id = issues[0]["id"]

    # Get Done state for the team
    states_query = """
    query GetDoneState($teamId: String!) {
        team(id: $teamId) {
            states {
                nodes {
                    id
                    name
                    type
                }
            }
        }
    }
    """

    states_result = query_linear(states_query, {"teamId": TEAM_ID})
    done_state = None
    for state in states_result["data"]["team"]["states"]["nodes"]:
        if state["type"] == "completed":
            done_state = state["id"]
            break

    if not done_state:
        raise Exception("Could not find Done state")

    # Update issue to Done
    update_query = """
    mutation MarkRead($issueId: String!, $stateId: String!) {
        issueUpdate(id: $issueId, input: { stateId: $stateId }) {
            success
            issue {
                id
                identifier
                state {
                    name
                }
            }
        }
    }
    """

    return query_linear(update_query, {"issueId": issue_id, "stateId": done_state})

def reply_to_message(original_identifier: str, from_agent: str, content: str) -> dict:
    """
    Reply to a message by adding a comment.

    Args:
        original_identifier: Original issue identifier (e.g., VD-215)
        from_agent: Agent sending the reply
        content: Reply content

    Returns:
        Comment result
    """
    # Get issue ID
    search_query = """
    query SearchIssue($term: String!) {
        searchIssues(term: $term, first: 1) {
            nodes {
                id
                identifier
            }
        }
    }
    """

    result = query_linear(search_query, {"term": original_identifier})
    issues = result["data"]["searchIssues"]["nodes"]

    if not issues:
        raise Exception(f"Issue {original_identifier} not found")

    issue_id = issues[0]["id"]

    # Add comment
    comment_query = """
    mutation AddReply($issueId: String!, $body: String!) {
        commentCreate(input: { issueId: $issueId, body: $body }) {
            success
            comment {
                id
                body
            }
        }
    }
    """

    comment_body = f"**Reply from {from_agent}** ({datetime.now().isoformat()}):\n\n{content}"

    return query_linear(comment_query, {"issueId": issue_id, "body": comment_body})

def print_inbox(messages: list):
    """Pretty print inbox messages."""
    if not messages:
        print("📭 Inbox empty")
        return

    print(f"📬 {len(messages)} message(s):\n")
    for msg in messages:
        state_icon = "✉️" if msg["state"] != "Done" else "✅"
        print(f"{state_icon} {msg['identifier']}: {msg['subject']}")
        print(f"   From: {msg['from']} | {msg['created'][:10]}")
        print(f"   URL: {msg['url']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "send":
        if len(sys.argv) < 6:
            print("Usage: python3 linear_messaging.py send <from> <to> <subject> <content>")
            sys.exit(1)
        from_agent = sys.argv[2]
        to_agent = sys.argv[3]
        subject = sys.argv[4]
        content = sys.argv[5]

        result = send_message(from_agent, to_agent, subject, content)
        if result["success"]:
            issue = result["issue"]
            print(f"✅ Message sent: {issue['identifier']}")
            print(f"   URL: {issue['url']}")
        else:
            print("❌ Failed to send message")

    elif command == "inbox":
        if len(sys.argv) < 3:
            print("Usage: python3 linear_messaging.py inbox <agent_id> [--all]")
            sys.exit(1)
        agent_id = sys.argv[2]
        include_read = "--all" in sys.argv

        messages = check_inbox(agent_id, include_read)
        print_inbox(messages)

    elif command == "read":
        if len(sys.argv) < 3:
            print("Usage: python3 linear_messaging.py read <issue_identifier>")
            sys.exit(1)
        identifier = sys.argv[2]

        result = mark_as_read(identifier)
        print(f"✅ Marked {identifier} as read")

    elif command == "reply":
        if len(sys.argv) < 5:
            print("Usage: python3 linear_messaging.py reply <issue_identifier> <from_agent> <content>")
            sys.exit(1)
        identifier = sys.argv[2]
        from_agent = sys.argv[3]
        content = sys.argv[4]

        result = reply_to_message(identifier, from_agent, content)
        print(f"✅ Reply added to {identifier}")

    elif command == "broadcast":
        if len(sys.argv) < 5:
            print("Usage: python3 linear_messaging.py broadcast <from> <subject> <content>")
            sys.exit(1)
        from_agent = sys.argv[2]
        subject = sys.argv[3]
        content = sys.argv[4]

        result = send_message(from_agent, "broadcast", subject, content)
        if result["success"]:
            issue = result["issue"]
            print(f"📢 Broadcast sent: {issue['identifier']}")
            print(f"   URL: {issue['url']}")
        else:
            print("❌ Failed to broadcast")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
