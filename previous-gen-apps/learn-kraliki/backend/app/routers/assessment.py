"""
AI Readiness Assessment Router

Lead capture and assessment tracking for the AI Readiness Assessment tool.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment", tags=["assessment"])

# Store leads in a JSON file (simple solution for MVP)
LEADS_FILE = Path(__file__).parent.parent.parent / "data" / "assessment_leads.json"


class AssessmentResult(BaseModel):
    """Assessment result data."""
    score: int
    maxScore: int
    percentage: int
    level: str


class AssessmentSubmission(BaseModel):
    """Assessment submission payload."""
    email: str
    companyName: str | None = None
    answers: dict[str, int]
    result: AssessmentResult
    timestamp: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Simple email validation."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()


def ensure_data_dir():
    """Ensure data directory exists."""
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LEADS_FILE.exists():
        LEADS_FILE.write_text("[]")


def load_leads() -> list[dict[str, Any]]:
    """Load existing leads from file."""
    ensure_data_dir()
    try:
        return json.loads(LEADS_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_lead(lead: dict[str, Any]) -> None:
    """Save a new lead to file."""
    leads = load_leads()
    leads.append(lead)
    LEADS_FILE.write_text(json.dumps(leads, indent=2))


@router.post("/submit")
async def submit_assessment(submission: AssessmentSubmission):
    """
    Submit an AI Readiness Assessment result.

    Captures lead information for sales follow-up.
    """
    try:
        lead_data = {
            "id": f"lead_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{submission.email.split('@')[0]}",
            "email": submission.email,
            "company_name": submission.companyName,
            "score": submission.result.score,
            "max_score": submission.result.maxScore,
            "percentage": submission.result.percentage,
            "level": submission.result.level,
            "answers": submission.answers,
            "submitted_at": submission.timestamp,
            "processed_at": datetime.now().isoformat(),
            "source": "ai-readiness-assessment",
            "status": "new"
        }

        save_lead(lead_data)

        logger.info(f"New assessment lead: {submission.email} - Score: {submission.result.percentage}%")

        return {
            "success": True,
            "message": "Assessment submitted successfully",
            "lead_id": lead_data["id"]
        }
    except Exception as e:
        logger.error(f"Failed to save assessment lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to save assessment")


@router.get("/stats")
async def get_assessment_stats():
    """
    Get aggregate statistics for assessments.

    Returns summary data without exposing individual leads.
    """
    leads = load_leads()

    if not leads:
        return {
            "total_assessments": 0,
            "average_score": 0,
            "level_distribution": {}
        }

    total = len(leads)
    avg_score = sum(l.get("percentage", 0) for l in leads) / total

    level_counts = {}
    for lead in leads:
        level = lead.get("level", "Unknown")
        level_counts[level] = level_counts.get(level, 0) + 1

    return {
        "total_assessments": total,
        "average_score": round(avg_score, 1),
        "level_distribution": level_counts
    }
