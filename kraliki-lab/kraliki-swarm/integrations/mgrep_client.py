#!/usr/bin/env python3
"""
mgrep Memory Helper for GIN Highways
=====================================
Simple interface for all highways to access permanent memory.

Usage:
    from mgrep_memory import search, remember, recall

    # Search for context
    results = search("authentication handler")

    # Store a learning
    remember("Bug Fix: Auth token expiry",
             "Fixed token refresh by adding 5 minute buffer",
             tags=["auth", "bug_fix"])

    # Recall recent learnings
    learnings = recall("auth token issues")
"""

import json
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib import request
from urllib.error import URLError

MGREP_URL = "http://localhost:8001"
GIN_DIR = Path(__file__).parent
LEARNINGS_DIR = GIN_DIR / "learnings"
LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)


def _api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Internal API call to mgrep"""
    url = f"{MGREP_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    try:
        if data:
            req = request.Request(url, data=json.dumps(data).encode(), headers=headers, method=method)
        else:
            req = request.Request(url, headers=headers, method=method)

        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def search(
    query: str,
    stores: List[str] = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Semantic search across indexed codebases.

    Args:
        query: Natural language query
        stores: Store IDs to search (default: all_projects, gin_learnings)
        top_k: Number of results

    Returns:
        List of matching documents with path, score, and text
    """
    if stores is None:
        stores = ["all_projects", "gin_learnings"]

    result = _api_call("/v1/stores/search", "POST", {
        "query": query,
        "store_identifiers": stores,
        "top_k": top_k
    })

    if "error" in result:
        return []

    formatted = []
    for item in result.get("data", []):
        formatted.append({
            "path": item.get("metadata", {}).get("path", "unknown"),
            "score": round(item.get("score", 0), 3),
            "text": item.get("text", "")[:500],
            "store": item.get("store_id", "unknown")
        })

    return formatted


def remember(
    title: str,
    content: str,
    category: str = "learning",
    tags: List[str] = None,
    source: str = "highway"
) -> bool:
    """
    Store a learning/insight to permanent memory.

    Args:
        title: Short title for the learning
        content: Full content/details
        category: Category (learning, bug_fix, improvement, pattern)
        tags: Additional tags for searchability
        source: Which highway/agent created this

    Returns:
        True if stored successfully
    """
    learning_id = hashlib.md5(f"{title}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    timestamp = datetime.now().isoformat()

    document = f"""# {title}

**Category:** {category}
**Source:** {source}
**Tags:** {', '.join(tags or [])}
**Timestamp:** {timestamp}
**ID:** {learning_id}

---

{content}

---
_Stored by GIN {source}_
"""

    # Save locally first
    local_path = LEARNINGS_DIR / f"{learning_id}_{category}.md"
    local_path.write_text(document)

    # Ensure gin_learnings store exists
    _api_call("/v1/stores", "POST", {
        "name": "gin_learnings",
        "description": "GIN learnings and improvements"
    })

    # Upload to mgrep using curl (simpler for multipart)
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(document)
        temp_path = f.name

    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST",
            f"{MGREP_URL}/v1/stores/gin_learnings/files",
            "-F", f"file=@{temp_path}",
            "-F", f"external_id={learning_id}",
            "-F", f'metadata={{"path":"{local_path}","category":"{category}","tags":{json.dumps(tags or [])},"source":"{source}"}}'
        ], capture_output=True, text=True, timeout=30)

        return result.returncode == 0
    except Exception:
        return False
    finally:
        Path(temp_path).unlink(missing_ok=True)


def recall(
    query: str,
    category: str = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Recall relevant learnings from permanent memory.

    Args:
        query: What to search for
        category: Optional category filter
        top_k: Number of results

    Returns:
        List of relevant learnings
    """
    search_query = query
    if category:
        search_query = f"{category}: {query}"

    return search(search_query, stores=["gin_learnings"], top_k=top_k)


def get_context(topic: str, top_k: int = 5) -> str:
    """
    Get context for a topic - formatted for prompt injection.

    Args:
        topic: What to search for
        top_k: Number of results

    Returns:
        Formatted context string for prompt
    """
    results = search(topic, top_k=top_k)

    if not results:
        return "No relevant context found."

    context_parts = []
    for r in results:
        context_parts.append(f"**{r['path']}** (score: {r['score']})")
        context_parts.append(f"```\n{r['text']}\n```\n")

    return "\n".join(context_parts)


# Quick test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mgrep_memory.py <search|remember|recall> [args]")
        print("Examples:")
        print("  python mgrep_memory.py search 'authentication handler'")
        print("  python mgrep_memory.py remember 'Bug Fix' 'Fixed auth token refresh'")
        print("  python mgrep_memory.py recall 'auth issues'")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = search(query)
        for r in results:
            print(f"[{r['score']}] {r['path']}")
            print(f"  {r['text'][:100]}...")
            print()

    elif cmd == "remember" and len(sys.argv) > 3:
        title = sys.argv[2]
        content = " ".join(sys.argv[3:])
        if remember(title, content):
            print(f"Remembered: {title}")
        else:
            print("Failed to store")

    elif cmd == "recall" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = recall(query)
        for r in results:
            print(f"[{r['score']}] {r['path']}")
            print(f"  {r['text'][:100]}...")
            print()

    else:
        print(f"Unknown command: {cmd}")
