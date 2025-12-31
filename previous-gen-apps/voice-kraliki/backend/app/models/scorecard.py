"""Scorecard models for automated agent grading."""

from datetime import datetime

from pydantic import BaseModel, Field


class ScorecardRequest(BaseModel):
    """Input payload for generating a scorecard."""
    agent_transcript: str = Field(..., min_length=1)
    customer_transcript: str | None = None
    expected_facts: list[str] = Field(default_factory=list)
    forbidden_facts: list[str] = Field(default_factory=list)


class EmpathyDetail(BaseModel):
    score: float
    sentiment_score: float
    empathy_phrases: list[str]
    notes: list[str]


class AccuracyDetail(BaseModel):
    score: float
    matched_facts: list[str]
    missing_facts: list[str]
    flagged_facts: list[str]
    coverage: float
    notes: list[str]


class HandlingDetail(BaseModel):
    score: float
    resolution_signals: list[str]
    follow_up_signals: list[str]
    notes: list[str]


class ScorecardResponse(BaseModel):
    overall_score: float
    summary: str
    highlights: list[str]
    improvements: list[str]
    empathy: EmpathyDetail
    accuracy: AccuracyDetail
    handling: HandlingDetail
    generated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 82.3,
                "summary": "Good performance with clear resolution steps.",
                "highlights": ["Strong empathy and clear acknowledgment of the issue."],
                "improvements": ["Confirm the ticket number earlier in the call."],
                "empathy": {
                    "score": 88.0,
                    "sentiment_score": 0.4,
                    "empathy_phrases": ["i understand", "i'm sorry"],
                    "notes": ["Positive tone maintained throughout the call."]
                },
                "accuracy": {
                    "score": 75.0,
                    "matched_facts": ["refund"],
                    "missing_facts": ["ticket number"],
                    "flagged_facts": [],
                    "coverage": 0.5,
                    "notes": ["One required fact was not mentioned."]
                },
                "handling": {
                    "score": 84.0,
                    "resolution_signals": ["refund", "escalate"],
                    "follow_up_signals": ["follow up"],
                    "notes": ["Resolution steps and follow-up promise detected."]
                },
                "generated_at": "2025-12-23T04:30:00Z"
            }
        }
