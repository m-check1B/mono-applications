#!/usr/bin/env python3
"""
Session Harness for Kraliki Agents
===================================
Implements the Two-Phase Session Harness pattern from Anthropic:
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Enables context preservation and clean handoffs across agent sessions.

Usage:
    harness = SessionHarness("/github/applications/focus-kraliki")
    context = harness.startup_protocol()
    # ... agent does work ...
    harness.shutdown_protocol(feature_id="VD-123", passed=True, summary="Implemented auth")
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class SessionHarness:
    """Manages agent session lifecycle for context preservation."""

    def __init__(self, workspace: str, agent_id: Optional[str] = None):
        """
        Initialize session harness for a workspace.

        Args:
            workspace: Path to the workspace directory (e.g., /github/applications/focus-kraliki)
            agent_id: Optional agent identifier for logging
        """
        self.workspace = Path(workspace).resolve()
        self.agent_id = agent_id or os.environ.get("DARWIN_AGENT", "unknown-agent")

        # Session tracking files
        self.progress_path = self.workspace / "progress.txt"
        self.features_path = self.workspace / "features.json"  # Local cache, not source of truth
        self.init_script = self.workspace / "init.sh"

    def startup_protocol(self) -> Dict[str, Any]:
        """
        Run at session start. Returns context for agent to continue work.

        Protocol:
        1. Verify workspace exists
        2. Read git history for recent context
        3. Read progress file for narrative
        4. Run smoke test if init.sh exists
        5. Return aggregated context

        Returns:
            dict with keys: workspace_valid, git_history, progress, smoke_test_passed, ready
        """
        context = {
            "workspace_valid": False,
            "git_history": [],
            "progress": "",
            "smoke_test_passed": None,
            "ready": False,
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        # 1. Verify workspace
        if not self.workspace.exists():
            context["errors"].append(f"Workspace not found: {self.workspace}")
            return context
        context["workspace_valid"] = True

        # 2. Read git history (last 5 commits)
        context["git_history"] = self._get_git_history(limit=5)

        # 3. Read progress file
        context["progress"] = self._read_progress()

        # 4. Run smoke test if init.sh exists
        if self.init_script.exists():
            passed, output = self._run_smoke_test()
            context["smoke_test_passed"] = passed
            if not passed:
                context["errors"].append(f"Smoke test failed: {output[:200]}")
        else:
            context["smoke_test_passed"] = None  # No smoke test configured

        # 5. Determine readiness
        context["ready"] = (
            context["workspace_valid"] and
            context["smoke_test_passed"] in (True, None)  # None means no test configured
        )

        return context

    def shutdown_protocol(
        self,
        feature_id: str,
        passed: bool,
        summary: str,
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        Run at session end. Updates progress tracking and commits.

        Protocol:
        1. Append to progress.txt with session summary
        2. Git commit if requested
        3. Return completion status

        Args:
            feature_id: Linear issue ID or feature identifier
            passed: Whether the feature was completed successfully
            summary: Brief description of what was done
            commit: Whether to git commit (default True)

        Returns:
            dict with completion status
        """
        result = {
            "feature_id": feature_id,
            "passed": passed,
            "summary": summary,
            "committed": False,
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }

        # 1. Update progress.txt
        progress_entry = self._format_progress_entry(feature_id, passed, summary)
        self._append_progress(progress_entry)

        # 2. Git commit if requested
        if commit:
            try:
                status = "complete" if passed else "WIP"
                commit_msg = f"feat({feature_id}): {summary} [{status}]"
                self._git_commit(commit_msg)
                result["committed"] = True
            except Exception as e:
                result["errors"].append(f"Git commit failed: {str(e)}")

        return result

    def _get_git_history(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%s|%an|%ar"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0][:8],
                            "message": parts[1],
                            "author": parts[2],
                            "time": parts[3]
                        })
            return commits
        except Exception:
            return []

    def _read_progress(self) -> str:
        """Read progress.txt if it exists."""
        try:
            if self.progress_path.exists():
                return self.progress_path.read_text()[-2000:]  # Last 2000 chars
            return ""
        except Exception:
            return ""

    def _run_smoke_test(self) -> tuple[bool, str]:
        """Run init.sh smoke test."""
        try:
            result = subprocess.run(
                ["bash", str(self.init_script)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Smoke test timed out"
        except Exception as e:
            return False, str(e)

    def _format_progress_entry(self, feature_id: str, passed: bool, summary: str) -> str:
        """Format a progress entry."""
        status = "PASSED" if passed else "WIP"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"\n[{timestamp}] {self.agent_id} | {feature_id} [{status}]: {summary}"

    def _append_progress(self, entry: str) -> None:
        """Append entry to progress.txt."""
        try:
            with open(self.progress_path, "a") as f:
                f.write(entry + "\n")
        except Exception:
            pass  # Don't fail session on progress write error

    def _git_commit(self, message: str) -> None:
        """Git add and commit."""
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self.workspace,
            capture_output=True,
            timeout=30
        )
        subprocess.run(
            ["git", "commit", "-m", message, "--allow-empty"],
            cwd=self.workspace,
            capture_output=True,
            timeout=30
        )


def create_session_context(workspace: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to create session context for an agent.

    Usage in genomes:
        from arena.session_harness import create_session_context
        context = create_session_context("/github/applications/focus-kraliki", "darwin-claude-builder")
    """
    harness = SessionHarness(workspace, agent_id)
    return harness.startup_protocol()


def end_session(
    workspace: str,
    feature_id: str,
    passed: bool,
    summary: str,
    agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to end a session properly.

    Usage in genomes:
        from arena.session_harness import end_session
        result = end_session("/github/applications/focus-kraliki", "VD-123", True, "Implemented auth")
    """
    harness = SessionHarness(workspace, agent_id)
    return harness.shutdown_protocol(feature_id, passed, summary)


if __name__ == "__main__":
    # CLI interface for testing
    import sys

    if len(sys.argv) < 3:
        print("Usage: python session_harness.py <workspace> <start|end> [feature_id] [passed] [summary]")
        sys.exit(1)

    workspace = sys.argv[1]
    action = sys.argv[2]

    harness = SessionHarness(workspace)

    if action == "start":
        context = harness.startup_protocol()
        print(json.dumps(context, indent=2))
    elif action == "end":
        if len(sys.argv) < 6:
            print("Usage for end: python session_harness.py <workspace> end <feature_id> <passed> <summary>")
            sys.exit(1)
        feature_id = sys.argv[3]
        passed = sys.argv[4].lower() in ("true", "1", "yes")
        summary = sys.argv[5]
        result = harness.shutdown_protocol(feature_id, passed, summary)
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
