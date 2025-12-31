# Parallel Execution Pattern

**Purpose:** Execute multiple independent tasks simultaneously to maximize throughput.

## Overview

```
                    ┌──────────────┐
                    │ ORCHESTRATOR │
                    │   (Claude)   │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐
    │ Worker 1│       │ Worker 2│       │ Worker 3│
    │ (Gemini)│       │ (Codex) │       │ (Gemini)│
    └────┬────┘       └────┬────┘       └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │   COLLECT    │
                    │   RESULTS    │
                    └──────────────┘
```

## When to Use

- Tasks with no dependencies on each other
- Different aspects of the same feature (frontend + backend)
- Research tasks that can run independently
- Test suites that can parallelize

## When NOT to Use

- Sequential dependencies (A must complete before B)
- Shared resources that would conflict
- Tasks that modify the same files

## Orchestrator Instructions

**Prompt:**
```
You are orchestrating parallel execution. Your job is to:

1. Analyze the overall task
2. Identify independent subtasks
3. Assign each subtask to the appropriate worker
4. Collect and integrate results

For each subtask, specify:
- Worker: gemini|codex|claude
- Task description
- Expected output format
- How it integrates with other tasks
```

## Output Format

```yaml
parallel_execution:
  id: "exec_12345"
  total_tasks: 3

  tasks:
    - id: "task_1"
      worker: "gemini"
      description: "Build React login component"
      output_format: "React component file"
      integration: "Connects to auth API from task_2"

    - id: "task_2"
      worker: "codex"
      description: "Build authentication API"
      output_format: "Python API endpoints"
      integration: "Provides endpoints for task_1"

    - id: "task_3"
      worker: "gemini"
      description: "Write auth documentation"
      output_format: "Markdown docs"
      integration: "Documents task_1 and task_2"

  integration_points:
    - between: ["task_1", "task_2"]
      contract: |
        API Contract:
        POST /api/auth/login
        Request: { email: string, password: string }
        Response: { token: string, user: {...} }

  completion_criteria:
    - "All tasks completed"
    - "Integration points verified"
```

## Integration Contracts

Before parallel execution, define contracts between tasks:

```yaml
contracts:
  auth_api:
    provider: "task_2 (backend)"
    consumer: "task_1 (frontend)"
    specification:
      endpoint: "POST /api/auth/login"
      request:
        type: "object"
        properties:
          email: { type: "string", format: "email" }
          password: { type: "string", minLength: 8 }
      response:
        success:
          type: "object"
          properties:
            token: { type: "string" }
            user:
              type: "object"
              properties:
                id: { type: "string" }
                email: { type: "string" }
        error:
          type: "object"
          properties:
            code: { type: "string" }
            message: { type: "string" }
```

## Orchestration Script

```python
#!/usr/bin/env python3
"""
Parallel execution orchestration for Magic Box.
"""

import asyncio
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Task:
    id: str
    worker: str  # gemini, codex, claude
    description: str
    prompt_file: str
    depends_on: List[str] = None


@dataclass
class TaskResult:
    task_id: str
    success: bool
    output: str
    error: Optional[str] = None


async def run_worker(task: Task) -> TaskResult:
    """Run a single worker task."""
    worker_cmd = {
        "gemini": "gemini",
        "codex": "codex",
        "claude": "claude"
    }

    try:
        proc = await asyncio.create_subprocess_exec(
            worker_cmd[task.worker],
            "--prompt", task.prompt_file,
            task.description,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        return TaskResult(
            task_id=task.id,
            success=proc.returncode == 0,
            output=stdout.decode(),
            error=stderr.decode() if stderr else None
        )
    except Exception as e:
        return TaskResult(
            task_id=task.id,
            success=False,
            output="",
            error=str(e)
        )


async def execute_parallel(tasks: List[Task]) -> List[TaskResult]:
    """Execute independent tasks in parallel."""
    # Group tasks by dependency
    independent = [t for t in tasks if not t.depends_on]
    dependent = [t for t in tasks if t.depends_on]

    results = []

    # Run independent tasks in parallel
    if independent:
        print(f"Running {len(independent)} tasks in parallel...")
        parallel_results = await asyncio.gather(
            *[run_worker(task) for task in independent]
        )
        results.extend(parallel_results)

    # Run dependent tasks after their dependencies complete
    completed_ids = {r.task_id for r in results if r.success}

    for task in dependent:
        if all(dep in completed_ids for dep in task.depends_on):
            print(f"Running dependent task: {task.id}")
            result = await run_worker(task)
            results.append(result)
            if result.success:
                completed_ids.add(task.id)

    return results


# Example usage
async def main():
    tasks = [
        Task(
            id="frontend",
            worker="gemini",
            description="Build login component",
            prompt_file="prompts/workers/gemini/frontend-builder.md"
        ),
        Task(
            id="backend",
            worker="codex",
            description="Build auth API",
            prompt_file="prompts/workers/codex/backend-builder.md"
        ),
        Task(
            id="docs",
            worker="gemini",
            description="Write auth docs",
            prompt_file="prompts/workers/gemini/documentation.md"
        ),
        Task(
            id="integration",
            worker="claude",
            description="Verify frontend-backend integration",
            prompt_file="prompts/orchestrator/quality-control.md",
            depends_on=["frontend", "backend"]
        )
    ]

    results = await execute_parallel(tasks)

    print("\n=== Execution Results ===")
    for result in results:
        status = "SUCCESS" if result.success else "FAILED"
        print(f"{result.task_id}: {status}")
        if result.error:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Example: Full-Stack Feature

```yaml
feature: "User Profile Page"

parallel_execution:
  phase_1:  # Independent research
    - task: "Research profile UX patterns"
      worker: "gemini"

    - task: "Research profile API best practices"
      worker: "gemini"

  phase_2:  # Parallel build (with contract)
    contract:
      endpoint: "GET /api/users/:id"
      response: { id, name, email, avatar, bio, createdAt }

    - task: "Build profile API endpoint"
      worker: "codex"

    - task: "Build profile React component"
      worker: "gemini"

  phase_3:  # Integration & review
    - task: "Integration test"
      worker: "codex"
      depends_on: ["phase_2"]

    - task: "Security audit"
      worker: "codex"
      depends_on: ["phase_2"]

  phase_4:  # Documentation
    - task: "Write API docs"
      worker: "gemini"
      depends_on: ["phase_3"]
```

## Best Practices

1. **Define contracts first** - Workers need to agree on interfaces
2. **Maximize parallelism** - More parallel = faster completion
3. **Handle failures gracefully** - One failure shouldn't block others
4. **Collect all results** - Don't lose output from any worker
5. **Verify integration** - Parallel work must combine correctly
