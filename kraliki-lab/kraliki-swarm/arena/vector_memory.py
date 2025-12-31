#!/usr/bin/env python3
"""Vector memory for semantic recall using mgrep-selfhosted.

Uses the existing mgrep infrastructure (Infinity + Qdrant) instead of local FAISS.
This shares the embedding models and vector DB, avoiding duplicate resources.

WHY NOT FAISS:
- mgrep already runs Infinity (mxbai-embed-large-v1, 1024 dims) and Qdrant
- Running separate FAISS + sentence-transformers would duplicate:
  - ~4GB model weights in memory
  - Embedding computation
  - Vector storage
- mgrep provides better embeddings (1024 dims vs 384) and production infrastructure
- Local JSON backup ensures data safety when mgrep is temporarily unavailable

ARCHITECTURE:
  store() -> local JSON backup + attempt mgrep index
  recall() -> try mgrep semantic search, fallback to keyword matching

Usage:
    python3 vector_memory.py store agent_id "key" "content to remember"
    python3 vector_memory.py recall agent_id "semantic query"
    python3 vector_memory.py list agent_id
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# mgrep API endpoint
MGREP_URL = os.environ.get("MGREP_URL", "http://localhost:8001")
STORE_NAME = "kraliki_memories"

KRALIKI_DIR = Path(__file__).parent.parent
MEMORY_DIR = KRALIKI_DIR / "data" / "vector_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_store_exists():
    """Create the memories store if it doesn't exist."""
    try:
        # Check if store exists
        resp = requests.get(f"{MGREP_URL}/v1/stores/{STORE_NAME}", timeout=5)
        if resp.status_code == 200:
            return True

        # Create store
        resp = requests.post(
            f"{MGREP_URL}/v1/stores",
            json={"name": STORE_NAME, "description": "Kraliki agent memories"},
            timeout=5
        )
        return resp.status_code in (200, 201, 409)  # 409 = already exists
    except requests.RequestException:
        return False


def _mgrep_available() -> bool:
    """Check if mgrep is available."""
    try:
        # Try searching an existing store to check if mgrep is up
        resp = requests.post(
            f"{MGREP_URL}/v1/stores/search",
            json={"query": "test", "store_identifiers": ["business_ops"], "top_k": 1},
            timeout=2
        )
        return resp.status_code == 200
    except requests.RequestException:
        return False


class VectorMemory:
    """Vector-based memory store using mgrep backend."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.local_file = MEMORY_DIR / f"{agent_id}.json"
        self.use_mgrep = _mgrep_available()

        if self.use_mgrep:
            _ensure_store_exists()

        # Load local backup
        self.memories: List[Dict] = []
        if self.local_file.exists():
            try:
                with open(self.local_file) as f:
                    self.memories = json.load(f)
            except Exception:
                self.memories = []

    def _save_local(self):
        """Save to local JSON as backup."""
        with open(self.local_file, 'w') as f:
            json.dump(self.memories, f, indent=2)

    def store(self, key: str, content: str, metadata: Dict = None) -> int:
        """Store a memory with semantic embedding.

        Returns:
            Memory ID
        """
        memory_id = len(self.memories)
        external_id = f"{self.agent_id}_{memory_id}"

        memory = {
            "id": memory_id,
            "external_id": external_id,
            "key": key,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "agent_id": self.agent_id
        }
        self.memories.append(memory)
        self._save_local()

        # Store in mgrep
        if self.use_mgrep:
            try:
                # mgrep expects file upload, we simulate with text content
                full_text = f"# {key}\n\nAgent: {self.agent_id}\nCreated: {memory['created_at']}\n\n{content}"

                resp = requests.post(
                    f"{MGREP_URL}/v1/stores/{STORE_NAME}/documents",
                    json={
                        "external_id": external_id,
                        "text": full_text,
                        "metadata": {
                            "agent_id": self.agent_id,
                            "key": key,
                            "memory_id": memory_id,
                            "type": "agent_memory",
                            **memory.get("metadata", {})
                        }
                    },
                    timeout=10
                )
                if resp.status_code not in (200, 201):
                    print(f"Warning: Failed to store in mgrep: {resp.text}")
            except requests.RequestException as e:
                print(f"Warning: mgrep store failed: {e}")

        return memory_id

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recall memories by semantic similarity.

        Args:
            query: Natural language query
            top_k: Number of results

        Returns:
            List of matching memories with scores
        """
        if not self.memories:
            return []

        # Try mgrep first
        if self.use_mgrep:
            try:
                resp = requests.post(
                    f"{MGREP_URL}/v1/stores/search",
                    json={
                        "query": query,
                        "store_identifiers": [STORE_NAME],
                        "top_k": top_k * 2,  # Get more, filter by agent
                        "filters": {
                            "all": [
                                {"key": "agent_id", "operator": "equals", "value": self.agent_id}
                            ]
                        }
                    },
                    timeout=10
                )

                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("data", [])[:top_k]:
                        # Find matching local memory
                        meta = item.get("metadata", {})
                        memory_id = meta.get("memory_id")
                        if memory_id is not None and memory_id < len(self.memories):
                            mem = self.memories[memory_id].copy()
                            mem["score"] = item.get("score", 0)
                            results.append(mem)
                    return results
            except requests.RequestException as e:
                print(f"Warning: mgrep recall failed: {e}, using fallback")

        # Fallback: keyword matching
        results = []
        query_lower = query.lower()
        for mem in self.memories:
            if mem.get("deleted"):
                continue
            score = sum(1 for word in query_lower.split()
                       if word in mem["content"].lower() or word in mem["key"].lower())
            if score > 0:
                results.append({**mem, "score": score})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]

    def recall_by_key(self, key: str) -> Optional[Dict]:
        """Recall memory by exact key match."""
        for mem in reversed(self.memories):
            if mem["key"] == key and not mem.get("deleted"):
                return mem
        return None

    def list_all(self) -> List[Dict]:
        """List all memories for this agent."""
        return [m for m in self.memories if not m.get("deleted")]

    def delete(self, memory_id: int) -> bool:
        """Mark a memory as deleted."""
        for mem in self.memories:
            if mem["id"] == memory_id:
                mem["deleted"] = True
                mem["deleted_at"] = datetime.now().isoformat()
                self._save_local()

                # Delete from mgrep
                if self.use_mgrep:
                    try:
                        external_id = f"{self.agent_id}_{memory_id}"
                        requests.delete(
                            f"{MGREP_URL}/v1/stores/{STORE_NAME}/documents/{external_id}",
                            timeout=5
                        )
                    except Exception:
                        pass

                return True
        return False

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        active = [m for m in self.memories if not m.get("deleted")]
        return {
            "agent_id": self.agent_id,
            "total_memories": len(self.memories),
            "active_memories": len(active),
            "using_mgrep": self.use_mgrep,
            "mgrep_url": MGREP_URL,
            "local_file": str(self.local_file),
        }


# Global cache of memory instances
_memory_cache: Dict[str, VectorMemory] = {}


def get_memory(agent_id: str) -> VectorMemory:
    """Get or create memory instance for agent."""
    if agent_id not in _memory_cache:
        _memory_cache[agent_id] = VectorMemory(agent_id)
    return _memory_cache[agent_id]


def store(agent_id: str, key: str, content: str, metadata: Dict = None) -> int:
    """Store a memory."""
    return get_memory(agent_id).store(key, content, metadata)


def recall(agent_id: str, query: str, top_k: int = 5) -> List[Dict]:
    """Recall memories by semantic search."""
    return get_memory(agent_id).recall(query, top_k)


def recall_key(agent_id: str, key: str) -> Optional[Dict]:
    """Recall memory by exact key."""
    return get_memory(agent_id).recall_by_key(key)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Kraliki Vector Memory (using mgrep backend)")
        print("=" * 50)
        print(f"\nmgrep URL: {MGREP_URL}")
        print(f"Store: {STORE_NAME}")
        print(f"Available: {_mgrep_available()}")
        print("\nUsage:")
        print("  vector_memory.py store <agent_id> <key> <content>")
        print("  vector_memory.py recall <agent_id> <query>")
        print("  vector_memory.py list <agent_id>")
        print("  vector_memory.py stats <agent_id>")
        sys.exit(1)

    command = sys.argv[1]
    agent_id = sys.argv[2]

    if command == "store":
        if len(sys.argv) < 5:
            print("Usage: vector_memory.py store <agent_id> <key> <content>")
            sys.exit(1)
        key = sys.argv[3]
        content = " ".join(sys.argv[4:])
        mem_id = store(agent_id, key, content)
        memory = get_memory(agent_id)
        print(f"Stored memory {mem_id} for {agent_id}")
        print(f"  Using mgrep: {memory.use_mgrep}")

    elif command == "recall":
        if len(sys.argv) < 4:
            print("Usage: vector_memory.py recall <agent_id> <query>")
            sys.exit(1)
        query = " ".join(sys.argv[3:])
        results = recall(agent_id, query)
        print(f"\nRecall results for '{query}':\n")
        for r in results:
            print(f"  [{r['score']:.2f}] {r['key']}: {r['content'][:100]}...")

    elif command == "list":
        memory = get_memory(agent_id)
        memories = memory.list_all()
        print(f"\nMemories for {agent_id} ({len(memories)} total):\n")
        for m in memories[-10:]:
            print(f"  {m['id']}: {m['key']}")
            print(f"      {m['content'][:80]}...")

    elif command == "stats":
        memory = get_memory(agent_id)
        stats = memory.get_stats()
        print(json.dumps(stats, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
