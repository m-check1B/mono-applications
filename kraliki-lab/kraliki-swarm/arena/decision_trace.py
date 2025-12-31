#!/usr/bin/env python3
"""Decision Trace System for Kraliki Agents.

Captures and stores decision traces from agent runs for observability,
debugging, and learning from agent behavior.

Decision traces capture:
- What decision was made
- Why (reasoning/context)
- What alternatives were considered
- The outcome

VD-481: Add decision trace emission to Kraliki agent runs
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

ARENA_DIR = Path(__file__).parent
DATA_DIR = ARENA_DIR / "data"
TRACES_DIR = DATA_DIR / "traces"
TRACES_FILE = DATA_DIR / "decision_traces.json"


class DecisionType(str, Enum):
    """Types of decisions agents make."""
    TASK_SELECTION = "task_selection"
    IMPLEMENTATION_STRATEGY = "implementation_strategy"
    TOOL_CHOICE = "tool_choice"
    ERROR_HANDLING = "error_handling"
    COMPLETION = "completion"
    CLAIM = "claim"
    SKIP = "skip"
    DELEGATE = "delegate"
    ABORT = "abort"
    CUSTOM = "custom"


@dataclass
class DecisionTrace:
    """A single decision trace record."""
    trace_id: str
    timestamp: str
    agent_id: str
    decision_type: str
    context: Dict[str, Any]
    decision: str
    reasoning: str
    alternatives: List[str] = field(default_factory=list)
    confidence: float = 0.0
    outcome: Optional[str] = None
    duration_ms: Optional[int] = None
    linear_issue: Optional[str] = None
    genome: Optional[str] = None
    cli: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "DecisionTrace":
        """Create from dictionary."""
        return cls(**data)


def _ensure_dirs():
    """Ensure trace directories exist."""
    TRACES_DIR.mkdir(parents=True, exist_ok=True)


def _load_traces() -> Dict:
    """Load traces from file."""
    _ensure_dirs()
    if not TRACES_FILE.exists():
        return {"created": datetime.now().isoformat(), "traces": []}
    try:
        return json.loads(TRACES_FILE.read_text())
    except Exception as e:
        logger.error(f"Failed to load traces: {e}")
        return {"created": datetime.now().isoformat(), "traces": []}


def _save_traces(data: Dict):
    """Save traces to file."""
    TRACES_FILE.write_text(json.dumps(data, indent=2))


def _generate_trace_id(agent_id: str) -> str:
    """Generate unique trace ID."""
    now = datetime.now()
    timestamp = now.strftime("%H%M%S%f")[:10]
    return f"DT-{agent_id[:10]}-{timestamp}"


def emit(
    agent_id: str,
    decision_type: str,
    decision: str,
    reasoning: str,
    context: Optional[Dict[str, Any]] = None,
    alternatives: Optional[List[str]] = None,
    confidence: float = 0.0,
    linear_issue: Optional[str] = None,
    genome: Optional[str] = None,
    cli: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> DecisionTrace:
    """Emit a decision trace.

    Args:
        agent_id: ID of the agent making the decision
        decision_type: Type of decision (use DecisionType enum values)
        decision: The decision that was made
        reasoning: Why this decision was made
        context: Relevant context (inputs, state, etc.)
        alternatives: Other options that were considered
        confidence: 0.0-1.0 confidence in the decision
        linear_issue: Related Linear issue ID (e.g., VD-123)
        genome: Agent's genome name
        cli: CLI tool used (claude, opencode, etc.)
        metadata: Additional metadata

    Returns:
        The created DecisionTrace
    """
    trace = DecisionTrace(
        trace_id=_generate_trace_id(agent_id),
        timestamp=datetime.now().isoformat(),
        agent_id=agent_id,
        decision_type=decision_type,
        context=context or {},
        decision=decision,
        reasoning=reasoning,
        alternatives=alternatives or [],
        confidence=confidence,
        linear_issue=linear_issue,
        genome=genome,
        cli=cli,
        metadata=metadata or {},
    )

    # Store trace
    data = _load_traces()
    data["traces"].append(trace.to_dict())
    data["last_updated"] = datetime.now().isoformat()
    _save_traces(data)

    # Also save to per-agent trace file for easy retrieval
    agent_trace_file = TRACES_DIR / f"{agent_id}.json"
    agent_traces = []
    if agent_trace_file.exists():
        try:
            agent_traces = json.loads(agent_trace_file.read_text())
        except Exception:
            pass
    agent_traces.append(trace.to_dict())
    agent_trace_file.write_text(json.dumps(agent_traces, indent=2))

    logger.info(f"Decision trace emitted: {trace.trace_id} - {decision_type}: {decision[:50]}...")

    return trace


def update_outcome(trace_id: str, outcome: str, duration_ms: Optional[int] = None) -> bool:
    """Update a trace with its outcome.

    Args:
        trace_id: The trace ID to update
        outcome: The outcome of the decision (success, failure, partial, etc.)
        duration_ms: How long the decision execution took

    Returns:
        True if updated, False if not found
    """
    data = _load_traces()

    for trace in data["traces"]:
        if trace.get("trace_id") == trace_id:
            trace["outcome"] = outcome
            if duration_ms is not None:
                trace["duration_ms"] = duration_ms
            _save_traces(data)
            return True

    return False


def get_traces(
    agent_id: Optional[str] = None,
    decision_type: Optional[str] = None,
    linear_issue: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    """Query decision traces.

    Args:
        agent_id: Filter by agent ID
        decision_type: Filter by decision type
        linear_issue: Filter by Linear issue
        since: Only traces after this ISO timestamp
        limit: Max traces to return

    Returns:
        List of trace dicts
    """
    data = _load_traces()
    traces = data.get("traces", [])

    if agent_id:
        traces = [t for t in traces if t.get("agent_id") == agent_id]

    if decision_type:
        traces = [t for t in traces if t.get("decision_type") == decision_type]

    if linear_issue:
        traces = [t for t in traces if t.get("linear_issue") == linear_issue]

    if since:
        traces = [t for t in traces if t.get("timestamp", "") > since]

    return traces[-limit:]


def get_agent_traces(agent_id: str) -> List[Dict]:
    """Get all traces for a specific agent.

    Args:
        agent_id: The agent ID

    Returns:
        List of trace dicts
    """
    agent_trace_file = TRACES_DIR / f"{agent_id}.json"
    if agent_trace_file.exists():
        try:
            return json.loads(agent_trace_file.read_text())
        except Exception:
            pass
    return []


def get_stats() -> Dict:
    """Get decision trace statistics.

    Returns:
        Dict with trace counts, types, agents, etc.
    """
    data = _load_traces()
    traces = data.get("traces", [])

    by_type = {}
    by_agent = {}
    by_outcome = {}
    by_genome = {}

    for t in traces:
        # By type
        dtype = t.get("decision_type", "unknown")
        by_type[dtype] = by_type.get(dtype, 0) + 1

        # By agent
        agent = t.get("agent_id", "unknown")
        by_agent[agent] = by_agent.get(agent, 0) + 1

        # By outcome
        outcome = t.get("outcome") or "pending"
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1

        # By genome
        genome = t.get("genome") or "unknown"
        by_genome[genome] = by_genome.get(genome, 0) + 1

    # Time range
    timestamps = [t.get("timestamp", "") for t in traces if t.get("timestamp")]
    oldest = min(timestamps) if timestamps else None
    newest = max(timestamps) if timestamps else None

    return {
        "total_traces": len(traces),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "by_agent": dict(sorted(by_agent.items(), key=lambda x: -x[1])[:10]),
        "by_outcome": by_outcome,
        "by_genome": dict(sorted(by_genome.items(), key=lambda x: -x[1])[:10]),
        "oldest_trace": oldest,
        "newest_trace": newest,
    }


def cleanup(keep_days: int = 30, archive: bool = True) -> Dict:
    """Archive old traces and clean up.

    Args:
        keep_days: Keep traces from last N days
        archive: Whether to save archived traces

    Returns:
        Cleanup stats
    """
    from datetime import timedelta

    data = _load_traces()
    traces = data.get("traces", [])

    cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()

    old_traces = [t for t in traces if t.get("timestamp", "") < cutoff]
    recent_traces = [t for t in traces if t.get("timestamp", "") >= cutoff]

    archived_count = 0
    if archive and old_traces:
        archive_dir = DATA_DIR / "trace_archives"
        archive_dir.mkdir(exist_ok=True)
        archive_file = archive_dir / f"traces_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        archive_file.write_text(json.dumps({
            "archived_at": datetime.now().isoformat(),
            "cutoff_date": cutoff,
            "trace_count": len(old_traces),
            "traces": old_traces,
        }, indent=2))
        archived_count = len(old_traces)

    data["traces"] = recent_traces
    data["last_cleanup"] = datetime.now().isoformat()
    _save_traces(data)

    return {
        "archived": archived_count,
        "kept": len(recent_traces),
        "cutoff_date": cutoff,
    }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kraliki Decision Trace System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Emit command
    emit_parser = subparsers.add_parser("emit", help="Emit a decision trace")
    emit_parser.add_argument("agent_id", help="Agent ID")
    emit_parser.add_argument("decision_type", help="Decision type")
    emit_parser.add_argument("decision", help="The decision made")
    emit_parser.add_argument("-r", "--reasoning", required=True, help="Reasoning")
    emit_parser.add_argument("-i", "--issue", help="Linear issue ID")
    emit_parser.add_argument("-g", "--genome", help="Genome name")
    emit_parser.add_argument("-c", "--confidence", type=float, default=0.0, help="Confidence 0-1")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query traces")
    query_parser.add_argument("-a", "--agent", help="Filter by agent ID")
    query_parser.add_argument("-t", "--type", help="Filter by decision type")
    query_parser.add_argument("-i", "--issue", help="Filter by Linear issue")
    query_parser.add_argument("-l", "--limit", type=int, default=20, help="Max results")

    # Stats command
    subparsers.add_parser("stats", help="Show trace statistics")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Archive old traces")
    cleanup_parser.add_argument("-d", "--days", type=int, default=30, help="Keep last N days")
    cleanup_parser.add_argument("--no-archive", action="store_true", help="Don't archive")

    # Update outcome command
    update_parser = subparsers.add_parser("update", help="Update a trace outcome")
    update_parser.add_argument("trace_id_or_agent", help="Trace ID or agent ID (uses latest trace)")
    update_parser.add_argument("outcome", help="Outcome: success, failure, partial, complete, error")
    update_parser.add_argument("-d", "--duration", type=int, help="Duration in ms")

    # Last trace command
    last_parser = subparsers.add_parser("last", help="Get last trace for an agent")
    last_parser.add_argument("agent_id", help="Agent ID")

    args = parser.parse_args()

    if args.command == "emit":
        trace = emit(
            agent_id=args.agent_id,
            decision_type=args.decision_type,
            decision=args.decision,
            reasoning=args.reasoning,
            linear_issue=args.issue,
            genome=args.genome,
            confidence=args.confidence,
        )
        print(f"Emitted trace: {trace.trace_id}")

    elif args.command == "query":
        traces = get_traces(
            agent_id=args.agent,
            decision_type=args.type,
            linear_issue=args.issue,
            limit=args.limit,
        )
        for t in traces:
            print(f"[{t['timestamp'][:16]}] {t['agent_id']}: {t['decision_type']} - {t['decision'][:60]}...")

    elif args.command == "stats":
        stats = get_stats()
        print("=== DECISION TRACE STATISTICS ===")
        print(f"Total traces: {stats['total_traces']}")
        if stats['oldest_trace']:
            print(f"Oldest: {stats['oldest_trace'][:16]}")
            print(f"Newest: {stats['newest_trace'][:16]}")
        print("\nBy Type:")
        for dtype, count in stats['by_type'].items():
            print(f"  {dtype}: {count}")
        print("\nBy Outcome:")
        for outcome, count in stats['by_outcome'].items():
            print(f"  {outcome}: {count}")
        print("\nTop Agents:")
        for agent, count in list(stats['by_agent'].items())[:5]:
            print(f"  {agent}: {count}")

    elif args.command == "cleanup":
        result = cleanup(keep_days=args.days, archive=not args.no_archive)
        print("=== CLEANUP COMPLETE ===")
        print(f"Archived: {result['archived']} traces")
        print(f"Kept: {result['kept']} traces")
        print(f"Cutoff: {result['cutoff_date'][:16]}")

    elif args.command == "update":
        trace_id = args.trace_id_or_agent
        # If it looks like an agent ID (contains common patterns), find their last trace
        if not trace_id.startswith("DT-"):
            # It's an agent ID, find their latest trace
            traces = get_traces(agent_id=trace_id, limit=1)
            if traces:
                trace_id = traces[-1].get("trace_id")
                print(f"Using latest trace for {args.trace_id_or_agent}: {trace_id}")
            else:
                print(f"No traces found for agent: {args.trace_id_or_agent}")
                exit(1)

        if update_outcome(trace_id, args.outcome, args.duration):
            print(f"✓ Updated trace {trace_id} with outcome: {args.outcome}")
        else:
            print(f"✗ Trace not found: {trace_id}")
            exit(1)

    elif args.command == "last":
        traces = get_traces(agent_id=args.agent_id, limit=1)
        if traces:
            t = traces[-1]
            print(f"=== LAST TRACE FOR {args.agent_id} ===")
            print(f"Trace ID: {t['trace_id']}")
            print(f"Time: {t['timestamp'][:19]}")
            print(f"Type: {t['decision_type']}")
            print(f"Decision: {t['decision']}")
            print(f"Reasoning: {t['reasoning'][:100]}...")
            print(f"Outcome: {t.get('outcome') or 'pending'}")
            if t.get('linear_issue'):
                print(f"Linear: {t['linear_issue']}")
        else:
            print(f"No traces found for agent: {args.agent_id}")

    else:
        parser.print_help()
