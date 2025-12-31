#!/usr/bin/env python3
"""
Evolution Engine for Agent Genetics
Implements mutation, crossover, and selection operations for genome evolution.

Mutation Types:
- skill_addition: Add a new skill to genome
- prompt_tuning: Modify instruction text
- priority_shift: Reorder task priorities
- context_addition: Add new context files

Crossover:
- Combine traits from two high-performing genomes
- Take skills from both parents
- Merge non-conflicting instructions

Selection:
- Use fitness scores from fitness.py
- Top 50% advance to next generation
- Bottom performers flagged for retirement
"""

import json
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

ARENA_DIR = Path(__file__).parent
KRALIKI_DIR = ARENA_DIR.parent
DATA_DIR = KRALIKI_DIR / "data" / "evolution"
PROPOSALS_FILE = DATA_DIR / "proposals.json"
HISTORY_FILE = DATA_DIR / "history.json"

# Import sibling modules
sys.path.insert(0, str(ARENA_DIR))
try:
    from fitness import get_leaderboard, check_agent
    from genome_registry import (
        load_registry,
        save_registry,
        get_genome,
        register_genome,
        add_mutation,
        list_genomes,
    )
except ImportError:
    # Fallback for standalone testing
    def get_leaderboard(limit=10):
        return []
    def check_agent(agent_id):
        return None
    def load_registry():
        return {"genomes": {}}
    def save_registry(data):
        pass
    def get_genome(genome_id):
        return None
    def register_genome(*args, **kwargs):
        return {}
    def add_mutation(genome_id, mutation):
        return None
    def list_genomes(**kwargs):
        return []


# Mutation types with descriptions
MUTATION_TYPES = {
    "skill_addition": {
        "description": "Add a new skill to genome",
        "weight": 0.3,
    },
    "prompt_tuning": {
        "description": "Modify instruction text",
        "weight": 0.3,
    },
    "priority_shift": {
        "description": "Reorder task priorities",
        "weight": 0.2,
    },
    "context_addition": {
        "description": "Add new context files",
        "weight": 0.2,
    },
}


def load_proposals() -> dict:
    """Load evolution proposals from disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PROPOSALS_FILE.exists():
        return json.loads(PROPOSALS_FILE.read_text())
    return {"proposals": [], "last_updated": None}


def save_proposals(data: dict) -> None:
    """Save evolution proposals to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    PROPOSALS_FILE.write_text(json.dumps(data, indent=2))


def load_history() -> dict:
    """Load evolution history from disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"events": [], "generations": 0, "last_evolution": None}


def save_history(data: dict) -> None:
    """Save evolution history to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2))


def generate_proposal_id() -> str:
    """Generate a unique proposal ID."""
    return f"prop_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:4]}"


def propose_mutation(
    genome_id: str,
    mutation_type: str,
    description: str,
    evidence: Optional[str] = None,
    proposed_by: Optional[str] = None,
) -> dict:
    """
    Propose a mutation for a genome.

    Args:
        genome_id: The genome to mutate
        mutation_type: One of skill_addition, prompt_tuning, priority_shift, context_addition
        description: What the mutation does
        evidence: Why this mutation should be applied
        proposed_by: Agent or human proposing the mutation

    Returns:
        The created proposal
    """
    data = load_proposals()

    # Validate genome exists
    genome = get_genome(genome_id)
    if not genome:
        return {"error": f"Genome '{genome_id}' not found"}

    # Validate mutation type
    if mutation_type not in MUTATION_TYPES:
        return {"error": f"Invalid mutation type '{mutation_type}'. Valid types: {list(MUTATION_TYPES.keys())}"}

    proposal = {
        "id": generate_proposal_id(),
        "genome_id": genome_id,
        "mutation_type": mutation_type,
        "description": description,
        "evidence": evidence,
        "proposed_by": proposed_by or "unknown",
        "status": "pending",
        "created": datetime.now().isoformat(),
        "genome_fitness_at_proposal": genome.get("fitness_score", 0.0),
    }

    data["proposals"].append(proposal)
    save_proposals(data)

    return proposal


def list_proposals(status_filter: Optional[str] = None) -> list:
    """List all proposals with optional status filter."""
    data = load_proposals()
    proposals = data.get("proposals", [])

    if status_filter:
        proposals = [p for p in proposals if p.get("status") == status_filter]

    return proposals


def get_proposal(proposal_id: str) -> Optional[dict]:
    """Get a single proposal by ID."""
    data = load_proposals()
    for proposal in data.get("proposals", []):
        if proposal.get("id") == proposal_id:
            return proposal
    return None


def apply_proposal(proposal_id: str) -> dict:
    """
    Apply a mutation proposal to its target genome.

    This adds the mutation to the genome's history and updates the proposal status.
    """
    data = load_proposals()

    proposal = None
    for p in data.get("proposals", []):
        if p.get("id") == proposal_id:
            proposal = p
            break

    if not proposal:
        return {"error": f"Proposal '{proposal_id}' not found"}

    if proposal.get("status") != "pending":
        return {"error": f"Proposal is not pending (status: {proposal.get('status')})"}

    genome_id = proposal.get("genome_id")
    mutation_desc = f"[{proposal.get('mutation_type')}] {proposal.get('description')}"

    # Apply mutation to genome registry
    result = add_mutation(genome_id, mutation_desc)
    if not result:
        return {"error": f"Failed to apply mutation to genome '{genome_id}'"}

    # Update proposal status
    proposal["status"] = "applied"
    proposal["applied_at"] = datetime.now().isoformat()
    save_proposals(data)

    # Log to history
    history = load_history()
    history["events"].append({
        "type": "mutation_applied",
        "proposal_id": proposal_id,
        "genome_id": genome_id,
        "mutation_type": proposal.get("mutation_type"),
        "description": proposal.get("description"),
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)

    return {
        "success": True,
        "proposal_id": proposal_id,
        "genome_id": genome_id,
        "mutation": mutation_desc,
    }


def reject_proposal(proposal_id: str, reason: Optional[str] = None) -> dict:
    """Reject a mutation proposal."""
    data = load_proposals()

    proposal = None
    for p in data.get("proposals", []):
        if p.get("id") == proposal_id:
            proposal = p
            break

    if not proposal:
        return {"error": f"Proposal '{proposal_id}' not found"}

    proposal["status"] = "rejected"
    proposal["rejected_at"] = datetime.now().isoformat()
    proposal["rejection_reason"] = reason
    save_proposals(data)

    return {"success": True, "proposal_id": proposal_id}


def crossover(genome_a_id: str, genome_b_id: str, child_name: Optional[str] = None) -> dict:
    """
    Create a hybrid genome from two parents.

    Combines:
    - Skills from both parents (union)
    - Takes CLI from parent A (primary)
    - Inherits higher fitness as starting point

    Args:
        genome_a_id: Primary parent genome ID
        genome_b_id: Secondary parent genome ID
        child_name: Optional name for child (auto-generated if not provided)

    Returns:
        The created child genome or error
    """
    genome_a = get_genome(genome_a_id)
    genome_b = get_genome(genome_b_id)

    if not genome_a:
        return {"error": f"Genome '{genome_a_id}' not found"}
    if not genome_b:
        return {"error": f"Genome '{genome_b_id}' not found"}

    # Determine CLI from primary parent
    cli = genome_a.get("cli", "claude")

    # Combine skills (union, removing duplicates)
    skills_a = set(genome_a.get("skills", []))
    skills_b = set(genome_b.get("skills", []))
    combined_skills = list(skills_a | skills_b)

    # Generate child name if not provided
    if not child_name:
        role_a = genome_a_id.split("_")[1] if "_" in genome_a_id else "hybrid"
        # Find next version number
        registry = load_registry()
        version = 1
        for gid in registry.get("genomes", {}).keys():
            if gid.startswith(f"{cli}_{role_a}"):
                try:
                    v = int(gid.split("_v")[-1])
                    version = max(version, v + 1)
                except (ValueError, IndexError):
                    pass
        child_name = f"{cli}_{role_a}_v{version}"

    # Create crossover description
    description = f"Crossover of {genome_a_id} x {genome_b_id}"

    # Register the new genome
    result = register_genome(
        genome_id=child_name,
        parent=genome_a_id,  # Primary parent as parent
        skills=combined_skills,
        cli=cli,
        description=description,
    )

    if "error" in result:
        return result

    # Add crossover mutation to track secondary parent
    add_mutation(child_name, f"Crossover with {genome_b_id} - inherited skills: {list(skills_b - skills_a)}")

    # Log to history
    history = load_history()
    history["events"].append({
        "type": "crossover",
        "parent_a": genome_a_id,
        "parent_b": genome_b_id,
        "child": child_name,
        "combined_skills": combined_skills,
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)

    return {
        "success": True,
        "child_id": child_name,
        "parent_a": genome_a_id,
        "parent_b": genome_b_id,
        "skills": combined_skills,
    }


def select_top_performers(top_percent: int = 50) -> dict:
    """
    Select top performing genomes for next generation.

    Args:
        top_percent: Percentage of genomes to keep (default 50%)

    Returns:
        Selection results with promoted and flagged genomes
    """
    genomes = list_genomes(active_only=True, sort_by="fitness_score")

    if not genomes:
        return {"error": "No genomes found"}

    total = len(genomes)
    cutoff_index = max(1, int(total * top_percent / 100))

    promoted = genomes[:cutoff_index]
    flagged_for_retirement = genomes[cutoff_index:]

    # Update registry to flag low performers
    registry = load_registry()
    for genome in flagged_for_retirement:
        gid = genome.get("genome_id")
        if gid in registry["genomes"]:
            registry["genomes"][gid]["flagged_for_retirement"] = True
            registry["genomes"][gid]["flagged_at"] = datetime.now().isoformat()
    save_registry(registry)

    # Log to history
    history = load_history()
    history["events"].append({
        "type": "selection",
        "total_genomes": total,
        "top_percent": top_percent,
        "promoted_count": len(promoted),
        "flagged_count": len(flagged_for_retirement),
        "promoted_ids": [g.get("genome_id") for g in promoted],
        "flagged_ids": [g.get("genome_id") for g in flagged_for_retirement],
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)

    return {
        "total": total,
        "top_percent": top_percent,
        "promoted": [
            {"genome_id": g.get("genome_id"), "fitness": g.get("fitness_score", 0)}
            for g in promoted
        ],
        "flagged_for_retirement": [
            {"genome_id": g.get("genome_id"), "fitness": g.get("fitness_score", 0)}
            for g in flagged_for_retirement
        ],
    }


def retire_genome(genome_id: str) -> dict:
    """Mark a genome as retired (inactive)."""
    registry = load_registry()

    if genome_id not in registry["genomes"]:
        return {"error": f"Genome '{genome_id}' not found"}

    registry["genomes"][genome_id]["active"] = False
    registry["genomes"][genome_id]["retired_at"] = datetime.now().isoformat()
    save_registry(registry)

    history = load_history()
    history["events"].append({
        "type": "retirement",
        "genome_id": genome_id,
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)

    return {"success": True, "genome_id": genome_id, "status": "retired"}


def run_evolution_cycle() -> dict:
    """
    Run a complete evolution cycle:
    1. Select top 50% performers
    2. Create crossovers from top pairs
    3. Propose random mutations for top genomes

    Returns:
        Summary of evolution cycle
    """
    history = load_history()
    generation = history.get("generations", 0) + 1

    # Step 1: Selection
    selection_result = select_top_performers(top_percent=50)
    if "error" in selection_result:
        return selection_result

    promoted = selection_result.get("promoted", [])

    # Step 2: Crossover top pairs
    crossovers = []
    if len(promoted) >= 2:
        # Pair top performers for crossover
        for i in range(0, min(len(promoted) - 1, 4), 2):  # Max 2 crossovers per cycle
            parent_a = promoted[i]["genome_id"]
            parent_b = promoted[i + 1]["genome_id"]
            result = crossover(parent_a, parent_b)
            if result.get("success"):
                crossovers.append(result)

    # Step 3: Propose random mutations for top genomes
    mutations_proposed = []
    for genome_info in promoted[:3]:  # Top 3 get mutation proposals
        genome_id = genome_info["genome_id"]

        # Pick random mutation type
        mutation_types = list(MUTATION_TYPES.keys())
        weights = [MUTATION_TYPES[mt]["weight"] for mt in mutation_types]
        mutation_type = random.choices(mutation_types, weights=weights, k=1)[0]

        proposal = propose_mutation(
            genome_id=genome_id,
            mutation_type=mutation_type,
            description=f"Auto-proposed {mutation_type} during evolution cycle {generation}",
            evidence=f"Top performer (fitness: {genome_info['fitness']:.1f})",
            proposed_by="evolution_engine",
        )
        if not proposal.get("error"):
            mutations_proposed.append(proposal)

    # Update history
    history["generations"] = generation
    history["last_evolution"] = datetime.now().isoformat()
    history["events"].append({
        "type": "evolution_cycle",
        "generation": generation,
        "selected": len(promoted),
        "retired": len(selection_result.get("flagged_for_retirement", [])),
        "crossovers": len(crossovers),
        "mutations_proposed": len(mutations_proposed),
        "timestamp": datetime.now().isoformat(),
    })
    save_history(history)

    return {
        "generation": generation,
        "selection": selection_result,
        "crossovers": crossovers,
        "mutations_proposed": mutations_proposed,
    }


def display_proposals(status_filter: Optional[str] = None) -> str:
    """Format proposals for display."""
    proposals = list_proposals(status_filter=status_filter)

    lines = ["EVOLUTION PROPOSALS", "=" * 70]

    if not proposals:
        lines.append("No proposals found.")
        return "\n".join(lines)

    lines.append(f"Total: {len(proposals)}")
    lines.append("")
    lines.append(f"{'ID':<25} {'GENOME':<25} {'TYPE':<15} {'STATUS':<10}")
    lines.append("-" * 70)

    for prop in proposals[:20]:  # Show last 20
        prop_id = prop.get("id", "?")[:25]
        genome = prop.get("genome_id", "?")[:25]
        mut_type = prop.get("mutation_type", "?")[:15]
        status = prop.get("status", "?")[:10]
        lines.append(f"{prop_id:<25} {genome:<25} {mut_type:<15} {status:<10}")

    return "\n".join(lines)


def display_proposal(proposal_id: str) -> str:
    """Format single proposal for display."""
    proposal = get_proposal(proposal_id)

    if not proposal:
        return f"Proposal '{proposal_id}' not found"

    lines = [
        f"PROPOSAL: {proposal['id']}",
        "=" * 50,
        f"Genome:       {proposal.get('genome_id')}",
        f"Type:         {proposal.get('mutation_type')}",
        f"Status:       {proposal.get('status')}",
        f"Created:      {proposal.get('created', 'N/A')[:19]}",
        f"Proposed by:  {proposal.get('proposed_by', 'unknown')}",
        "",
        f"Description:  {proposal.get('description')}",
        "",
        f"Evidence:     {proposal.get('evidence') or 'None provided'}",
    ]

    if proposal.get("applied_at"):
        lines.append(f"Applied at:   {proposal.get('applied_at')[:19]}")

    if proposal.get("rejected_at"):
        lines.append(f"Rejected at:  {proposal.get('rejected_at')[:19]}")
        lines.append(f"Reason:       {proposal.get('rejection_reason') or 'Not specified'}")

    return "\n".join(lines)


def display_history(limit: int = 10) -> str:
    """Format evolution history for display."""
    history = load_history()

    lines = ["EVOLUTION HISTORY", "=" * 70]
    lines.append(f"Total Generations: {history.get('generations', 0)}")
    lines.append(f"Last Evolution:    {history.get('last_evolution', 'Never')[:19] if history.get('last_evolution') else 'Never'}")
    lines.append("")
    lines.append("Recent Events:")
    lines.append("-" * 70)

    events = history.get("events", [])[-limit:]
    for event in reversed(events):
        timestamp = event.get("timestamp", "")[:19]
        event_type = event.get("type", "unknown")

        if event_type == "evolution_cycle":
            lines.append(f"[{timestamp}] Evolution Cycle #{event.get('generation')}")
            lines.append(f"    Selected: {event.get('selected')}, Retired: {event.get('retired')}, Crossovers: {event.get('crossovers')}")
        elif event_type == "crossover":
            lines.append(f"[{timestamp}] Crossover: {event.get('parent_a')} x {event.get('parent_b')} -> {event.get('child')}")
        elif event_type == "mutation_applied":
            lines.append(f"[{timestamp}] Mutation Applied: {event.get('genome_id')} - {event.get('description', '')[:40]}")
        elif event_type == "selection":
            lines.append(f"[{timestamp}] Selection: {event.get('promoted_count')} promoted, {event.get('flagged_count')} flagged")
        elif event_type == "retirement":
            lines.append(f"[{timestamp}] Retired: {event.get('genome_id')}")
        else:
            lines.append(f"[{timestamp}] {event_type}")

    return "\n".join(lines)


def print_usage():
    """Print CLI usage."""
    print("Usage: evolution.py <command> [args]")
    print("")
    print("Commands:")
    print("  propose --genome GENOME --mutation DESC [--type TYPE] [--evidence WHY]")
    print("  list-proposals [--status pending|applied|rejected]")
    print("  show-proposal PROPOSAL_ID")
    print("  apply PROPOSAL_ID")
    print("  reject PROPOSAL_ID [--reason REASON]")
    print("  crossover GENOME_A GENOME_B [--name CHILD_NAME]")
    print("  select [--top PERCENT]")
    print("  retire GENOME_ID")
    print("  evolve")
    print("  history [--limit N]")
    print("")
    print("Mutation Types:")
    for mt, info in MUTATION_TYPES.items():
        print(f"  {mt}: {info['description']}")
    print("")
    print("Examples:")
    print("  evolution.py propose --genome claude_builder_v1 --mutation 'Add Linear MCP usage' --evidence 'Improves task tracking'")
    print("  evolution.py list-proposals")
    print("  evolution.py apply prop_20251225120000_abc1")
    print("  evolution.py crossover claude_builder_v1 gemini_builder_v1")
    print("  evolution.py select --top 50")
    print("  evolution.py evolve")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "propose":
        # Parse named arguments
        args = sys.argv[2:]
        genome_id = None
        mutation_desc = None
        mutation_type = "prompt_tuning"
        evidence = None

        i = 0
        while i < len(args):
            if args[i] == "--genome" and i + 1 < len(args):
                genome_id = args[i + 1]
                i += 2
            elif args[i] == "--mutation" and i + 1 < len(args):
                mutation_desc = args[i + 1]
                i += 2
            elif args[i] == "--type" and i + 1 < len(args):
                mutation_type = args[i + 1]
                i += 2
            elif args[i] == "--evidence" and i + 1 < len(args):
                evidence = args[i + 1]
                i += 2
            else:
                i += 1

        if not genome_id or not mutation_desc:
            print("Error: --genome and --mutation are required")
            sys.exit(1)

        result = propose_mutation(
            genome_id=genome_id,
            mutation_type=mutation_type,
            description=mutation_desc,
            evidence=evidence,
        )

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"Proposal created: {result['id']}")
        print(f"  Genome: {result['genome_id']}")
        print(f"  Type: {result['mutation_type']}")
        print(f"  Description: {result['description']}")

    elif cmd == "list-proposals":
        status_filter = None
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            if idx + 1 < len(sys.argv):
                status_filter = sys.argv[idx + 1]
        print(display_proposals(status_filter=status_filter))

    elif cmd == "show-proposal" and len(sys.argv) >= 3:
        proposal_id = sys.argv[2]
        print(display_proposal(proposal_id))

    elif cmd == "apply" and len(sys.argv) >= 3:
        proposal_id = sys.argv[2]
        result = apply_proposal(proposal_id)

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"Mutation applied!")
        print(f"  Proposal: {result['proposal_id']}")
        print(f"  Genome: {result['genome_id']}")
        print(f"  Mutation: {result['mutation']}")

    elif cmd == "reject" and len(sys.argv) >= 3:
        proposal_id = sys.argv[2]
        reason = None
        if "--reason" in sys.argv:
            idx = sys.argv.index("--reason")
            if idx + 1 < len(sys.argv):
                reason = sys.argv[idx + 1]

        result = reject_proposal(proposal_id, reason=reason)

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"Proposal rejected: {proposal_id}")

    elif cmd == "crossover" and len(sys.argv) >= 4:
        genome_a = sys.argv[2]
        genome_b = sys.argv[3]
        child_name = None
        if "--name" in sys.argv:
            idx = sys.argv.index("--name")
            if idx + 1 < len(sys.argv):
                child_name = sys.argv[idx + 1]

        result = crossover(genome_a, genome_b, child_name=child_name)

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"Crossover successful!")
        print(f"  Parent A: {result['parent_a']}")
        print(f"  Parent B: {result['parent_b']}")
        print(f"  Child: {result['child_id']}")
        print(f"  Skills: {', '.join(result['skills'])}")

    elif cmd == "select":
        top_percent = 50
        if "--top" in sys.argv:
            idx = sys.argv.index("--top")
            if idx + 1 < len(sys.argv):
                top_percent = int(sys.argv[idx + 1])

        result = select_top_performers(top_percent=top_percent)

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"SELECTION RESULTS (Top {top_percent}%)")
        print("=" * 50)
        print(f"Total genomes: {result['total']}")
        print("")
        print("PROMOTED:")
        for g in result["promoted"]:
            print(f"  {g['genome_id']}: {g['fitness']:.1f}")
        print("")
        print("FLAGGED FOR RETIREMENT:")
        for g in result["flagged_for_retirement"]:
            print(f"  {g['genome_id']}: {g['fitness']:.1f}")

    elif cmd == "retire" and len(sys.argv) >= 3:
        genome_id = sys.argv[2]
        result = retire_genome(genome_id)

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"Genome retired: {genome_id}")

    elif cmd == "evolve":
        print("Running evolution cycle...")
        print("")
        result = run_evolution_cycle()

        if result.get("error"):
            print(f"Error: {result['error']}")
            sys.exit(1)

        print(f"EVOLUTION CYCLE COMPLETE - Generation {result['generation']}")
        print("=" * 50)

        selection = result.get("selection", {})
        print(f"Selected: {len(selection.get('promoted', []))} promoted")
        print(f"Flagged: {len(selection.get('flagged_for_retirement', []))} for retirement")

        crossovers = result.get("crossovers", [])
        print(f"Crossovers: {len(crossovers)} created")
        for c in crossovers:
            print(f"  {c['parent_a']} x {c['parent_b']} -> {c['child_id']}")

        mutations = result.get("mutations_proposed", [])
        print(f"Mutations proposed: {len(mutations)}")
        for m in mutations:
            print(f"  {m['id']}: {m['genome_id']} - {m['mutation_type']}")

    elif cmd == "history":
        limit = 10
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])
        print(display_history(limit=limit))

    else:
        print_usage()
        sys.exit(1)
