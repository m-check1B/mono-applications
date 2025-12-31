#!/usr/bin/env python3
"""
Objective Verification System for Kraliki Agents

Instead of self-rating (subjective), agents run objective verification:
- Tests pass/fail
- Build succeeds
- Type checks pass
- Linter reports
- Linear issue has acceptance criteria met

This provides binary success/failure with evidence, not opinion.
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

KRALIKI_DIR = Path(__file__).parent.parent
GITHUB_DIR = KRALIKI_DIR.parent.parent
VERIFICATION_LOG = KRALIKI_DIR / "logs" / "verification.jsonl"


def run_command(cmd: list, cwd: Optional[str] = None, timeout: int = 120) -> dict:
    """Run a command and return structured result."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(GITHUB_DIR),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout[:2000] if result.stdout else "",
            "stderr": result.stderr[:2000] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout", "exit_code": -1}
    except Exception as e:
        return {"success": False, "error": str(e), "exit_code": -1}


def verify_tests(project_path: str) -> dict:
    """Run tests for a project and return pass/fail status."""
    path = Path(project_path)

    # Detect test framework
    if (path / "package.json").exists():
        # Node project - try npm test
        result = run_command(["npm", "test"], cwd=str(path))
        return {
            "type": "npm_test",
            "passed": result["success"],
            "details": result
        }
    elif (path / "pyproject.toml").exists() or (path / "pytest.ini").exists():
        # Python project - try pytest
        result = run_command(["python3", "-m", "pytest", "-v", "--tb=short"], cwd=str(path))
        return {
            "type": "pytest",
            "passed": result["success"],
            "details": result
        }
    elif (path / "Cargo.toml").exists():
        # Rust project
        result = run_command(["cargo", "test"], cwd=str(path))
        return {
            "type": "cargo_test",
            "passed": result["success"],
            "details": result
        }

    return {"type": "none", "passed": True, "details": {"note": "No test framework detected"}}


def verify_build(project_path: str) -> dict:
    """Run build for a project."""
    path = Path(project_path)

    if (path / "package.json").exists():
        # Check if build script exists
        try:
            pkg = json.loads((path / "package.json").read_text())
            if "build" in pkg.get("scripts", {}):
                result = run_command(["npm", "run", "build"], cwd=str(path))
                return {"type": "npm_build", "passed": result["success"], "details": result}
        except Exception:
            pass
        return {"type": "none", "passed": True, "details": {"note": "No build script"}}

    elif (path / "Cargo.toml").exists():
        result = run_command(["cargo", "build"], cwd=str(path))
        return {"type": "cargo_build", "passed": result["success"], "details": result}

    return {"type": "none", "passed": True, "details": {"note": "No build system detected"}}


def verify_typecheck(project_path: str) -> dict:
    """Run type checking."""
    path = Path(project_path)

    if (path / "tsconfig.json").exists():
        result = run_command(["npx", "tsc", "--noEmit"], cwd=str(path))
        return {"type": "typescript", "passed": result["success"], "details": result}

    elif (path / "pyproject.toml").exists():
        # Try mypy
        result = run_command(["python3", "-m", "mypy", "."], cwd=str(path))
        return {"type": "mypy", "passed": result["success"], "details": result}

    return {"type": "none", "passed": True, "details": {"note": "No type system detected"}}


def verify_lint(project_path: str) -> dict:
    """Run linter."""
    path = Path(project_path)

    if (path / "package.json").exists():
        # Try eslint
        result = run_command(["npx", "eslint", ".", "--max-warnings=0"], cwd=str(path))
        return {"type": "eslint", "passed": result["success"], "details": result}

    elif (path / "pyproject.toml").exists():
        # Try ruff
        result = run_command(["python3", "-m", "ruff", "check", "."], cwd=str(path))
        return {"type": "ruff", "passed": result["success"], "details": result}

    return {"type": "none", "passed": True, "details": {"note": "No linter detected"}}


def verify_git_clean(project_path: str) -> dict:
    """Check if git working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], cwd=str(project_path))
    is_clean = result["success"] and not result["stdout"].strip()
    return {
        "type": "git_status",
        "passed": is_clean,
        "details": {
            "clean": is_clean,
            "changes": result["stdout"].strip().split("\n") if result["stdout"].strip() else []
        }
    }


def run_verification(
    agent_id: str,
    task_id: str,
    project_path: str,
    checks: list = None
) -> dict:
    """
    Run full verification suite for an agent's completed work.

    Args:
        agent_id: The agent that completed the work
        task_id: Linear issue ID or task identifier
        project_path: Path to the project to verify
        checks: List of checks to run (default: all)

    Returns:
        Dict with overall pass/fail and individual check results
    """
    if checks is None:
        checks = ["tests", "build", "typecheck", "lint"]

    results = {
        "agent_id": agent_id,
        "task_id": task_id,
        "project": project_path,
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_passed": True
    }

    check_functions = {
        "tests": verify_tests,
        "build": verify_build,
        "typecheck": verify_typecheck,
        "lint": verify_lint,
        "git_clean": verify_git_clean,
    }

    for check in checks:
        if check in check_functions:
            result = check_functions[check](project_path)
            results["checks"][check] = result
            if not result["passed"]:
                results["overall_passed"] = False

    # Log result
    log_verification(results)

    return results


def log_verification(result: dict):
    """Append verification result to log file."""
    VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VERIFICATION_LOG, "a") as f:
        f.write(json.dumps(result) + "\n")


def get_verification_summary(agent_id: str = None, limit: int = 20) -> list:
    """Get recent verification results, optionally filtered by agent."""
    if not VERIFICATION_LOG.exists():
        return []

    results = []
    with open(VERIFICATION_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if agent_id is None or entry.get("agent_id") == agent_id:
                    results.append(entry)
            except Exception:
                continue

    # Return most recent
    return results[-limit:]


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify agent work")
    parser.add_argument("--agent", required=True, help="Agent ID")
    parser.add_argument("--task", required=True, help="Task/Issue ID")
    parser.add_argument("--project", required=True, help="Project path to verify")
    parser.add_argument("--checks", nargs="+", help="Specific checks to run")
    parser.add_argument("--summary", action="store_true", help="Show verification summary")

    args = parser.parse_args()

    if args.summary:
        results = get_verification_summary(args.agent)
        for r in results:
            status = "PASS" if r["overall_passed"] else "FAIL"
            print(f"[{status}] {r['timestamp'][:16]} {r['agent_id']} {r['task_id']}")
    else:
        result = run_verification(
            agent_id=args.agent,
            task_id=args.task,
            project_path=args.project,
            checks=args.checks
        )

        print(f"\nVerification Result: {'PASS' if result['overall_passed'] else 'FAIL'}")
        print("-" * 40)
        for check, data in result["checks"].items():
            status = "OK" if data["passed"] else "FAIL"
            print(f"  {check}: {status} ({data['type']})")
