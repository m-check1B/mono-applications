#!/usr/bin/env python3
"""Safety systems: Doom loop detection and consecutive mistake tracking.

From OpenCode and Cline research.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import json
import os

SAFETY_LOG = "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/logs/safety.json"


@dataclass
class DoomLoopDetector:
    """Detect when agent is stuck in a loop calling same tool repeatedly."""

    threshold: int = 3
    recent_calls: List[str] = field(default_factory=list)

    def check(self, tool_name: str, args: str) -> bool:
        """Check if we're in a doom loop.

        Returns True if loop detected (should terminate).
        """
        # Create signature from tool and args hash
        call_signature = f"{tool_name}:{hash(str(args))}"
        self.recent_calls.append(call_signature)

        # Keep only recent calls
        self.recent_calls = self.recent_calls[-self.threshold:]

        # Check if all recent calls are identical
        if len(self.recent_calls) == self.threshold:
            if len(set(self.recent_calls)) == 1:
                self._log_event("doom_loop", {
                    "tool": tool_name,
                    "repeated_calls": self.threshold
                })
                return True

        return False

    def reset(self):
        """Reset after successful different action."""
        self.recent_calls = []

    def _log_event(self, event_type: str, data: dict):
        """Log safety event."""
        log_safety_event(event_type, data)


@dataclass
class MistakeTracker:
    """Track consecutive failures and terminate if too many."""

    max_consecutive: int = 5
    count: int = 0
    last_error: Optional[str] = None
    errors: List[dict] = field(default_factory=list)

    def record_success(self):
        """Reset counter on success."""
        self.count = 0
        self.last_error = None

    def record_failure(self, error: str) -> bool:
        """Record failure. Returns True if should terminate."""
        self.count += 1
        self.last_error = error
        self.errors.append({
            "time": datetime.now().isoformat(),
            "error": error,
            "count": self.count
        })

        if self.count >= self.max_consecutive:
            self._log_event("max_mistakes", {
                "count": self.count,
                "last_error": error
            })
            return True
        return False

    def get_status(self) -> dict:
        return {
            "consecutive_failures": self.count,
            "last_error": self.last_error,
            "should_terminate": self.count >= self.max_consecutive,
            "recent_errors": self.errors[-5:]
        }

    def _log_event(self, event_type: str, data: dict):
        """Log safety event."""
        log_safety_event(event_type, data)


def log_safety_event(event_type: str, data: dict):
    """Log a safety event to file."""
    os.makedirs(os.path.dirname(SAFETY_LOG), exist_ok=True)

    events = []
    if os.path.exists(SAFETY_LOG):
        try:
            with open(SAFETY_LOG) as f:
                events = json.load(f)
        except:
            events = []

    events.append({
        "time": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    })

    # Keep last 1000 events
    events = events[-1000:]

    with open(SAFETY_LOG, "w") as f:
        json.dump(events, f, indent=2)


# Singleton instances for use across agents
_doom_detectors = {}
_mistake_trackers = {}


def get_doom_detector(agent_id: str) -> DoomLoopDetector:
    """Get or create doom loop detector for agent."""
    if agent_id not in _doom_detectors:
        _doom_detectors[agent_id] = DoomLoopDetector()
    return _doom_detectors[agent_id]


def get_mistake_tracker(agent_id: str) -> MistakeTracker:
    """Get or create mistake tracker for agent."""
    if agent_id not in _mistake_trackers:
        _mistake_trackers[agent_id] = MistakeTracker()
    return _mistake_trackers[agent_id]


def cleanup_agent(agent_id: str):
    """Clean up trackers when agent completes."""
    _doom_detectors.pop(agent_id, None)
    _mistake_trackers.pop(agent_id, None)


if __name__ == "__main__":
    # Test the safety systems
    print("Testing Doom Loop Detector...")
    detector = DoomLoopDetector()
    for i in range(5):
        result = detector.check("bash", "ls -la")
        print(f"  Call {i+1}: doom_loop={result}")

    print("\nTesting Mistake Tracker...")
    tracker = MistakeTracker()
    for i in range(6):
        result = tracker.record_failure(f"Error {i+1}")
        print(f"  Failure {i+1}: should_terminate={result}")
