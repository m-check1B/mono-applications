import requests
import os
import sys
from pathlib import Path

def move_to_todo(identifier):
    key_path = Path.home() / "secrets" / "linear_api_key.txt"
    if not key_path.exists():
        print("Error: Linear API key not found")
        return

    api_key = key_path.read_text().strip()
    url = "https://api.linear.app/graphql"
    headers = {"Authorization": api_key, "Content-Type": "application/json"}

    # Get issue ID and Todo state ID
    query = """
    query($id: String!) {
      issue(id: $id) { id }
      workflowStates(filter: { name: { eq: "Todo" } }) {
        nodes { id }
      }
    }
    """
    resp = requests.post(url, headers=headers, json={"query": query, "variables": {"id": identifier}})
    data = resp.json().get("data", {})
    
    if not data.get("issue"):
        print(f"Issue {identifier} not found")
        return
        
    issue_id = data["issue"]["id"]
    state_id = data["workflowStates"]["nodes"][0]["id"]

    # Now update the issue
    mutation = """
    mutation IssueUpdate($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue { id identifier title state { name } }
      }
    }
    """
    variables = {"id": issue_id, "stateId": state_id}
    resp = requests.post(url, headers=headers, json={"query": mutation, "variables": variables})
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get("data", {}).get("issueUpdate", {}).get("success"):
            issue = result["data"]["issueUpdate"]["issue"]
            print(f"Moved {issue['identifier']} to Todo")
        else:
            print(f"Failed to move {issue_id}: {result}")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 move_to_todo.py [issue_identifier_or_id]")
    else:
        move_to_todo(sys.argv[1])
