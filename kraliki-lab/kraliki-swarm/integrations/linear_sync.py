#!/usr/bin/env python3
"""
Kraliki Linear Sync Service

Fetches issues from Linear to display on the dashboard.
Focuses on:
1. Issues assigned to the user (Human Work)
2. Blocking issues
3. High Priority issues
4. Active cycles

Output:
- Writes to kraliki/data/linear.json
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [LINEAR] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Config
LINEAR_URL = "https://api.linear.app/graphql"
LINEAR_API_KEY_PATH = "/home/adminmatej/github/secrets/linear_api_key.txt"

# Dynamically determine Kraliki directory
KRALIKI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(KRALIKI_DIR, "data", "linear.json")
SYNC_INTERVAL = 60  # seconds

def get_api_key():
    """Load Linear API key."""
    try:
        with open(LINEAR_API_KEY_PATH, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        key = os.getenv("LINEAR_API_TOKEN")
        if key: return key
        raise Exception(f"Linear API key not found at {LINEAR_API_KEY_PATH}")

def query_linear(query, variables=None):
    """Execute GraphQL query."""
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
        raise Exception(f"GraphQL error: {result['errors'][0]['message']}")

    return result

def fetch_issues():
    """Fetch relevant issues from Linear."""
    # filtering for active states (Todo, In Progress)
    # and either assigned to me OR urgent/high priority
    query = """
    query GetDashboardIssues {
        issues(
            filter: {
                state: { type: { in: ["started", "unstarted", "backlog"] } }
            }
            first: 30
            orderBy: updatedAt
        ) {
            nodes {
                id
                identifier
                title
                priority
                priorityLabel
                state {
                    name
                    type
                    color
                }
                assignee {
                    displayName
                    isMe
                }
                labels {
                    nodes {
                        name
                        color
                    }
                }
                url
                createdAt
            }
        }
        viewer {
            id
            name
        }
    }
    """
    
    result = query_linear(query)
    issues = result["data"]["issues"]["nodes"]
    viewer = result["data"]["viewer"]
    
    # Process issues
    processed = []
    
    human_count = 0
    blocker_count = 0
    
    for issue in issues:
        is_human = issue["assignee"] and issue["assignee"]["isMe"]
        is_blocker = issue["priority"] == 1 or any(l["name"].lower() == "blocker" for l in issue["labels"]["nodes"])
        
        if is_human: human_count += 1
        if is_blocker: blocker_count += 1
        
        processed.append({
            "id": issue["id"],
            "identifier": issue["identifier"],
            "title": issue["title"],
            "priority": issue["priority"],
            "priorityLabel": issue["priorityLabel"],
            "state": issue["state"]["name"],
            "stateColor": issue["state"]["color"],
            "assignee": issue["assignee"]["displayName"] if issue["assignee"] else "Unassigned",
            "isAssignedToMe": is_human,
            "labels": [l["name"] for l in issue["labels"]["nodes"]],
            "url": issue["url"]
        })
        
    return {
        "timestamp": datetime.now().isoformat(),
        "viewer": viewer["name"],
        "stats": {
            "total": len(processed),
            "human_assigned": human_count,
            "blockers": blocker_count
        },
        "issues": processed
    }

def run_sync():
    """Main sync loop."""
    log.info("Starting Linear Sync Service")
    
    while True:
        try:
            data = fetch_issues()
            
            # Atomic write
            temp_file = OUTPUT_FILE + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(temp_file, OUTPUT_FILE)
            
            log.info(f"Synced {len(data['issues'])} issues. Next sync in {SYNC_INTERVAL}s")
            
        except Exception as e:
            log.error(f"Sync error: {e}")
            
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    run_sync()
