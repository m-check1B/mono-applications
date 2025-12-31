#!/usr/bin/env python3
"""
Genome Registry for Agent Genetics Tracking
Tracks all genomes with metadata, lineage, mutations, and fitness scores.

Features:
- Auto-populate from existing genome files
- Track parent/child relationships (lineage)
- Store mutation history
- Integrate with fitness.py for score updates
- CLI for querying and managing genomes
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ARENA_DIR = Path(__file__).parent
KRALIKI_DIR = ARENA_DIR.parent
GENOMES_DIR = KRALIKI_DIR / "genomes"
DATA_DIR = KRALIKI_DIR / "data" / "genomes"
REGISTRY_FILE = DATA_DIR / "registry.json"

# CLI to lab prefix mapping
CLI_TO_LAB = {
    "claude": "CC",
    "opencode": "OC",
    "gemini": "GE",
    "codex": "CX",
}


def load_registry() -> dict:
    """Load genome registry from disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {"genomes": {}, "last_updated": None}


def save_registry(data: dict) -> None:
    """Save genome registry to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    REGISTRY_FILE.write_text(json.dumps(data, indent=2))


def parse_genome_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from genome file."""
    result = {
        "name": None,
        "description": None,
        "cli": None,
        "skills": [],
    }

    # Match YAML frontmatter between ---
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return result

    frontmatter = match.group(1)

    # Parse key: value pairs
    for line in frontmatter.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if key == 'name':
                result['name'] = value
            elif key == 'description':
                result['description'] = value
            elif key == 'cli':
                result['cli'] = value
            elif key == 'skills':
                # Skills can be inline list or multi-line
                if value.startswith('['):
                    # Inline list: [skill1, skill2]
                    skills = re.findall(r'[\w-]+', value)
                    result['skills'] = skills
                elif value == '':
                    # Multi-line list follows
                    pass
        elif line.startswith('- '):
            # Multi-line skill list item
            skill = line[2:].strip()
            if skill:
                result['skills'].append(skill)

    return result


def scan_genome_files() -> list:
    """Scan genome directory and return genome metadata."""
    genomes = []

    if not GENOMES_DIR.exists():
        return genomes

    for genome_file in sorted(GENOMES_DIR.glob("*.md")):
        content = genome_file.read_text()
        metadata = parse_genome_frontmatter(content)

        # Derive genome_id from filename (e.g., claude_builder.md -> claude_builder_v1)
        genome_id = genome_file.stem
        if not genome_id.endswith("_v1"):
            genome_id = f"{genome_id}_v1"

        # Determine CLI from filename or frontmatter
        cli = metadata.get('cli') or genome_file.stem.split('_')[0]

        genomes.append({
            "genome_id": genome_id,
            "file": str(genome_file),
            "name": metadata.get('name') or genome_file.stem,
            "description": metadata.get('description'),
            "cli": cli,
            "lab": CLI_TO_LAB.get(cli, "XX"),
            "skills": metadata.get('skills', []),
        })

    return genomes


def populate_from_files() -> dict:
    """Auto-populate registry from existing genome files."""
    registry = load_registry()
    scanned = scan_genome_files()

    added = 0
    updated = 0

    for genome in scanned:
        genome_id = genome["genome_id"]

        if genome_id not in registry["genomes"]:
            # New genome - add to registry
            registry["genomes"][genome_id] = {
                "genome_id": genome_id,
                "parent": None,
                "mutations": [],
                "created": datetime.now().isoformat()[:10],
                "fitness_score": 0.0,
                "tasks_completed": 0,
                "tasks_attempted": 0,
                "success_rate": 0.0,
                "skills": genome["skills"],
                "cli": genome["cli"],
                "lab": genome["lab"],
                "file": genome["file"],
                "name": genome["name"],
                "description": genome["description"],
                "version": 1,
                "active": True,
            }
            added += 1
        else:
            # Update file path and skills if changed
            existing = registry["genomes"][genome_id]
            if existing.get("file") != genome["file"]:
                existing["file"] = genome["file"]
                updated += 1
            if existing.get("skills") != genome["skills"]:
                existing["skills"] = genome["skills"]
                updated += 1

    save_registry(registry)
    return {"added": added, "updated": updated, "total": len(registry["genomes"])}


def get_genome(genome_id: str) -> Optional[dict]:
    """Get a single genome by ID."""
    registry = load_registry()
    return registry["genomes"].get(genome_id)


def register_genome(
    genome_id: str,
    parent: Optional[str] = None,
    skills: Optional[list] = None,
    cli: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Register a new genome."""
    registry = load_registry()

    if genome_id in registry["genomes"]:
        return {"error": f"Genome {genome_id} already exists"}

    # Derive version from ID
    version = 1
    if "_v" in genome_id:
        try:
            version = int(genome_id.split("_v")[-1])
        except ValueError:
            pass

    # Derive CLI from ID or parent
    if not cli:
        cli = genome_id.split("_")[0]

    # Inherit skills from parent if not specified
    if skills is None and parent and parent in registry["genomes"]:
        skills = registry["genomes"][parent].get("skills", [])

    genome = {
        "genome_id": genome_id,
        "parent": parent,
        "mutations": [],
        "created": datetime.now().isoformat()[:10],
        "fitness_score": 0.0,
        "tasks_completed": 0,
        "tasks_attempted": 0,
        "success_rate": 0.0,
        "skills": skills or [],
        "cli": cli,
        "lab": CLI_TO_LAB.get(cli, "XX"),
        "file": None,
        "name": genome_id,
        "description": description,
        "version": version,
        "active": True,
    }

    registry["genomes"][genome_id] = genome
    save_registry(registry)

    return genome


def add_mutation(genome_id: str, mutation: str) -> Optional[dict]:
    """Add a mutation to a genome's history."""
    registry = load_registry()

    if genome_id not in registry["genomes"]:
        return None

    genome = registry["genomes"][genome_id]
    genome["mutations"].append({
        "description": mutation,
        "date": datetime.now().isoformat()[:10],
    })

    save_registry(registry)
    return genome


def get_ancestry(genome_id: str) -> list:
    """Get the full ancestry chain for a genome."""
    registry = load_registry()
    ancestry = []
    current_id = genome_id

    visited = set()  # Prevent infinite loops

    while current_id and current_id not in visited:
        visited.add(current_id)
        genome = registry["genomes"].get(current_id)
        if not genome:
            break
        ancestry.append({
            "genome_id": genome["genome_id"],
            "created": genome.get("created"),
            "mutations": len(genome.get("mutations", [])),
            "fitness_score": genome.get("fitness_score", 0.0),
        })
        current_id = genome.get("parent")

    return ancestry


def get_descendants(genome_id: str) -> list:
    """Get all genomes that descended from this one."""
    registry = load_registry()
    descendants = []

    for gid, genome in registry["genomes"].items():
        if genome.get("parent") == genome_id:
            descendants.append({
                "genome_id": gid,
                "created": genome.get("created"),
                "fitness_score": genome.get("fitness_score", 0.0),
            })

    return descendants


def update_fitness_from_tracker(genome_id: str) -> Optional[dict]:
    """Update genome fitness from fitness.py agent data."""
    registry = load_registry()

    if genome_id not in registry["genomes"]:
        return None

    genome = registry["genomes"][genome_id]

    # Load fitness data
    fitness_file = KRALIKI_DIR / "data" / "fitness" / "agents.json"
    if not fitness_file.exists():
        return genome

    fitness_data = json.loads(fitness_file.read_text())

    # Find matching agent entries by genome name pattern
    # Agents are named like CC-builder-23:05.24.12.AA
    # Genomes are named like claude_builder_v1

    # Extract role from genome_id (e.g., claude_builder_v1 -> builder)
    parts = genome_id.replace("_v1", "").replace("_v2", "").split("_")
    if len(parts) >= 2:
        role = "_".join(parts[1:])
        cli = parts[0]
        lab = CLI_TO_LAB.get(cli, "XX")

        # Find agents matching this genome
        total_completed = 0
        total_attempted = 0
        fitness_scores = []

        for agent_id, agent_data in fitness_data.get("agents", {}).items():
            # Check if agent matches this genome's lab and role
            if agent_id.startswith(f"{lab}-{role}"):
                total_completed += agent_data.get("tasks_completed", 0)
                total_attempted += agent_data.get("tasks_attempted", 0)
                if agent_data.get("fitness_score", 0) > 0:
                    fitness_scores.append(agent_data["fitness_score"])

        # Update genome with aggregated data
        genome["tasks_completed"] = total_completed
        genome["tasks_attempted"] = total_attempted
        if total_attempted > 0:
            genome["success_rate"] = round(total_completed / total_attempted, 4)
        if fitness_scores:
            genome["fitness_score"] = round(sum(fitness_scores) / len(fitness_scores), 2)

    save_registry(registry)
    return genome


def list_genomes(
    cli_filter: Optional[str] = None,
    active_only: bool = True,
    sort_by: str = "fitness_score",
) -> list:
    """List all genomes with optional filtering."""
    registry = load_registry()
    genomes = list(registry["genomes"].values())

    # Filter by CLI
    if cli_filter:
        genomes = [g for g in genomes if g.get("cli") == cli_filter]

    # Filter active only
    if active_only:
        genomes = [g for g in genomes if g.get("active", True)]

    # Sort
    if sort_by == "fitness_score":
        genomes.sort(key=lambda x: x.get("fitness_score", 0), reverse=True)
    elif sort_by == "tasks_completed":
        genomes.sort(key=lambda x: x.get("tasks_completed", 0), reverse=True)
    elif sort_by == "created":
        genomes.sort(key=lambda x: x.get("created", ""), reverse=True)
    elif sort_by == "name":
        genomes.sort(key=lambda x: x.get("genome_id", ""))

    return genomes


def display_list(cli_filter: Optional[str] = None) -> str:
    """Format genome list for display."""
    genomes = list_genomes(cli_filter=cli_filter)

    lines = ["GENOME REGISTRY", "=" * 70]
    lines.append(f"Total genomes: {len(genomes)}")
    lines.append("")
    lines.append(f"{'GENOME ID':<35} {'CLI':<8} {'FITNESS':>8} {'TASKS':>8} {'SKILLS'}")
    lines.append("-" * 70)

    for genome in genomes:
        genome_id = genome.get("genome_id", "")[:35]
        cli = genome.get("cli", "?")[:8]
        fitness = genome.get("fitness_score", 0.0)
        tasks = genome.get("tasks_completed", 0)
        skills = ", ".join(genome.get("skills", [])[:3])
        if len(genome.get("skills", [])) > 3:
            skills += "..."

        lines.append(f"{genome_id:<35} {cli:<8} {fitness:>8.1f} {tasks:>8} {skills}")

    return "\n".join(lines)


def display_genome(genome_id: str) -> str:
    """Format genome details for display."""
    genome = get_genome(genome_id)

    if not genome:
        return f"Genome '{genome_id}' not found"

    lines = [
        f"GENOME: {genome['genome_id']}",
        "=" * 50,
        f"CLI:         {genome.get('cli', 'N/A')}",
        f"Lab:         {genome.get('lab', 'N/A')}",
        f"Version:     {genome.get('version', 1)}",
        f"Created:     {genome.get('created', 'N/A')}",
        f"Parent:      {genome.get('parent') or 'None (root)'}",
        f"Active:      {genome.get('active', True)}",
        "",
        f"Fitness:     {genome.get('fitness_score', 0.0):.1f}",
        f"Success:     {genome.get('success_rate', 0.0):.1%}",
        f"Tasks:       {genome.get('tasks_completed', 0)}/{genome.get('tasks_attempted', 0)}",
        "",
        f"Skills:      {', '.join(genome.get('skills', [])) or 'None'}",
        "",
        f"Description: {genome.get('description') or 'N/A'}",
        f"File:        {genome.get('file') or 'N/A'}",
    ]

    mutations = genome.get("mutations", [])
    if mutations:
        lines.append("")
        lines.append("Mutations:")
        for mut in mutations[-5:]:  # Show last 5
            lines.append(f"  - [{mut.get('date', '?')}] {mut.get('description', '?')}")

    descendants = get_descendants(genome_id)
    if descendants:
        lines.append("")
        lines.append(f"Descendants ({len(descendants)}):")
        for desc in descendants[:5]:
            lines.append(f"  - {desc['genome_id']} (fitness: {desc['fitness_score']:.1f})")

    return "\n".join(lines)


def display_ancestry(genome_id: str) -> str:
    """Format ancestry chain for display."""
    ancestry = get_ancestry(genome_id)

    if not ancestry:
        return f"Genome '{genome_id}' not found"

    lines = [f"LINEAGE: {genome_id}", "=" * 50]

    for i, ancestor in enumerate(ancestry):
        prefix = "  " * i
        arrow = "" if i == 0 else "-> "
        mut_count = ancestor.get("mutations", 0)
        lines.append(
            f"{prefix}{arrow}{ancestor['genome_id']} "
            f"(fitness: {ancestor['fitness_score']:.1f}, mutations: {mut_count})"
        )

    if len(ancestry) == 1:
        lines.append("")
        lines.append("This is a root genome (no ancestors).")

    return "\n".join(lines)


def print_usage():
    """Print CLI usage."""
    print("Usage: genome_registry.py <command> [args]")
    print("")
    print("Commands:")
    print("  list [--cli CLI]               List all genomes")
    print("  show GENOME_ID                 Show genome details")
    print("  ancestry GENOME_ID             Show lineage")
    print("  register GENOME_ID [--parent P] [--skills S1,S2] [--cli CLI]")
    print("  update GENOME_ID               Update fitness from fitness.py")
    print("  update-all                     Update fitness for all genomes")
    print("  populate                       Auto-populate from genome files")
    print("  mutate GENOME_ID DESCRIPTION   Add mutation to history")
    print("")
    print("Examples:")
    print("  genome_registry.py list")
    print("  genome_registry.py list --cli claude")
    print("  genome_registry.py show claude_builder_v1")
    print("  genome_registry.py ancestry claude_builder_v2")
    print("  genome_registry.py register claude_builder_v2 --parent claude_builder_v1")
    print("  genome_registry.py update claude_builder_v1")
    print("  genome_registry.py populate")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        cli_filter = None
        if "--cli" in sys.argv:
            idx = sys.argv.index("--cli")
            if idx + 1 < len(sys.argv):
                cli_filter = sys.argv[idx + 1]
        print(display_list(cli_filter=cli_filter))

    elif cmd == "show" and len(sys.argv) >= 3:
        genome_id = sys.argv[2]
        print(display_genome(genome_id))

    elif cmd == "ancestry" and len(sys.argv) >= 3:
        genome_id = sys.argv[2]
        print(display_ancestry(genome_id))

    elif cmd == "register" and len(sys.argv) >= 3:
        genome_id = sys.argv[2]
        parent = None
        skills = None
        cli = None

        args = sys.argv[3:]
        i = 0
        while i < len(args):
            if args[i] == "--parent" and i + 1 < len(args):
                parent = args[i + 1]
                i += 2
            elif args[i] == "--skills" and i + 1 < len(args):
                skills = args[i + 1].split(",")
                i += 2
            elif args[i] == "--cli" and i + 1 < len(args):
                cli = args[i + 1]
                i += 2
            else:
                i += 1

        result = register_genome(genome_id, parent=parent, skills=skills, cli=cli)
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(f"Registered genome: {result['genome_id']}")
        if parent:
            print(f"  Parent: {parent}")
        if skills:
            print(f"  Skills: {', '.join(skills)}")

    elif cmd == "update" and len(sys.argv) >= 3:
        genome_id = sys.argv[2]
        result = update_fitness_from_tracker(genome_id)
        if not result:
            print(f"Genome '{genome_id}' not found")
            sys.exit(1)
        print(f"Updated {genome_id}:")
        print(f"  Fitness: {result['fitness_score']:.1f}")
        print(f"  Tasks: {result['tasks_completed']}/{result['tasks_attempted']}")
        print(f"  Success rate: {result['success_rate']:.1%}")

    elif cmd == "update-all":
        registry = load_registry()
        updated = 0
        for genome_id in registry["genomes"]:
            result = update_fitness_from_tracker(genome_id)
            if result:
                updated += 1
        print(f"Updated {updated} genomes from fitness tracker")

    elif cmd == "populate":
        result = populate_from_files()
        print(f"Populated genome registry:")
        print(f"  Added: {result['added']}")
        print(f"  Updated: {result['updated']}")
        print(f"  Total: {result['total']}")

    elif cmd == "mutate" and len(sys.argv) >= 4:
        genome_id = sys.argv[2]
        mutation = " ".join(sys.argv[3:])
        result = add_mutation(genome_id, mutation)
        if not result:
            print(f"Genome '{genome_id}' not found")
            sys.exit(1)
        print(f"Added mutation to {genome_id}:")
        print(f"  {mutation}")

    else:
        print_usage()
        sys.exit(1)
