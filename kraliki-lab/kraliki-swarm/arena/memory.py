#!/usr/bin/env python3
"""
Darwin Memory - Semantic memory using mgrep
Remember by meaning, not just keys.
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

MGREP_API = "http://localhost:8001"
MEMORY_STORE = "kraliki_memories"
DATA_DIR = Path(__file__).parent / "data"
MEMORY_DIR = DATA_DIR / "memories"

def ensure_store():
    """Create memory store if it doesn't exist"""
    try:
        requests.post(f"{MGREP_API}/v1/stores", json={
            "name": MEMORY_STORE,
            "description": "Darwin agent memories"
        }, timeout=5)
    except:
        pass  # Store might already exist

def remember(text, agent="anonymous", tags=None):
    """Store a memory - always local, optionally mgrep"""
    memory = {
        "text": text,
        "metadata": {
            "agent": agent,
            "time": datetime.now().isoformat(),
            "tags": tags or []
        }
    }

    # Always save locally (primary storage)
    MEMORY_DIR.mkdir(exist_ok=True)
    agent_file = MEMORY_DIR / f"{agent}.jsonl"
    with open(agent_file, "a") as f:
        f.write(json.dumps(memory) + "\n")

    # Also try to index in mgrep for semantic search
    try:
        ensure_store()
        # Create a temp file and upload it
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(f"[{agent}] {text}")
            tmp_path = tmp.name

        with open(tmp_path, 'rb') as f:
            r = requests.post(
                f"{MGREP_API}/v1/stores/{MEMORY_STORE}/files",
                files={"file": f},
                data={
                    "external_id": f"{agent}_{datetime.now().timestamp()}",
                    "metadata": json.dumps(memory["metadata"])
                },
                timeout=10
            )
        os.unlink(tmp_path)
    except:
        pass  # mgrep indexing is optional

    print(f"🧠 Remembered: {text[:50]}...")

def recall(query, agent=None, limit=5):
    """Recall memories by semantic search"""
    try:
        payload = {
            "query": query,
            "store_identifiers": [MEMORY_STORE],
            "top_k": limit
        }

        r = requests.post(f"{MGREP_API}/v1/stores/search", json=payload, timeout=10)

        if r.ok:
            results = r.json().get("data", [])
            if not results:
                print("🤔 No memories found")
                return

            print(f"🧠 Recalling '{query}':")
            for mem in results:
                meta = mem.get("metadata", {})
                who = meta.get("agent", "?")
                when = meta.get("time", "?")[:10]
                if agent and who != agent:
                    continue
                print(f"  [{who} @ {when}] {mem['text'][:100]}...")
        else:
            # Fallback to local search
            recall_local(query, agent, limit)
    except:
        recall_local(query, agent, limit)

def recall_local(query, agent=None, limit=5):
    """Fallback: search local memory files (word-based matching)"""
    if not MEMORY_DIR.exists():
        print("🤔 No memories found")
        return

    # Split query into words for flexible matching
    query_words = [w.lower() for w in query.split() if len(w) > 2]
    matches = []

    for f in MEMORY_DIR.glob("*.jsonl"):
        if agent and f.stem != agent:
            continue
        for line in open(f):
            mem = json.loads(line)
            text_lower = mem["text"].lower()
            # Match if ANY query word appears in memory
            if any(word in text_lower for word in query_words):
                # Score by how many words match
                score = sum(1 for word in query_words if word in text_lower)
                matches.append((score, mem))

    if not matches:
        print("🤔 No memories found")
        return

    # Sort by score (most matching words first)
    matches.sort(key=lambda x: -x[0])

    print(f"🧠 Recalling '{query}' (local):")
    for score, mem in matches[:limit]:
        who = mem["metadata"].get("agent", "?")
        print(f"  [{who}] {mem['text'][:100]}...")

def forget(query, agent="anonymous"):
    """Forget memories matching query (local only)"""
    agent_file = MEMORY_DIR / f"{agent}.jsonl"
    if not agent_file.exists():
        print("🤔 Nothing to forget")
        return

    lines = open(agent_file).readlines()
    kept = [l for l in lines if query.lower() not in l.lower()]

    if len(kept) == len(lines):
        print("🤔 Nothing matched")
        return

    with open(agent_file, "w") as f:
        f.writelines(kept)

    forgotten = len(lines) - len(kept)
    print(f"🗑️ Forgot {forgotten} memories matching '{query}'")

def share(key, recipient, agent="anonymous"):
    """Share a memory with another agent"""
    # Find memory locally
    agent_file = MEMORY_DIR / f"{agent}.jsonl"
    if not agent_file.exists():
        print("🤔 No memories to share")
        return

    for line in open(agent_file):
        mem = json.loads(line)
        if key.lower() in mem["text"].lower():
            # Copy to recipient
            MEMORY_DIR.mkdir(exist_ok=True)
            recipient_file = MEMORY_DIR / f"{recipient}.jsonl"
            mem["metadata"]["shared_by"] = agent
            with open(recipient_file, "a") as f:
                f.write(json.dumps(mem) + "\n")
            print(f"📤 Shared memory with @{recipient}")
            return

    print("🤔 No matching memory to share")

def my_memories(agent="anonymous", limit=10):
    """List your own memories"""
    agent_file = MEMORY_DIR / f"{agent}.jsonl"
    if not agent_file.exists():
        print("🤔 No memories yet")
        return

    lines = agent_file.read_text().strip().split("\n")[-limit:]
    print(f"🧠 Your memories ({len(lines)}):")
    for line in lines:
        mem = json.loads(line)
        print(f"  • {mem['text'][:80]}...")


def compact(agent="anonymous", days=30):
    """Remove memories older than N days for an agent"""
    agent_file = MEMORY_DIR / f"{agent}.jsonl"
    if not agent_file.exists():
        print("🤔 No memories to compact")
        return

    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    lines = agent_file.read_text().strip().split("\n")
    kept = []
    removed = 0

    for line in lines:
        if not line:
            continue
        try:
            mem = json.loads(line)
            time_str = mem.get("metadata", {}).get("time", "")
            if time_str and time_str < cutoff:
                removed += 1
            else:
                kept.append(line)
        except:
            kept.append(line)  # Keep unparseable lines

    if removed == 0:
        print(f"✅ No memories older than {days} days")
        return

    with open(agent_file, "w") as f:
        f.write("\n".join(kept) + "\n")

    print(f"🗑️ Removed {removed} memories older than {days} days")
    print(f"   Kept {len(kept)} memories")


def consolidate(dry_run=False):
    """Consolidate ephemeral agent memories into role-based files.

    Merges files like CC-builder-08:30.26.12.AA.jsonl → CC-builder.jsonl
    This reduces file count and improves recall quality.
    """
    import re

    if not MEMORY_DIR.exists():
        print("📦 No memories to consolidate")
        return

    # Pattern to match ephemeral agent IDs: LAB-role-HH:MM.DD.MM.XX
    ephemeral_pattern = re.compile(r'^([A-Z]{2})-([a-z_]+)-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2}$')

    # Track consolidation targets
    consolidations = {}  # role_file -> [(source_file, memory_count), ...]

    for f in MEMORY_DIR.glob("*.jsonl"):
        agent_name = f.stem
        match = ephemeral_pattern.match(agent_name)
        if not match:
            continue  # Skip non-ephemeral files (darwin-*, anonymous, etc.)

        lab = match.group(1)
        role = match.group(2)
        target_name = f"{lab}-{role}"

        if target_name not in consolidations:
            consolidations[target_name] = []

        # Count memories in this file
        try:
            lines = [l for l in f.read_text().strip().split("\n") if l]
            consolidations[target_name].append((f, len(lines)))
        except:
            pass

    if not consolidations:
        print("📦 No ephemeral memories to consolidate")
        return

    # Print summary
    total_files = sum(len(sources) for sources in consolidations.values())
    total_memories = sum(sum(count for _, count in sources) for sources in consolidations.values())

    print("📦 MEMORY CONSOLIDATION PLAN")
    print("=" * 50)
    print(f"Ephemeral files to merge: {total_files}")
    print(f"Total memories to move: {total_memories}")
    print(f"Target consolidated files: {len(consolidations)}")
    print()

    print("CONSOLIDATION TARGETS:")
    print("-" * 50)
    for target, sources in sorted(consolidations.items(), key=lambda x: -len(x[1])):
        source_count = len(sources)
        memory_count = sum(count for _, count in sources)
        print(f"  {target}.jsonl ← {source_count} files ({memory_count} memories)")

    if dry_run:
        print()
        print("💡 Dry run mode. Use 'consolidate --execute' to perform merge.")
        return

    # Perform consolidation
    print()
    print("EXECUTING CONSOLIDATION...")

    merged_count = 0
    deleted_count = 0

    for target_name, sources in consolidations.items():
        target_file = MEMORY_DIR / f"{target_name}.jsonl"

        # Collect all memories from source files
        all_memories = []
        for source_file, _ in sources:
            try:
                for line in source_file.read_text().strip().split("\n"):
                    if not line:
                        continue
                    try:
                        mem = json.loads(line)
                        # Add original agent to metadata for traceability
                        if "metadata" not in mem:
                            mem["metadata"] = {}
                        mem["metadata"]["original_agent"] = source_file.stem
                        mem["metadata"]["consolidated"] = True
                        all_memories.append(mem)
                    except:
                        pass
            except:
                pass

        if not all_memories:
            continue

        # Sort by time
        all_memories.sort(key=lambda m: m.get("metadata", {}).get("time", ""))

        # Append to target file
        with open(target_file, "a") as f:
            for mem in all_memories:
                f.write(json.dumps(mem) + "\n")

        merged_count += len(all_memories)

        # Delete source files
        for source_file, _ in sources:
            try:
                source_file.unlink()
                deleted_count += 1
            except:
                pass

    print(f"✅ Merged {merged_count} memories into {len(consolidations)} files")
    print(f"🗑️ Deleted {deleted_count} ephemeral files")


def stats():
    """Show memory statistics across all agents"""
    if not MEMORY_DIR.exists():
        print("📊 Memory Stats: No memories stored yet")
        return

    total_memories = 0
    agents_data = []
    oldest_memory = None
    newest_memory = None
    ephemeral_count = 0

    # Pattern to detect ephemeral agents
    import re
    ephemeral_pattern = re.compile(r'^[A-Z]{2}-[a-z_]+-\d{2}:\d{2}\.\d{2}\.\d{2}\.[A-Z]{2}$')

    for f in MEMORY_DIR.glob("*.jsonl"):
        agent_name = f.stem
        lines = f.read_text().strip().split("\n")
        count = len([l for l in lines if l])  # Count non-empty lines
        total_memories += count

        is_ephemeral = bool(ephemeral_pattern.match(agent_name))
        if is_ephemeral:
            ephemeral_count += 1

        # Get first and last memory times
        first_time = None
        last_time = None
        for line in lines:
            if not line:
                continue
            try:
                mem = json.loads(line)
                time_str = mem.get("metadata", {}).get("time", "")
                if time_str:
                    if first_time is None:
                        first_time = time_str
                    last_time = time_str
            except:
                pass

        agents_data.append({
            "agent": agent_name,
            "count": count,
            "first": first_time,
            "last": last_time,
            "size_kb": f.stat().st_size / 1024,
            "ephemeral": is_ephemeral
        })

        # Track global oldest/newest
        if first_time:
            if oldest_memory is None or first_time < oldest_memory:
                oldest_memory = first_time
        if last_time:
            if newest_memory is None or last_time > newest_memory:
                newest_memory = last_time

    # Sort by count descending
    agents_data.sort(key=lambda x: -x["count"])

    print("📊 MEMORY STATISTICS")
    print("=" * 50)
    print(f"Total Memories: {total_memories}")
    print(f"Total Agents: {len(agents_data)}")
    print(f"Ephemeral Agent Files: {ephemeral_count} (consider 'consolidate' to merge)")
    if oldest_memory:
        print(f"Oldest Memory: {oldest_memory[:19]}")
    if newest_memory:
        print(f"Newest Memory: {newest_memory[:19]}")
    print()

    print("BY AGENT (top 15):")
    print("-" * 50)
    for data in agents_data[:15]:
        last_date = data["last"][:10] if data["last"] else "?"
        marker = " [E]" if data["ephemeral"] else ""
        print(f"  {data['agent'][:30]:30} | {data['count']:4} memories | {data['size_kb']:.1f} KB | last: {last_date}{marker}")

    # Show total storage
    total_kb = sum(d["size_kb"] for d in agents_data)
    print("-" * 50)
    print(f"Total storage: {total_kb:.1f} KB")

    # Check mgrep status
    print()
    try:
        r = requests.get(f"{MGREP_API}/v1/stores/{MEMORY_STORE}", timeout=2)
        if r.ok:
            store_data = r.json()
            print(f"mgrep store: {MEMORY_STORE} ✓ (semantic search enabled)")
        else:
            print(f"mgrep store: {MEMORY_STORE} ✗ (not indexed)")
    except:
        print(f"mgrep store: unavailable (local-only mode)")

def print_help():
    """Print help message."""
    print("""Darwin Memory - Semantic memory system for agents

Usage: memory.py <command> [args]

Commands:
  remember <text>           Store a memory (use DARWIN_AGENT env for agent ID)
  recall <query>            Recall memories by semantic search
  mine                      List your own memories
  forget <query>            Delete memories matching query
  share @<agent> <query>    Share a memory with another agent
  stats                     Show memory statistics
  compact [days]            Remove memories older than N days (default: 30)
  consolidate [--execute]   Merge ephemeral agent memories into role files

Environment:
  DARWIN_AGENT              Agent ID (default: anonymous)

Examples:
  DARWIN_AGENT="CC-builder" python3 memory.py remember "Found a bug in the auth module"
  python3 memory.py recall "authentication"
  python3 memory.py stats
  python3 memory.py consolidate --execute
""")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cmd = sys.argv[1]
    agent = os.environ.get("DARWIN_AGENT", "anonymous")

    if cmd == "remember" and len(sys.argv) >= 3:
        text = " ".join(sys.argv[2:])
        tags = [t for t in sys.argv[2:] if t.startswith("#")]
        remember(text, agent, tags)

    elif cmd == "recall" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        recall(query, agent=None)

    elif cmd == "mine":
        recall(query="", agent=agent) if len(sys.argv) > 2 else my_memories(agent)

    elif cmd == "forget" and len(sys.argv) >= 3:
        forget(" ".join(sys.argv[2:]), agent)

    elif cmd == "share" and len(sys.argv) >= 4:
        recipient = sys.argv[2].lstrip("@")
        key = " ".join(sys.argv[3:])
        share(key, recipient, agent)

    elif cmd == "stats":
        stats()

    elif cmd == "compact":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        compact(agent, days)

    elif cmd == "consolidate":
        # consolidate [--execute]
        execute = len(sys.argv) > 2 and sys.argv[2] == "--execute"
        consolidate(dry_run=not execute)

    else:
        print(f"Unknown command: {cmd}")
