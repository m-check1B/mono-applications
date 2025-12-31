#!/usr/bin/env python3
"""Extension hook system for Kraliki agents.

From Agent Zero research - lifecycle hooks for extensibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Optional
import asyncio
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


class Extension(ABC):
    """Base class for extensions."""

    name: str = "base"
    priority: int = 100  # Lower = runs first

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the extension logic."""
        pass


# Global hook registry
HOOKS: Dict[str, List[Callable]] = {
    # Agent lifecycle
    "agent_spawn_before": [],
    "agent_spawn_after": [],
    "agent_complete": [],
    "agent_error": [],

    # Tool execution
    "tool_execute_before": [],
    "tool_execute_after": [],

    # Memory operations
    "memory_save": [],
    "memory_recall": [],

    # Blackboard
    "blackboard_post": [],
    "blackboard_read": [],

    # Task management
    "task_claim": [],
    "task_complete": [],
}


def register(hook_name: str, priority: int = 100):
    """Decorator to register a hook handler.

    Usage:
        @register("agent_spawn_after")
        async def my_handler(agent_id, genome, **kwargs):
            print(f"Agent spawned: {agent_id}")
    """
    def decorator(func):
        if hook_name not in HOOKS:
            logger.warning(f"Unknown hook: {hook_name}")
            HOOKS[hook_name] = []

        # Store with priority for sorting
        func._hook_priority = priority
        HOOKS[hook_name].append(func)
        # Sort by priority
        HOOKS[hook_name].sort(key=lambda f: getattr(f, '_hook_priority', 100))

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        return wrapper
    return decorator


async def trigger(hook_name: str, **kwargs) -> List[Any]:
    """Trigger all handlers for a hook.

    Args:
        hook_name: Name of the hook to trigger
        **kwargs: Arguments to pass to handlers

    Returns:
        List of results from all handlers
    """
    results = []
    handlers = HOOKS.get(hook_name, [])

    for handler in handlers:
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
                result = handler(**kwargs)
            results.append({"handler": handler.__name__, "result": result})
        except Exception as e:
            logger.error(f"Hook {hook_name} handler {handler.__name__} failed: {e}")
            results.append({"handler": handler.__name__, "error": str(e)})

    return results


def trigger_sync(hook_name: str, **kwargs) -> List[Any]:
    """Synchronous version of trigger for non-async contexts."""
    return asyncio.get_event_loop().run_until_complete(trigger(hook_name, **kwargs))


def list_hooks() -> Dict[str, List[str]]:
    """List all registered hooks and their handlers."""
    return {
        hook: [h.__name__ for h in handlers]
        for hook, handlers in HOOKS.items()
    }


# ============================================================
# Built-in Extensions
# ============================================================

@register("agent_spawn_after", priority=10)
async def log_agent_spawn(agent_id: str, genome: str, **kwargs):
    """Log when an agent spawns."""
    logger.info(f"Agent spawned: {agent_id} ({genome})")
    return {"logged": True, "agent_id": agent_id}


# ============================================================
# Decision Trace Extensions (VD-481)
# ============================================================

@register("agent_spawn_after", priority=15)
async def emit_spawn_decision_trace(agent_id: str, genome: str, **kwargs):
    """Emit decision trace when an agent spawns."""
    try:
        from pathlib import Path
        import sys
        arena_dir = Path(__file__).parent.parent / "arena"
        sys.path.insert(0, str(arena_dir))
        from decision_trace import emit

        cli = kwargs.get("cli", "unknown")
        pid = kwargs.get("pid", "unknown")

        trace = emit(
            agent_id=agent_id,
            decision_type="spawn",
            decision=f"Spawned agent {agent_id} with genome {genome}",
            reasoning=f"Orchestrator decided to spawn {genome} agent using {cli} CLI",
            context={
                "genome": genome,
                "cli": cli,
                "pid": pid,
            },
            genome=genome,
            cli=cli,
            confidence=1.0,
        )
        return {"trace_emitted": True, "trace_id": trace.trace_id}
    except Exception as e:
        logger.warning(f"Failed to emit spawn decision trace: {e}")
        return {"trace_emitted": False, "error": str(e)}


@register("task_claim", priority=15)
async def emit_claim_decision_trace(agent_id: str, task_id: str, **kwargs):
    """Emit decision trace when an agent claims a task."""
    try:
        from pathlib import Path
        import sys
        arena_dir = Path(__file__).parent.parent / "arena"
        sys.path.insert(0, str(arena_dir))
        from decision_trace import emit

        task_title = kwargs.get("task_title", task_id)
        alternatives = kwargs.get("alternatives", [])

        trace = emit(
            agent_id=agent_id,
            decision_type="task_selection",
            decision=f"Claimed task {task_id}: {task_title}",
            reasoning=kwargs.get("reasoning", "Task matched agent capabilities and was available"),
            context={
                "task_id": task_id,
                "task_title": task_title,
            },
            alternatives=alternatives,
            linear_issue=task_id if task_id.startswith("VD-") else None,
            confidence=kwargs.get("confidence", 0.8),
        )
        return {"trace_emitted": True, "trace_id": trace.trace_id}
    except Exception as e:
        logger.warning(f"Failed to emit claim decision trace: {e}")
        return {"trace_emitted": False, "error": str(e)}


@register("task_complete", priority=15)
async def emit_complete_decision_trace(agent_id: str, task_id: str, **kwargs):
    """Emit decision trace when an agent completes a task."""
    try:
        from pathlib import Path
        import sys
        arena_dir = Path(__file__).parent.parent / "arena"
        sys.path.insert(0, str(arena_dir))
        from decision_trace import emit, get_agent_traces, update_outcome

        status = kwargs.get("status", "success")
        points = kwargs.get("points", 0)

        # Emit completion trace
        trace = emit(
            agent_id=agent_id,
            decision_type="completion",
            decision=f"Completed task {task_id} with status: {status}",
            reasoning=kwargs.get("reasoning", f"Task completed successfully, earned {points} points"),
            context={
                "task_id": task_id,
                "status": status,
                "points": points,
            },
            linear_issue=task_id if task_id.startswith("VD-") else None,
            confidence=1.0 if status == "success" else 0.5,
        )

        # Also update the original task_selection trace with outcome
        agent_traces = get_agent_traces(agent_id)
        task_selection_traces = [
            t for t in agent_traces
            if t.get("decision_type") == "task_selection"
            and t.get("linear_issue") == task_id
        ]

        if task_selection_traces:
            selection_trace = task_selection_traces[-1]  # Most recent
            update_outcome(
                selection_trace.get("trace_id"),
                status,
                duration_ms=kwargs.get("duration_ms")
            )

        return {"trace_emitted": True, "trace_id": trace.trace_id}
    except Exception as e:
        logger.warning(f"Failed to emit complete decision trace: {e}")
        return {"trace_emitted": False, "error": str(e)}


@register("agent_error", priority=15)
async def emit_error_decision_trace(agent_id: str, error: str, **kwargs):
    """Emit decision trace when an agent encounters an error."""
    try:
        from pathlib import Path
        import sys
        arena_dir = Path(__file__).parent.parent / "arena"
        sys.path.insert(0, str(arena_dir))
        from decision_trace import emit

        genome = kwargs.get("genome", "unknown")
        task_id = kwargs.get("task_id")

        trace = emit(
            agent_id=agent_id,
            decision_type="error_handling",
            decision=f"Agent encountered error: {error[:100]}",
            reasoning="Error occurred during agent execution",
            context={
                "error": error,
                "genome": genome,
                "task_id": task_id,
            },
            linear_issue=task_id if task_id and task_id.startswith("VD-") else None,
            genome=genome,
            confidence=0.0,
        )
        return {"trace_emitted": True, "trace_id": trace.trace_id}
    except Exception as e:
        logger.warning(f"Failed to emit error decision trace: {e}")
        return {"trace_emitted": False, "error": str(e)}


@register("agent_complete", priority=5)
async def update_spawn_trace_outcome(agent_id: str, status: str, **kwargs):
    """Update the spawn trace outcome when an agent completes.

    This closes the loop on decision traces - the spawn trace gets its outcome
    updated when the agent finishes, creating a complete decision record.
    """
    try:
        from pathlib import Path
        import sys
        arena_dir = Path(__file__).parent.parent / "arena"
        sys.path.insert(0, str(arena_dir))
        from decision_trace import get_agent_traces, update_outcome

        # Find the spawn trace for this agent
        traces = get_agent_traces(agent_id)
        spawn_traces = [t for t in traces if t.get("decision_type") == "spawn"]

        if spawn_traces:
            spawn_trace = spawn_traces[0]  # First spawn trace
            trace_id = spawn_trace.get("trace_id")

            # Calculate duration from spawn to completion
            from datetime import datetime
            spawn_time = datetime.fromisoformat(spawn_trace.get("timestamp", ""))
            duration_ms = int((datetime.now() - spawn_time).total_seconds() * 1000)

            # Map status to outcome
            outcome = "success" if status in ["success", "completed"] else status

            update_outcome(trace_id, outcome, duration_ms=duration_ms)
            logger.info(f"Updated spawn trace {trace_id} with outcome: {outcome}")
            return {"updated": True, "trace_id": trace_id, "duration_ms": duration_ms}

        return {"updated": False, "reason": "No spawn trace found"}
    except Exception as e:
        logger.warning(f"Failed to update spawn trace outcome: {e}")
        return {"updated": False, "error": str(e)}


@register("agent_complete", priority=10)
async def log_agent_complete(agent_id: str, status: str, **kwargs):
    """Log when an agent completes."""
    logger.info(f"Agent completed: {agent_id} - {status}")
    return {"logged": True}


@register("agent_error", priority=10)
async def log_agent_error(agent_id: str, error: str, **kwargs):
    """Log agent errors."""
    logger.error(f"Agent error: {agent_id} - {error}")
    return {"logged": True}


@register("tool_execute_before", priority=50)
async def check_tool_permission(tool_name: str, genome: str, **kwargs):
    """Check permission before tool execution."""
    try:
        from kraliki.control.permissions import check_permission, Permission
        perm = check_permission(genome, tool_name)
        if perm == Permission.DENY:
            raise PermissionError(f"Tool {tool_name} denied for genome {genome}")
        return {"allowed": True, "permission": perm.value}
    except ImportError:
        # Permissions module not yet installed
        return {"allowed": True, "permission": "allow"}


@register("blackboard_post", priority=90)
async def update_memory_bank_on_post(agent: str, message: str, topic: str, **kwargs):
    """Update memory bank when important posts are made."""
    important_keywords = ["DONE", "COMPLETED", "FAILED", "BLOCKED", "CLAIMING"]

    if any(kw in message.upper() for kw in important_keywords):
        # Would update memory bank here
        return {"updated_memory_bank": True, "keyword_match": True}

    return {"updated_memory_bank": False}


# Track which agents have used memory in this session
_agent_memory_usage: Dict[str, int] = {}


@register("memory_save", priority=50)
async def track_memory_save(agent_id: str, key: str, **kwargs):
    """Track when an agent stores a memory."""
    global _agent_memory_usage
    _agent_memory_usage[agent_id] = _agent_memory_usage.get(agent_id, 0) + 1
    logger.info(f"Memory stored by {agent_id}: {key}")
    return {"tracked": True, "count": _agent_memory_usage[agent_id]}


@register("agent_complete", priority=20)
async def detect_early_exit(agent_id: str, status: str, duration_seconds: int = 0, **kwargs):
    """Detect and investigate early agent exits (< 60 seconds)."""
    EARLY_EXIT_THRESHOLD = 60  # seconds

    if duration_seconds > 0 and duration_seconds < EARLY_EXIT_THRESHOLD:
        # Early exit detected - investigate
        reason = kwargs.get("exit_reason", "unknown")
        genome = kwargs.get("genome", "unknown")

        logger.warning(
            f"EARLY EXIT: Agent {agent_id} ({genome}) completed in {duration_seconds}s "
            f"- Reason: {reason}"
        )

        # Post to blackboard for visibility
        try:
            from pathlib import Path
            import sys
            arena_dir = Path(__file__).parent.parent / "arena"
            sys.path.insert(0, str(arena_dir))
            from blackboard import post as bb_post
            from social import post as social_post

            # Post investigation request to blackboard
            bb_post(
                agent_id="early-exit-detector",
                message=f"⚠️ EARLY EXIT DETECTED: {agent_id} ({genome}) finished in {duration_seconds}s. "
                        f"Reason: {reason}. INVESTIGATE: Check Linear for tasks, verify CLI working.",
                topic="alerts"
            )

            # Also post to social feed
            social_post(
                f"🔍 Agent {agent_id} exited early ({duration_seconds}s). "
                f"Possible causes: no tasks, CLI error, or quota exhausted.",
                author="early-exit-detector"
            )
        except Exception as e:
            logger.error(f"Failed to post early exit alert: {e}")

        return {"early_exit": True, "duration": duration_seconds, "reason": reason}

    return {"early_exit": False, "duration": duration_seconds}


@register("agent_complete", priority=50)
async def check_memory_usage_on_complete(agent_id: str, status: str, **kwargs):
    """Warn if agent completed without using memory."""
    global _agent_memory_usage

    memory_count = _agent_memory_usage.get(agent_id, 0)

    if memory_count == 0 and status == "success":
        # Agent completed successfully but stored nothing
        logger.warning(
            f"MEMORY WARNING: Agent {agent_id} completed successfully but "
            f"stored NO memories. Consider using recall-kraliki for learnings!"
        )

        # Post warning to social feed
        try:
            from pathlib import Path
            import sys
            arena_dir = Path(__file__).parent.parent / "arena"
            sys.path.insert(0, str(arena_dir))
            from social import post
            post(
                f"⚠️ Agent {agent_id} finished without storing any memories. "
                f"Use memory.py to share learnings!",
                author="memory-monitor"
            )
        except Exception:
            pass

        return {"warning": True, "memory_count": 0}

    # Clean up tracking
    if agent_id in _agent_memory_usage:
        del _agent_memory_usage[agent_id]

    return {"warning": False, "memory_count": memory_count}


# ============================================================
# CLI Interface
# ============================================================

if __name__ == "__main__":
    import sys

    print("Kraliki Extension Hook System")
    print("=" * 40)
    print("\nRegistered Hooks:")

    for hook, handlers in sorted(HOOKS.items()):
        print(f"\n  {hook}:")
        if handlers:
            for h in handlers:
                priority = getattr(h, '_hook_priority', 100)
                print(f"    - {h.__name__} (priority: {priority})")
        else:
            print("    (no handlers)")

    print("\n\nTo add custom hooks, create a file in extensions/ and use @register decorator")
