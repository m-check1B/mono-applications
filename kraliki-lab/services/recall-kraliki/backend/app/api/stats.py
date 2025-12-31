"""Stats API routes - memory system usage statistics"""
from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..services.storage import StorageService
from ..services.usage import get_usage_service
import os
import frontmatter

router = APIRouter(prefix="/stats", tags=["stats"])
storage = StorageService()
usage_service = get_usage_service()

@router.get("")
async def get_stats():
    """
    Get memory system statistics
    
    Returns:
        - total_entries: Total number of markdown files
        - total_stores: Total store count (from log + files)
        - total_retrieves: Total retrieve count (from log)
        - by_agent: Agent-specific stats
    """
    try:
        total_entries = 0
        by_agent = {}
        
        # 1. Count files on disk
        for category in storage.categories:
            cat_dir = storage.memory_dir / category
            if not cat_dir.exists():
                continue
                
            for filepath in cat_dir.glob("*.md"):
                total_entries += 1
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        post = frontmatter.load(f)
                        agent = post.metadata.get('agent', 'unknown')
                        
                        if agent not in by_agent:
                            by_agent[agent] = {"stores": 0, "retrieves": 0}
                        
                        by_agent[agent]["stores"] += 1
                except Exception:
                    continue
        
        # 2. Get stats from usage log (for retrieves and more accurate counting)
        usage_stats = usage_service.get_stats()
        
        # Merge stats
        total_retrieves = usage_stats["total_retrieves"]
        
        for agent, stats in usage_stats["by_agent"].items():
            if agent not in by_agent:
                by_agent[agent] = {"stores": 0, "retrieves": 0}
            
            # We trust the file count for stores if it's higher, 
            # but log might have things that were deleted.
            # For simplicity, we'll use the max or just add retrieves.
            by_agent[agent]["retrieves"] = max(by_agent[agent]["retrieves"], stats["retrieves"])
            
        return {
            "total_entries": total_entries,
            "total_stores": max(total_entries, usage_stats["total_stores"]), 
            "total_retrieves": total_retrieves,
            "by_agent": by_agent
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
