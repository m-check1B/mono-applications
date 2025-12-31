"""
Pydantic schemas for Flow Memory System
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Interaction Schemas
class InteractionCreate(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=5000, description="User's message or query")
    ai_response: Optional[str] = Field(None, max_length=10000, description="AI's response")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    session_id: Optional[str] = Field(None, min_length=1, max_length=100, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class InteractionResponse(BaseModel):
    user_message: str
    ai_response: Optional[str] = None
    timestamp: str
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Memory Pattern Schemas
class TimePattern(BaseModel):
    most_active_hour: int = Field(..., ge=0, le=23)
    distribution: Dict[int, int] = Field(default_factory=dict)


class MemoryPatterns(BaseModel):
    topics: Dict[str, int] = Field(default_factory=dict, description="Frequency of topics discussed")
    time_patterns: Optional[TimePattern] = Field(None, description="User's activity time patterns")
    intent_patterns: Dict[str, int] = Field(default_factory=dict, description="Question/command/statement distribution")
    task_keywords: List[str] = Field(default_factory=list, description="Task-related keywords found")


# Memory Retrieval Schemas
class MemoryRetrievalRequest(BaseModel):
    query: Optional[str] = Field(None, description="Query to filter relevant memories")
    limit: int = Field(10, ge=1, le=100, description="Maximum interactions to return")


class MemoryResponse(BaseModel):
    interactions: List[InteractionResponse]
    patterns: MemoryPatterns
    insights: List[str] = Field(default_factory=list)
    context_summary: Optional[str] = None
    total_count: int = Field(..., description="Total number of interactions")


# Session Schemas
class SessionResponse(BaseModel):
    session_id: str
    started_at: str
    last_activity: str
    interactions: List[InteractionResponse]
    interaction_count: int


# Context Summary Schemas
class ContextSummaryCreate(BaseModel):
    summary: str = Field(..., min_length=10, max_length=2000, description="Compressed context summary")


class ContextSummaryResponse(BaseModel):
    summary: str
    created_at: str
    version: int = 1


# Memory Stats Schemas
class MemoryStatsResponse(BaseModel):
    total_interactions: int
    memory_exists: bool
    patterns_detected: int = 0
    last_update: Optional[str] = None
    top_topics: List[str] = Field(default_factory=list)


# Bulk Operations
class BulkInteractionCreate(BaseModel):
    interactions: List[InteractionCreate] = Field(..., min_length=1, max_length=50)


class StoreResponse(BaseModel):
    success: bool
    message: str
    interactions_stored: int = 0


class ClearMemoryResponse(BaseModel):
    success: bool
    message: str
    cleared_items: Dict[str, int] = Field(default_factory=dict)


__all__ = [
    "InteractionCreate",
    "InteractionResponse",
    "TimePattern",
    "MemoryPatterns",
    "MemoryRetrievalRequest",
    "MemoryResponse",
    "SessionResponse",
    "ContextSummaryCreate",
    "ContextSummaryResponse",
    "MemoryStatsResponse",
    "BulkInteractionCreate",
    "StoreResponse",
    "ClearMemoryResponse"
]
