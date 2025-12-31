"""
Speak by Kraliki - Insights/Analytics Schemas
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SentimentGauge(BaseModel):
    """Sentiment gauge data."""
    current: float  # -1.0 to 1.0
    previous: float | None
    change: float | None
    trend: str  # up, down, stable


class ParticipationRate(BaseModel):
    """Participation rate data."""
    current: float  # 0.0 to 1.0
    previous: float | None
    change: float | None
    total_invited: int
    total_completed: int


class TopicCount(BaseModel):
    """Topic frequency data."""
    topic: str
    count: int
    sentiment: float  # Average sentiment for this topic


class InsightsOverview(BaseModel):
    """Company-wide insights overview."""
    company_id: UUID
    period_start: datetime
    period_end: datetime
    sentiment: SentimentGauge
    participation: ParticipationRate
    top_topics: list[TopicCount]
    active_alerts_count: int
    pending_actions_count: int


class DepartmentInsights(BaseModel):
    """Per-department insights."""
    department_id: UUID
    department_name: str
    employee_count: int
    sentiment: SentimentGauge
    participation: ParticipationRate
    top_topics: list[TopicCount]
    alerts_count: int


class TrendDataPoint(BaseModel):
    """Single data point for trends."""
    date: datetime
    value: float
    count: int | None = None


class TrendData(BaseModel):
    """Trend data over time."""
    metric: str  # sentiment, participation, topics
    period: str  # week, month, quarter
    data: list[TrendDataPoint]


class QuoteDisplay(BaseModel):
    """Anonymous quote for display."""
    id: UUID
    content: str
    sentiment: float
    topic: str | None
    department_name: str | None
    created_at: datetime
    anonymous_id: str
