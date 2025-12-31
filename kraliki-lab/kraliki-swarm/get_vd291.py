#!/usr/bin/env python3
import sys
import json

sys.path.insert(0, ".")
from integrations.linear_client import get_pending_tasks, get_task_by_id, graphql

# Try to get VD-291 by ID
tasks = get_pending_tasks(limit=100)

print("Searching for VD-291...")
for task in tasks:
    if task.get("identifier") == "VD-291":
        print("\n" + "=" * 80)
        print(f"TASK: {task['identifier']}")
        print(f"Title: {task['title']}")
        print(f"Priority: P{task['priority']}")
        print(f"State: {task['state']}")
        print(f"Labels: {', '.join(task.get('labels', []))}")
        print(f"\nDescription:")
        print(task.get("description", "No description"))
        print("=" * 80)
        break
else:
    print("VD-291 not found in pending tasks. Trying direct query...")

    # If not in pending, try searching for it
    result = graphql(
        """
        query SearchIssue($term: String!) {
            searchIssues(term: $term, first: 1) {
                nodes {
                    id
                    identifier
                    title
                    description
                    priority
                    state { name type }
                    labels { nodes { name } }
                }
            }
        }
    """,
        {"term": "VD-291"},
    )

    issues = result.get("data", {}).get("searchIssues", {}).get("nodes", [])
    if issues:
        issue = issues[0]
        labels = [l.get("name") for l in issue.get("labels", {}).get("nodes", [])]
        state = issue.get("state", {})
        print("\n" + "=" * 80)
        print(f"TASK: {issue.get('identifier')}")
        print(f"Title: {issue.get('title')}")
        print(f"Priority: P{issue.get('priority')}")
        print(f"State: {state.get('name')}")
        print(f"Labels: {', '.join(labels)}")
        print(f"\nDescription:")
        print(issue.get("description", "No description"))
        print("=" * 80)
    else:
        print("VD-291 not found")
