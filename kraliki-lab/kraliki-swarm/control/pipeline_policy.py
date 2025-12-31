#!/usr/bin/env python3
"""Pipeline policy helpers for swarm coordination."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

KRALIKI_DIR = Path(__file__).parent.parent
PIPELINE_POLICY_FILE = KRALIKI_DIR / "config" / "pipeline_policy.json"
PIPELINE_TAXONOMY_FILE = KRALIKI_DIR / "config" / "pipeline_taxonomy.json"

DEFAULT_POLICY = {
    "pipelines": {
        "dev": {"enabled": True, "reason": "Default"},
        "biz": {"enabled": True, "reason": "Default"},
        "self_improve": {"enabled": True, "reason": "Default"},
    }
}

DEFAULT_TAXONOMY = {
    "always_allowed_roles": ["orchestrator", "caretaker"],
    "order": ["biz", "dev", "self_improve"],
    "pipelines": {
        "dev": {
            "roles": [
                "builder",
                "patcher",
                "tester",
                "integrator",
                "explorer",
                "dev_discovery",
                "reviewer",
                "promoter",
                "rnd",
            ],
            "labels": ["stream:asset-engine", "stream:apps"],
        },
        "biz": {
            "roles": [
                "business",
                "biz_discovery",
                "marketer",
                "researcher",
                "researcher_external",
            ],
            "labels": ["stream:cash-engine"],
        },
        "self_improve": {"roles": ["self_improver"], "labels": []},
    },
}


def load_pipeline_policy() -> dict:
    """Load pipeline policy from disk."""
    try:
        if PIPELINE_POLICY_FILE.exists():
            return json.loads(PIPELINE_POLICY_FILE.read_text())
    except Exception:
        pass
    return DEFAULT_POLICY


def load_pipeline_taxonomy() -> dict:
    """Load pipeline taxonomy from disk."""
    try:
        if PIPELINE_TAXONOMY_FILE.exists():
            return json.loads(PIPELINE_TAXONOMY_FILE.read_text())
    except Exception:
        pass
    return DEFAULT_TAXONOMY


def save_pipeline_policy(policy: dict) -> None:
    """Persist pipeline policy to disk."""
    policy["_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    PIPELINE_POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    PIPELINE_POLICY_FILE.write_text(json.dumps(policy, indent=2))


def is_pipeline_enabled(pipeline: str, policy: Optional[dict] = None) -> bool:
    """Return True if pipeline is enabled by policy."""
    policy = policy or load_pipeline_policy()
    config = policy.get("pipelines", {}).get(pipeline, {})
    return bool(config.get("enabled", True))


def _extract_role(genome: str) -> str:
    role = genome
    for prefix in ("claude_", "opencode_", "gemini_", "codex_", "grok_"):
        if role.startswith(prefix):
            role = role[len(prefix) :]
            break
    return role


def pipeline_for_role(role: str, taxonomy: Optional[dict] = None) -> Optional[str]:
    """Return pipeline name for a role."""
    taxonomy = taxonomy or load_pipeline_taxonomy()
    always_allowed = set(taxonomy.get("always_allowed_roles", []))
    if role in always_allowed:
        return None

    pipelines = taxonomy.get("pipelines", {})
    for name, config in pipelines.items():
        roles = set(config.get("roles", []))
        if role in roles:
            return name

    return "dev"


def get_pipeline_order(taxonomy: Optional[dict] = None) -> list[str]:
    """Return pipeline priority order."""
    taxonomy = taxonomy or load_pipeline_taxonomy()
    order = taxonomy.get("order") or []
    if order:
        return list(order)
    return ["biz", "dev", "self_improve"]


def get_enabled_label_groups(
    policy: Optional[dict] = None, taxonomy: Optional[dict] = None
) -> list[list[str]]:
    """Return label groups for enabled pipelines (priority order)."""
    policy = policy or load_pipeline_policy()
    taxonomy = taxonomy or load_pipeline_taxonomy()
    pipelines = taxonomy.get("pipelines", {})
    ordered = get_pipeline_order(taxonomy=taxonomy)

    label_groups: list[list[str]] = []
    seen = set()

    def add_group(pipeline_name: str) -> None:
        labels = pipelines.get(pipeline_name, {}).get("labels", [])
        labels = [label for label in labels if label]
        if labels:
            label_groups.append(labels)
            seen.add(pipeline_name)

    for pipeline_name in ordered:
        if pipeline_name in pipelines and is_pipeline_enabled(pipeline_name, policy=policy):
            add_group(pipeline_name)

    for pipeline_name in pipelines:
        if pipeline_name in seen:
            continue
        if is_pipeline_enabled(pipeline_name, policy=policy):
            add_group(pipeline_name)

    return label_groups


def build_guard_prompt(genome_name: str) -> str:
    """Build a non-negotiable pipeline guard prompt for agents."""
    policy = load_pipeline_policy()
    taxonomy = load_pipeline_taxonomy()
    role = _extract_role(genome_name)
    pipeline = pipeline_for_role(role, taxonomy=taxonomy)

    pipeline_names = list((taxonomy.get("pipelines") or {}).keys())
    if not pipeline_names:
        pipeline_names = ["dev", "biz", "self_improve"]

    enabled = [p for p in pipeline_names if is_pipeline_enabled(p, policy=policy)]
    disabled = [p for p in pipeline_names if not is_pipeline_enabled(p, policy=policy)]

    pipeline_label = pipeline or "always-allowed"
    allowed_list = ", ".join(enabled) if enabled else "none"
    blocked_list = ", ".join(disabled) if disabled else "none"

    return (
        "PIPELINE GUARD (NON-NEGOTIABLE):\n"
        f"- Your role: {role}\n"
        f"- Your pipeline: {pipeline_label}\n"
        f"- Allowed pipelines right now: {allowed_list}\n"
        f"- Disabled pipelines right now: {blocked_list}\n"
        "- RULE: Do NOT accept, brainstorm, or execute tasks outside allowed pipelines.\n"
        "- If asked to do blocked work, reply: PIPELINE_BLOCKED and stop.\n"
        f"- Policy is dynamic: re-check {PIPELINE_POLICY_FILE} before claiming tasks.\n"
        f"- Taxonomy reference: {PIPELINE_TAXONOMY_FILE}\n"
    )


def pipeline_for_genome(genome: str, taxonomy: Optional[dict] = None) -> Optional[str]:
    """Return pipeline name for a genome (or None if always allowed)."""
    if not genome:
        return None
    role = _extract_role(genome)
    return pipeline_for_role(role, taxonomy=taxonomy)


def is_genome_allowed(genome: str, policy: Optional[dict] = None) -> bool:
    """Return True if genome is allowed to spawn under policy."""
    taxonomy = load_pipeline_taxonomy()
    pipeline = pipeline_for_genome(genome, taxonomy=taxonomy)
    if pipeline is None:
        return True
    return is_pipeline_enabled(pipeline, policy=policy)
