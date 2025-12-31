#!/usr/bin/env python3
"""
Kraliki Task Manager

Simple file-based task queue for agents with Task Hierarchy (Boomerang pattern).

Usage:
  python3 task_manager.py list                    # List open tasks
  python3 task_manager.py list --type dev         # List dev tasks
  python3 task_manager.py claim DEV-001 agent-x   # Claim a task
  python3 task_manager.py complete DEV-001        # Mark complete
  python3 task_manager.py release DEV-001         # Release claim

Boomerang Pattern:
  python3 task_manager.py create-subtask PARENT-001 "Subtask title" --type dev
  python3 task_manager.py complete-subtask SUB-001 "Result summary"
  python3 task_manager.py get-subtasks PARENT-001
  python3 task_manager.py get-parent SUB-001
"""

import json
import argparse
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

TASKS_FILE = Path(__file__).parent / "queue.json"


@dataclass
class Task:
    """Task with optional parent/child relationships for Boomerang pattern."""
    id: str
    title: str
    type: str = "dev"
    priority: str = "medium"
    app: str = "general"
    status: str = "open"
    description: Optional[str] = None
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    completed_at: Optional[str] = None
    verified_at: Optional[str] = None
    blocked_reason: Optional[str] = None
    estimated_time: Optional[str] = None
    for_agent: Optional[str] = None
    # Boomerang pattern fields
    parent_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    result_summary: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create Task from dictionary, handling missing fields gracefully."""
        # Only use known fields
        known_fields = {
            'id', 'title', 'type', 'priority', 'app', 'status', 'description',
            'claimed_by', 'claimed_at', 'completed_at', 'verified_at',
            'blocked_reason', 'estimated_time', 'for_agent',
            'parent_id', 'subtasks', 'result_summary'
        }
        filtered = {k: v for k, v in data.items() if k in known_fields}
        # Ensure subtasks is a list
        if 'subtasks' not in filtered:
            filtered['subtasks'] = []
        return cls(**filtered)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values for cleaner JSON."""
        result = asdict(self)
        # Remove None values and empty lists for cleaner output
        return {k: v for k, v in result.items() if v is not None and v != []}


def load_tasks() -> Dict[str, Any]:
    """Load tasks from JSON file."""
    with open(TASKS_FILE) as f:
        return json.load(f)


def save_tasks(data: Dict[str, Any]) -> None:
    """Save tasks to JSON file with updated timestamp."""
    data["updated"] = datetime.now().isoformat()
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_task_by_id(task_id: str) -> Optional[Task]:
    """Get a single task by ID."""
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == task_id:
            return Task.from_dict(t)
    return None


def update_task_in_data(data: Dict[str, Any], task: Task) -> bool:
    """Update a task in the data structure."""
    for i, t in enumerate(data["tasks"]):
        if t["id"] == task.id:
            data["tasks"][i] = task.to_dict()
            return True
    return False


def generate_subtask_id(parent_id: str) -> str:
    """Generate a unique subtask ID based on parent."""
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"{parent_id}-SUB-{short_uuid}"


# =============================================================================
# Boomerang Pattern Methods
# =============================================================================

def create_subtask(parent_id: str, title: str, **kwargs) -> Optional[Task]:
    """
    Create a subtask under a parent task.

    This enables the Boomerang pattern where:
    - Orchestrator creates subtasks for delegation
    - Specialized agents complete subtasks with summaries
    - Orchestrator receives only summaries (not full context)
    """
    data = load_tasks()

    # Find parent task
    parent_task = None
    parent_idx = None
    for i, t in enumerate(data["tasks"]):
        if t["id"] == parent_id:
            parent_task = Task.from_dict(t)
            parent_idx = i
            break

    if parent_task is None:
        print(f"Parent task {parent_id} not found")
        return None

    # Create subtask
    subtask_id = generate_subtask_id(parent_id)
    subtask = Task(
        id=subtask_id,
        title=title,
        type=kwargs.get("type") or parent_task.type,
        priority=kwargs.get("priority") or parent_task.priority,
        app=kwargs.get("app") or parent_task.app,
        status="open",
        description=kwargs.get("description"),
        parent_id=parent_id,
        subtasks=[],
        for_agent=kwargs.get("for_agent")
    )

    # Update parent's subtasks list
    if "subtasks" not in data["tasks"][parent_idx]:
        data["tasks"][parent_idx]["subtasks"] = []
    data["tasks"][parent_idx]["subtasks"].append(subtask_id)

    # Add subtask to tasks list
    data["tasks"].append(subtask.to_dict())
    save_tasks(data)

    print(f"Created subtask: {subtask_id} under {parent_id}")
    return subtask


def complete_subtask(task_id: str, summary: str) -> bool:
    """
    Complete a subtask with a result summary.

    This:
    1. Marks the subtask as completed with result_summary
    2. Checks if all sibling subtasks are complete
    3. If all complete, marks parent as completed too (bubble up)

    The summary is what gets passed back to the orchestrator,
    enabling context compression in the Boomerang pattern.
    """
    data = load_tasks()

    # Find the subtask
    subtask = None
    subtask_idx = None
    for i, t in enumerate(data["tasks"]):
        if t["id"] == task_id:
            subtask = Task.from_dict(t)
            subtask_idx = i
            break

    if subtask is None:
        print(f"Task {task_id} not found")
        return False

    # Mark subtask as completed with summary
    subtask.status = "completed"
    subtask.completed_at = datetime.now().isoformat()
    subtask.result_summary = summary
    data["tasks"][subtask_idx] = subtask.to_dict()

    print(f"Completed subtask: {task_id}")
    print(f"Summary: {summary}")

    # If this is a subtask, check if all siblings are complete
    if subtask.parent_id:
        parent_task = None
        parent_idx = None
        for i, t in enumerate(data["tasks"]):
            if t["id"] == subtask.parent_id:
                parent_task = Task.from_dict(t)
                parent_idx = i
                break

        if parent_task:
            # Check all sibling subtasks
            all_complete = True
            sibling_summaries = []

            for sibling_id in parent_task.subtasks:
                for t in data["tasks"]:
                    if t["id"] == sibling_id:
                        sibling = Task.from_dict(t)
                        if sibling.status != "completed":
                            all_complete = False
                        elif sibling.result_summary:
                            sibling_summaries.append(f"- {sibling_id}: {sibling.result_summary}")
                        break

            # If all subtasks complete, mark parent as complete
            if all_complete and parent_task.subtasks:
                parent_task.status = "completed"
                parent_task.completed_at = datetime.now().isoformat()
                # Aggregate summaries for parent
                parent_task.result_summary = "All subtasks completed:\n" + "\n".join(sibling_summaries)
                data["tasks"][parent_idx] = parent_task.to_dict()
                print(f"All subtasks complete - parent {subtask.parent_id} marked as completed")

    save_tasks(data)
    return True


def get_subtasks(parent_id: str) -> List[Task]:
    """Get all subtasks for a parent task."""
    data = load_tasks()

    # Find parent task
    parent_task = None
    for t in data["tasks"]:
        if t["id"] == parent_id:
            parent_task = Task.from_dict(t)
            break

    if parent_task is None:
        print(f"Parent task {parent_id} not found")
        return []

    # Get all subtasks
    subtasks = []
    for subtask_id in parent_task.subtasks:
        for t in data["tasks"]:
            if t["id"] == subtask_id:
                subtasks.append(Task.from_dict(t))
                break

    return subtasks


def get_parent(task_id: str) -> Optional[Task]:
    """Get the parent task for a subtask."""
    data = load_tasks()

    # Find the task
    task = None
    for t in data["tasks"]:
        if t["id"] == task_id:
            task = Task.from_dict(t)
            break

    if task is None:
        print(f"Task {task_id} not found")
        return None

    if not task.parent_id:
        print(f"Task {task_id} has no parent")
        return None

    # Find parent
    for t in data["tasks"]:
        if t["id"] == task.parent_id:
            return Task.from_dict(t)

    print(f"Parent task {task.parent_id} not found")
    return None


# =============================================================================
# Original Task Manager Functions (preserved)
# =============================================================================

def list_tasks(task_type=None, status=None, include_blocked=False):
    data = load_tasks()
    tasks = data["tasks"]

    if task_type:
        tasks = [t for t in tasks if t["type"] == task_type]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    elif not include_blocked:
        # Default: show open tasks, exclude blocked unless specifically requested
        tasks = [t for t in tasks if t["status"] in ["open", "claimed"]]

    print(f"{'ID':<20} {'Priority':<8} {'Type':<6} {'App':<15} {'Title'}")
    print("-" * 90)
    for t in tasks:
        task_id = t['id']
        # Indicate subtasks with indent
        if t.get('parent_id'):
            task_id = "  -> " + task_id
        print(f"{task_id:<20} {t['priority']:<8} {t['type']:<6} {t['app']:<15} {t['title'][:35]}")
    print(f"\nTotal: {len(tasks)} tasks")


def claim_task(task_id, agent_name):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == task_id:
            if t["status"] != "open":
                print(f"Task {task_id} is not open (status: {t['status']})")
                return False
            t["status"] = "claimed"
            t["claimed_by"] = agent_name
            t["claimed_at"] = datetime.now().isoformat()
            save_tasks(data)
            print(f"Claimed: {task_id} by {agent_name}")
            return True
    print(f"Task {task_id} not found")
    return False


def complete_task(task_id):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["status"] = "completed"
            t["completed_at"] = datetime.now().isoformat()
            save_tasks(data)
            print(f"Completed: {task_id}")
            return True
    print(f"Task {task_id} not found")
    return False


def release_task(task_id):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["status"] = "open"
            t["claimed_by"] = None
            t.pop("claimed_at", None)
            save_tasks(data)
            print(f"Released: {task_id}")
            return True
    print(f"Task {task_id} not found")
    return False


def get_task(task_id):
    data = load_tasks()
    for t in data["tasks"]:
        if t["id"] == task_id:
            print(json.dumps(t, indent=2))
            return t
    print(f"Task {task_id} not found")
    return None


def main():
    parser = argparse.ArgumentParser(description="Kraliki Task Manager")
    parser.add_argument("action", choices=[
        "list", "claim", "complete", "release", "get",
        "create-subtask", "complete-subtask", "get-subtasks", "get-parent"
    ])
    parser.add_argument("task_id", nargs="?", help="Task ID")
    parser.add_argument("agent_or_title", nargs="?", help="Agent name (for claim) or title (for create-subtask) or summary (for complete-subtask)")
    parser.add_argument("--type", help="Filter by type or set subtask type (dev, biz, infra, e2e, human)")
    parser.add_argument("--blocked", action="store_true", help="Include blocked tasks")
    parser.add_argument("--status", help="Filter by status (open, claimed, completed, blocked)")
    parser.add_argument("--priority", help="Set subtask priority")
    parser.add_argument("--app", help="Set subtask app")
    parser.add_argument("--description", help="Set subtask description")
    parser.add_argument("--for-agent", help="Assign to specific agent")

    args = parser.parse_args()

    if args.action == "list":
        list_tasks(task_type=args.type, status=args.status, include_blocked=args.blocked)

    elif args.action == "claim":
        if not args.task_id or not args.agent_or_title:
            print("Usage: task_manager.py claim <task_id> <agent_name>")
            return
        claim_task(args.task_id, args.agent_or_title)

    elif args.action == "complete":
        if not args.task_id:
            print("Usage: task_manager.py complete <task_id>")
            return
        complete_task(args.task_id)

    elif args.action == "release":
        if not args.task_id:
            print("Usage: task_manager.py release <task_id>")
            return
        release_task(args.task_id)

    elif args.action == "get":
        if not args.task_id:
            print("Usage: task_manager.py get <task_id>")
            return
        get_task(args.task_id)

    # Boomerang pattern commands
    elif args.action == "create-subtask":
        if not args.task_id or not args.agent_or_title:
            print("Usage: task_manager.py create-subtask <parent_id> <title> [--type TYPE] [--priority PRIORITY] [--app APP] [--description DESC] [--for-agent AGENT]")
            return
        create_subtask(
            args.task_id,
            args.agent_or_title,
            type=args.type,
            priority=args.priority,
            app=args.app,
            description=args.description,
            for_agent=args.for_agent
        )

    elif args.action == "complete-subtask":
        if not args.task_id or not args.agent_or_title:
            print("Usage: task_manager.py complete-subtask <task_id> <summary>")
            return
        complete_subtask(args.task_id, args.agent_or_title)

    elif args.action == "get-subtasks":
        if not args.task_id:
            print("Usage: task_manager.py get-subtasks <parent_id>")
            return
        subtasks = get_subtasks(args.task_id)
        if subtasks:
            print(f"Subtasks of {args.task_id}:")
            for st in subtasks:
                status_icon = "[x]" if st.status == "completed" else "[ ]"
                print(f"  {status_icon} {st.id}: {st.title}")
                if st.result_summary:
                    print(f"      Summary: {st.result_summary}")
        else:
            print(f"No subtasks found for {args.task_id}")

    elif args.action == "get-parent":
        if not args.task_id:
            print("Usage: task_manager.py get-parent <task_id>")
            return
        parent = get_parent(args.task_id)
        if parent:
            print(f"Parent of {args.task_id}:")
            print(json.dumps(parent.to_dict(), indent=2))


if __name__ == "__main__":
    main()
