"""
Progress Schemas
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Progress(BaseModel):
    """User progress for a course."""
    course_slug: str
    completed_lessons: List[str]
    current_lesson: Optional[str]
    percent_complete: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProgressCreate(BaseModel):
    """Create/update progress."""
    lesson_id: str
