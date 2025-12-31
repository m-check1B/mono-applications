"""Supervisor schemas - Pydantic models for supervisor operations"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CallSummaryKeyword(BaseModel):
    """Keyword with count"""
    word: str
    count: int


class CallTranscriptItem(BaseModel):
    """Transcript item"""
    role: str
    content: str
    timestamp: datetime


class CallSummaryResponse(BaseModel):
    """Detailed call summary"""
    call_id: str
    agent_id: Optional[str]
    from_number: str
    to_number: str
    status: str
    direction: str
    duration_sec: int
    total_exchanges: int
    first_utterance: str
    last_utterance: str
    keywords: list[CallSummaryKeyword]
    sentiment: str
    transcripts: list[CallTranscriptItem]


class MonitorCallResponse(BaseModel):
    """Monitor call response"""
    success: bool
    call_id: str
    monitor_url: str
    message: str


class ActiveCallItem(BaseModel):
    """Active call item"""
    id: str
    from_number: str
    to_number: str
    agent_id: Optional[str]
    start_time: datetime
    status: str


class ActiveCallsResponse(BaseModel):
    """Active calls response"""
    calls: list[dict]  # Using dict to avoid circular import with Call model
    total: int
