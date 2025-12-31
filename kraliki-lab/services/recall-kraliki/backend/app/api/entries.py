"""Entries API routes - memory system entries"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..services.storage import StorageService
from ..services.usage import get_usage_service
import os

router = APIRouter(prefix="/entries", tags=["entries"])
storage = StorageService()
usage_service = get_usage_service()

@router.get("")
async def get_entries(limit: int = 20):
    """
    Get recent memory entries in the format expected by the dashboard.
    """
    try:
        # 1. Get items from storage
        items = storage.list_items(limit=limit)
        entries = []
        
        for item in items:
            # Try to get a real timestamp from file system if the metadata date is too simple
            timestamp_val = item.get("date", "2025-12-23")
            # Ensure timestamp is a string (could be datetime.date object)
            if hasattr(timestamp_val, 'isoformat'):
                timestamp = timestamp_val.isoformat()
            else:
                timestamp = str(timestamp_val)
            if len(timestamp) <= 10:
                try:
                    file_stat = os.stat(item['file_path'])
                    timestamp = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                except Exception:
                    timestamp = f"{timestamp}T00:00:00Z"

            entries.append({
                "id": item.get("id", "unknown"),
                "agent": item.get("agent", "unknown"),
                "action": "store",
                "key": f"{item['category']}/{item.get('title', item.get('id', 'untitled'))}",
                "timestamp": timestamp,
                "size": len(item.get("content", ""))
            })
            
        # 2. Get recent operations from log (includes retrieves)
        recent_ops = usage_service.get_recent_operations(limit=limit)
        
        # Merge and deduplicate (by key and action if timestamps are very close)
        # For simplicity, we just merge and sort
        combined = entries + recent_ops
        
        # Sort by timestamp newest first
        combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return combined[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get entries: {str(e)}")
