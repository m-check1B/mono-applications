#!/usr/bin/env python3
"""Tests for the Decision Trace System.

VD-481: Add decision trace emission to Kraliki agent runs
"""

import os
import sys
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Add arena to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from decision_trace import (
    emit,
    get_traces,
    get_agent_traces,
    get_stats,
    update_outcome,
    cleanup,
    DecisionType,
    DecisionTrace,
    TRACES_FILE,
    TRACES_DIR,
    DATA_DIR,
)


def test_emit_trace():
    """Test emitting a decision trace."""
    print("Testing trace emission...")

    trace = emit(
        agent_id="test-agent-001",
        decision_type=DecisionType.TASK_SELECTION.value,
        decision="Selected task VD-123 for implementation",
        reasoning="Task matched agent capabilities and had high priority",
        context={"priority": "high", "labels": ["stream:asset-engine", "type:feature", "product:kraliki", "phase:agents"]},
        alternatives=["VD-456", "VD-789"],
        confidence=0.85,
        linear_issue="VD-123",
        genome="claude_builder",
        cli="claude",
    )

    assert trace.trace_id.startswith("DT-")
    assert trace.agent_id == "test-agent-001"
    assert trace.decision_type == "task_selection"
    assert trace.confidence == 0.85
    print(f"  ✓ Trace emitted: {trace.trace_id}")
    print("  Trace emission test PASSED")
    return True


def test_query_traces():
    """Test querying decision traces."""
    print("Testing trace querying...")

    # Emit a few test traces
    for i in range(3):
        emit(
            agent_id=f"query-test-agent-{i}",
            decision_type=DecisionType.IMPLEMENTATION_STRATEGY.value,
            decision=f"Test decision {i}",
            reasoning=f"Test reasoning {i}",
        )

    # Query all
    traces = get_traces(limit=10)
    assert len(traces) > 0
    print(f"  ✓ Found {len(traces)} traces")

    # Query by agent
    agent_traces = get_traces(agent_id="query-test-agent-0")
    assert len(agent_traces) >= 1
    print(f"  ✓ Found {len(agent_traces)} traces for query-test-agent-0")

    # Query by type
    type_traces = get_traces(decision_type="implementation_strategy")
    assert len(type_traces) >= 1
    print(f"  ✓ Found {len(type_traces)} traces of type implementation_strategy")

    print("  Trace querying test PASSED")
    return True


def test_update_outcome():
    """Test updating trace outcomes."""
    print("Testing outcome updates...")

    # Emit trace
    trace = emit(
        agent_id="outcome-test-agent",
        decision_type=DecisionType.COMPLETION.value,
        decision="Task completed",
        reasoning="All requirements met",
    )

    # Update outcome
    success = update_outcome(trace.trace_id, "success", duration_ms=5000)
    assert success
    print(f"  ✓ Outcome updated for {trace.trace_id}")

    # Verify update
    traces = get_traces(agent_id="outcome-test-agent", limit=1)
    if traces:
        latest = traces[-1]
        assert latest.get("outcome") == "success"
        assert latest.get("duration_ms") == 5000
        print("  ✓ Outcome verified in stored trace")

    print("  Outcome update test PASSED")
    return True


def test_get_stats():
    """Test statistics retrieval."""
    print("Testing statistics...")

    stats = get_stats()

    assert "total_traces" in stats
    assert "by_type" in stats
    assert "by_agent" in stats
    assert "by_outcome" in stats

    print(f"  ✓ Total traces: {stats['total_traces']}")
    print(f"  ✓ Decision types: {len(stats['by_type'])}")
    print(f"  ✓ Unique agents: {len(stats['by_agent'])}")

    print("  Statistics test PASSED")
    return True


def test_agent_trace_file():
    """Test per-agent trace files."""
    print("Testing per-agent trace files...")

    agent_id = "file-test-agent"

    # Emit trace
    emit(
        agent_id=agent_id,
        decision_type="custom",
        decision="Test file storage",
        reasoning="Testing per-agent files",
    )

    # Check file exists
    trace_file = TRACES_DIR / f"{agent_id}.json"
    assert trace_file.exists(), f"Agent trace file not created: {trace_file}"
    print(f"  ✓ Agent trace file exists: {trace_file}")

    # Load and verify
    traces = get_agent_traces(agent_id)
    assert len(traces) >= 1
    print(f"  ✓ Found {len(traces)} traces in agent file")

    print("  Per-agent trace file test PASSED")
    return True


def test_decision_trace_dataclass():
    """Test DecisionTrace dataclass."""
    print("Testing DecisionTrace dataclass...")

    trace = DecisionTrace(
        trace_id="DT-test-001",
        timestamp=datetime.now().isoformat(),
        agent_id="test-agent",
        decision_type="task_selection",
        context={"key": "value"},
        decision="Test decision",
        reasoning="Test reasoning",
        alternatives=["alt1", "alt2"],
        confidence=0.9,
    )

    # Test to_dict
    d = trace.to_dict()
    assert d["trace_id"] == "DT-test-001"
    assert d["confidence"] == 0.9
    print("  ✓ to_dict works correctly")

    # Test from_dict
    trace2 = DecisionTrace.from_dict(d)
    assert trace2.trace_id == trace.trace_id
    assert trace2.decision == trace.decision
    print("  ✓ from_dict works correctly")

    print("  DecisionTrace dataclass test PASSED")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Decision Trace System - Test Suite (VD-481)")
    print("=" * 60)
    print()

    tests = [
        test_decision_trace_dataclass,
        test_emit_trace,
        test_query_traces,
        test_update_outcome,
        test_get_stats,
        test_agent_trace_file,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✓ All tests passed! Decision trace system is ready.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please fix before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
