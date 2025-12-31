"""Analytics schemas - Pydantic models for analytics responses"""

from pydantic import BaseModel
from typing import Optional


class DashboardSummaryResponse(BaseModel):
    """Dashboard summary metrics"""
    total_calls_24h: int
    active_calls: int
    completed_calls_24h: int
    avg_call_duration: float
    active_campaigns: int
    completion_rate: float


class CallMetricsPeriod(BaseModel):
    """Call metrics for a specific period"""
    period: str
    total: int
    inbound: int
    outbound: int
    completed: int
    failed: int
    total_duration: int
    avg_duration: float
    completion_rate: float


class CallAnalyticsSummary(BaseModel):
    """Overall call analytics summary"""
    total_calls: int
    completed_calls: int
    avg_duration: float
    completion_rate: float


class CallAnalyticsResponse(BaseModel):
    """Call analytics response with summary and period metrics"""
    summary: CallAnalyticsSummary
    metrics: list[CallMetricsPeriod]


class AgentPerformanceResponse(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    agent_name: str
    total_calls: int
    completed_calls: int
    avg_duration: float
    completion_rate: float


class CampaignAnalyticsResponse(BaseModel):
    """Campaign analytics metrics"""
    campaign_id: str
    campaign_name: str
    total_calls: int
    completed_calls: int
    active: bool
    completion_rate: float
