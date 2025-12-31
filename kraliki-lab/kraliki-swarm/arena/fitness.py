#!/usr/bin/env python3
"""
Agent Fitness Tracking System
Measures genome effectiveness for evolutionary selection.

Metrics:
- task_completion_rate: Did agent finish assigned work?
- code_quality_score: Did PRs pass review?
- token_efficiency: Token usage vs output quality
- coordination_score: Blackboard protocol compliance
- learning_score: Memory usage and value

Weighted fitness = task(30%) + quality(25%) + efficiency(20%) + coordination(15%) + learning(10%)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ARENA_DIR = Path(__file__).parent
DATA_DIR = ARENA_DIR.parent / "data" / "fitness"
AGENTS_FILE = DATA_DIR / "agents.json"

# Fitness weights (must sum to 1.0)
WEIGHTS = {
    "task_completion_rate": 0.30,
    "code_quality_score": 0.25,
    "token_efficiency": 0.20,
    "coordination_score": 0.15,
    "learning_score": 0.10,
}


def load_agents() -> dict:
    """Load all agent fitness data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if AGENTS_FILE.exists():
        return json.loads(AGENTS_FILE.read_text())
    return {"agents": {}, "reports": []}


def save_agents(data: dict) -> None:
    """Save agent fitness data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    AGENTS_FILE.write_text(json.dumps(data, indent=2))


def calculate_weighted_fitness(metrics: dict) -> float:
    """Calculate weighted fitness score from all metrics."""
    score = 0.0
    for metric, weight in WEIGHTS.items():
        value = metrics.get(metric, 0.0)
        score += value * weight
    return round(score, 2)


def calculate_task_completion_rate(agent_data: dict) -> float:
    """Calculate task completion rate (0-100)."""
    tasks_completed = agent_data.get("tasks_completed", 0)
    tasks_attempted = agent_data.get("tasks_attempted", 0)
    if tasks_attempted == 0:
        return 0.0
    return round((tasks_completed / tasks_attempted) * 100, 2)


def calculate_token_efficiency(agent_data: dict) -> float:
    """Calculate token efficiency score (0-100).

    Lower tokens per successful task = higher efficiency.
    Baseline: 10000 tokens/task = 50 score
    """
    tasks_completed = agent_data.get("tasks_completed", 0)
    total_tokens = agent_data.get("total_tokens", 0)

    if tasks_completed == 0 or total_tokens == 0:
        return 0.0

    tokens_per_task = total_tokens / tasks_completed
    # 5000 tokens/task = 100, 10000 = 50, 20000 = 25, etc.
    efficiency = min(100, (5000 / tokens_per_task) * 100)
    return round(efficiency, 2)


def get_agent_metrics(agent_id: str) -> dict:
    """Get current metrics for an agent."""
    data = load_agents()
    if agent_id not in data["agents"]:
        return None

    agent = data["agents"][agent_id]

    # Calculate derived metrics
    metrics = {
        "task_completion_rate": calculate_task_completion_rate(agent),
        "code_quality_score": agent.get("avg_quality_score", 0.0),
        "token_efficiency": calculate_token_efficiency(agent),
        "coordination_score": agent.get("coordination_score", 0.0),
        "learning_score": agent.get("learning_score", 0.0),
    }

    return metrics


def report_task(
    agent_id: str,
    task_id: str,
    success: bool,
    tokens_used: int = 0,
    quality_score: int = 0,
    coordination_used: bool = False,
    memory_used: bool = False,
) -> dict:
    """Report a task completion for fitness tracking."""
    data = load_agents()

    # Initialize agent if new
    if agent_id not in data["agents"]:
        data["agents"][agent_id] = {
            "created": datetime.now().isoformat(),
            "tasks_attempted": 0,
            "tasks_completed": 0,
            "total_tokens": 0,
            "quality_scores": [],
            "avg_quality_score": 0.0,
            "coordination_count": 0,
            "memory_count": 0,
            "coordination_score": 0.0,
            "learning_score": 0.0,
        }

    agent = data["agents"][agent_id]

    # Update task counts
    agent["tasks_attempted"] += 1
    if success:
        agent["tasks_completed"] += 1

    # Update tokens
    agent["total_tokens"] += tokens_used

    # Update quality score (rolling average of last 20)
    if quality_score > 0:
        agent["quality_scores"].append(quality_score)
        agent["quality_scores"] = agent["quality_scores"][-20:]  # Keep last 20
        agent["avg_quality_score"] = round(
            sum(agent["quality_scores"]) / len(agent["quality_scores"]), 2
        )

    # Update coordination score
    if coordination_used:
        agent["coordination_count"] += 1
    coord_rate = (agent["coordination_count"] / agent["tasks_attempted"]) * 100
    agent["coordination_score"] = min(100.0, round(coord_rate, 2))

    # Update learning score
    if memory_used:
        agent["memory_count"] += 1
    mem_rate = (agent["memory_count"] / agent["tasks_attempted"]) * 100
    agent["learning_score"] = min(100.0, round(mem_rate, 2))

    # Calculate weighted fitness
    metrics = {
        "task_completion_rate": calculate_task_completion_rate(agent),
        "code_quality_score": agent["avg_quality_score"],
        "token_efficiency": calculate_token_efficiency(agent),
        "coordination_score": agent["coordination_score"],
        "learning_score": agent["learning_score"],
    }
    agent["fitness_score"] = calculate_weighted_fitness(metrics)
    agent["last_report"] = datetime.now().isoformat()

    # Log the report
    report = {
        "time": datetime.now().isoformat(),
        "agent_id": agent_id,
        "task_id": task_id,
        "success": success,
        "tokens_used": tokens_used,
        "quality_score": quality_score,
    }
    data["reports"].insert(0, report)
    data["reports"] = data["reports"][:500]  # Keep last 500 reports

    save_agents(data)

    return {
        "agent_id": agent_id,
        "fitness_score": agent["fitness_score"],
        "metrics": metrics,
    }


def check_agent(agent_id: str) -> Optional[dict]:
    """Get fitness details for an agent."""
    data = load_agents()

    if agent_id not in data["agents"]:
        return None

    agent = data["agents"][agent_id]
    metrics = get_agent_metrics(agent_id)

    return {
        "agent_id": agent_id,
        "fitness_score": agent.get("fitness_score", 0.0),
        "metrics": metrics,
        "tasks_attempted": agent.get("tasks_attempted", 0),
        "tasks_completed": agent.get("tasks_completed", 0),
        "total_tokens": agent.get("total_tokens", 0),
        "created": agent.get("created"),
        "last_report": agent.get("last_report"),
    }


def get_leaderboard(limit: int = 10) -> list:
    """Get fitness leaderboard."""
    data = load_agents()

    ranked = []
    for agent_id, agent in data["agents"].items():
        ranked.append({
            "agent_id": agent_id,
            "fitness_score": agent.get("fitness_score", 0.0),
            "tasks_completed": agent.get("tasks_completed", 0),
            "tasks_attempted": agent.get("tasks_attempted", 0),
        })

    ranked.sort(key=lambda x: x["fitness_score"], reverse=True)
    return ranked[:limit]


def display_leaderboard(limit: int = 10) -> str:
    """Format leaderboard for display."""
    ranked = get_leaderboard(limit)

    lines = ["FITNESS LEADERBOARD", "=" * 60]

    if not ranked:
        lines.append("No fitness data yet. Report some tasks!")
        return "\n".join(lines)

    for i, agent in enumerate(ranked, 1):
        medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(i, f"{i}th")
        completion = agent["tasks_completed"]
        attempted = agent["tasks_attempted"]
        rate = (completion / attempted * 100) if attempted > 0 else 0
        lines.append(
            f"{medal:4} {agent['agent_id'][:30]:30} "
            f"Fitness: {agent['fitness_score']:5.1f}  "
            f"Tasks: {completion}/{attempted} ({rate:.0f}%)"
        )

    return "\n".join(lines)


def display_agent_check(agent_id: str) -> str:
    """Format agent check for display."""
    result = check_agent(agent_id)

    if not result:
        return f"Agent '{agent_id}' has no fitness data yet."

    lines = [
        f"FITNESS CHECK: {agent_id}",
        "=" * 50,
        f"Overall Fitness Score: {result['fitness_score']:.1f}",
        "",
        "Metric Breakdown:",
    ]

    metrics = result["metrics"]
    for metric, weight in WEIGHTS.items():
        value = metrics.get(metric, 0.0)
        contribution = value * weight
        lines.append(
            f"  {metric:25} {value:6.1f} x {weight:.0%} = {contribution:.1f}"
        )

    lines.extend([
        "",
        f"Tasks: {result['tasks_completed']}/{result['tasks_attempted']}",
        f"Tokens Used: {result['total_tokens']:,}",
        f"First Report: {result['created'][:10] if result['created'] else 'N/A'}",
        f"Last Report: {result['last_report'][:10] if result['last_report'] else 'N/A'}",
    ])

    return "\n".join(lines)


def parse_bool(value: str) -> bool:
    """Parse boolean from CLI argument."""
    return value.lower() in ("true", "1", "yes", "y")


def print_help():
    """Print help message."""
    print("""Agent Fitness Tracking System - Measures genome effectiveness

Usage: fitness.py <command> [args]

Commands:
  report      Report a task completion for fitness tracking
  check       Get fitness details for an agent
  leaderboard Show fitness leaderboard

Options for 'report':
  --agent AGENT_ID        Agent ID (required)
  --task TASK_ID          Task ID (required)
  --success true|false    Whether task succeeded (required)
  --tokens_used N         Tokens consumed (optional)
  --quality_score N       Quality score 0-100 (optional)
  --coordination          Flag: agent used blackboard (optional)
  --memory                Flag: agent used memory system (optional)

Fitness Weights:
  task_completion_rate: 30%
  code_quality_score:   25%
  token_efficiency:     20%
  coordination_score:   15%
  learning_score:       10%

Examples:
  fitness.py report --agent CC-builder-23:05.24.12.AA --task VD-123 --success true --tokens_used 5000 --quality_score 85
  fitness.py check CC-builder-23:05.24.12.AA
  fitness.py leaderboard 20
""")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "report":
        # Parse named arguments
        args = sys.argv[2:]
        agent_id = None
        task_id = None
        success = False
        tokens_used = 0
        quality_score = 0
        coordination_used = False
        memory_used = False

        i = 0
        while i < len(args):
            if args[i] == "--agent" and i + 1 < len(args):
                agent_id = args[i + 1]
                i += 2
            elif args[i] == "--task" and i + 1 < len(args):
                task_id = args[i + 1]
                i += 2
            elif args[i] == "--success" and i + 1 < len(args):
                success = parse_bool(args[i + 1])
                i += 2
            elif args[i] == "--tokens_used" and i + 1 < len(args):
                tokens_used = int(args[i + 1])
                i += 2
            elif args[i] == "--quality_score" and i + 1 < len(args):
                quality_score = int(args[i + 1])
                i += 2
            elif args[i] == "--coordination":
                coordination_used = True
                i += 1
            elif args[i] == "--memory":
                memory_used = True
                i += 1
            else:
                i += 1

        if not agent_id or not task_id:
            print("Error: --agent and --task are required")
            sys.exit(1)

        result = report_task(
            agent_id=agent_id,
            task_id=task_id,
            success=success,
            tokens_used=tokens_used,
            quality_score=quality_score,
            coordination_used=coordination_used,
            memory_used=memory_used,
        )

        status = "SUCCESS" if success else "FAILED"
        print(f"Reported: {agent_id} - {task_id} [{status}]")
        print(f"Fitness Score: {result['fitness_score']:.1f}")
        print(f"Metrics: {result['metrics']}")

    elif cmd == "check" and len(sys.argv) >= 3:
        agent_id = sys.argv[2]
        print(display_agent_check(agent_id))

    elif cmd == "leaderboard":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(display_leaderboard(limit))

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: report, check, leaderboard")
        sys.exit(1)
