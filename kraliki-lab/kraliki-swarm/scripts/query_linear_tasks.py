import requests
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from control import pipeline_policy

def query_linear():
    key_path = Path.home() / "secrets" / "linear_api_key.txt"
    if not key_path.exists():
        print("Error: Linear API key not found")
        return

    api_key = key_path.read_text().strip()
    url = "https://api.linear.app/graphql"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}

    policy = pipeline_policy.load_pipeline_policy()
    taxonomy = pipeline_policy.load_pipeline_taxonomy()
    label_groups = pipeline_policy.get_enabled_label_groups(
        policy=policy, taxonomy=taxonomy
    )
    if os.getenv("LINEAR_INCLUDE_LEGACY_LABELS", "0") == "1":
        for group in label_groups:
            if "stream:cash-engine" in group:
                group.append("GIN-BIZ")
            if "stream:asset-engine" in group:
                group.extend(["GIN-DEV", "GIN-FIX"])

    query = """
    query($labels: [String!]) {
      issues(filter: {
        state: { name: { nin: ["Done", "Canceled", "Completed"] } }
        labels: { name: { in: $labels } }
      }) {
        nodes {
          id
          identifier
          title
          description
          priority
          state { name }
          labels { nodes { name } }
          assignee { name }
        }
      }
    }
    """
    
    issues = []
    selected_group = None
    label_summary = "; ".join([", ".join(group) for group in label_groups]) or "none"
    for group in label_groups:
        response = requests.post(
            url,
            headers=headers,
            json={"query": query, "variables": {"labels": group}},
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])
        if issues:
            selected_group = group
            break

    if selected_group:
        print(f"Selected labels: {', '.join(selected_group)}")
        print(f"Found {len(issues)} issues:")
    else:
        print(f"Selected labels: none (configured: {label_summary})")
        print("Found 0 issues.")
    for issue in issues:
        labels = [l["name"] for l in issue["labels"]["nodes"]]
        assignee = issue["assignee"]["name"] if issue["assignee"] else "Unassigned"
        print(f"[{issue['identifier']}] {issue['title']} | State: {issue['state']['name']} | Labels: {', '.join(labels)} | Assignee: {assignee}")

if __name__ == "__main__":
    query_linear()
