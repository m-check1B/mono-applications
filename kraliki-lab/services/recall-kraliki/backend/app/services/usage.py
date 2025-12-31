"""
Usage Tracking Service
Tracks memory operations (stores and retrieves)
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class UsageService:
    """Usage tracking service for recall-kraliki"""

    def __init__(self, usage_file: str = None):
        if usage_file is None:
            backend_dir = Path(__file__).parent.parent.parent
            self.usage_file = backend_dir / "usage_log.jsonl"
        else:
            self.usage_file = Path(usage_file)
        
        # Ensure parent directory exists
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)

    def log_operation(self, action: str, agent: str, key: str, size: int = 0):
        """Log a memory operation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action, # "store" or "retrieve"
            "agent": agent,
            "key": key,
            "size": size
        }
        
        with open(self.usage_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent_operations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent operations from log"""
        if not self.usage_file.exists():
            return []
            
        ops = []
        try:
            with open(self.usage_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        ops.append(json.loads(line))
        except Exception:
            pass
            
        return ops[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        stats = {
            "total_stores": 0,
            "total_retrieves": 0,
            "by_agent": {}
        }
        
        if not self.usage_file.exists():
            return stats
            
        try:
            with open(self.usage_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    op = json.loads(line)
                    action = op.get("action")
                    agent = op.get("agent", "unknown")
                    
                    if agent not in stats["by_agent"]:
                        stats["by_agent"][agent] = {"stores": 0, "retrieves": 0}
                        
                    if action == "store":
                        stats["total_stores"] += 1
                        stats["by_agent"][agent]["stores"] += 1
                    elif action == "retrieve":
                        stats["total_retrieves"] += 1
                        stats["by_agent"][agent]["retrieves"] += 1
        except Exception:
            pass
            
        return stats

# Singleton instance
_usage_service = None

def get_usage_service() -> UsageService:
    """Get or create usage service instance"""
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageService()
    return _usage_service
