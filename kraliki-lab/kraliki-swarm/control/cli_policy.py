#!/usr/bin/env python3
"""CLI policy and pause state helpers for swarm coordination."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

KRALIKI_DIR = Path(__file__).parent.parent
CLI_POLICY_FILE = KRALIKI_DIR / "config" / "cli_policy.json"
PAUSE_STATE_FILE = KRALIKI_DIR / "config" / "pause_state.json"


def load_cli_policy() -> dict:
    """Load CLI policy from disk (defaults to empty policy)."""
    try:
        if CLI_POLICY_FILE.exists():
            return json.loads(CLI_POLICY_FILE.read_text())
    except Exception:
        pass
    return {"clis": {}}


def save_cli_policy(policy: dict) -> None:
    """Persist CLI policy to disk."""
    policy["_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    CLI_POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    CLI_POLICY_FILE.write_text(json.dumps(policy, indent=2))


def load_pause_state() -> dict:
    """Load swarm pause state from disk."""
    try:
        if PAUSE_STATE_FILE.exists():
            return json.loads(PAUSE_STATE_FILE.read_text())
    except Exception:
        pass
    return {"paused": False}


def is_swarm_paused() -> bool:
    """Return True if the swarm is paused via dashboard."""
    return bool(load_pause_state().get("paused", False))


def _parse_disabled_until(value: str) -> Optional[datetime]:
    """Parse disabled_until timestamp values."""
    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except Exception:
        pass

    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue

    return None


def is_cli_enabled(cli: str, policy: Optional[dict] = None, auto_enable: bool = True) -> bool:
    """Return True if CLI is enabled by policy (auto-reenable if due)."""
    policy = policy or load_cli_policy()
    config = policy.get("clis", {}).get(cli, {})
    enabled = config.get("enabled", True)

    if enabled:
        return True

    disabled_until = config.get("disabled_until")
    if auto_enable and disabled_until:
        until = _parse_disabled_until(disabled_until)
        if until and datetime.now() >= until:
            config["enabled"] = True
            config["reason"] = "Auto-enabled after disabled_until"
            config.pop("disabled_until", None)
            policy.setdefault("clis", {})[cli] = config
            save_cli_policy(policy)
            return True

    return False


def get_enabled_clis(policy: Optional[dict] = None) -> list[str]:
    """Return list of CLIs currently enabled by policy."""
    policy = policy or load_cli_policy()
    enabled = []
    for cli in policy.get("clis", {}):
        if is_cli_enabled(cli, policy=policy):
            enabled.append(cli)
    return enabled
