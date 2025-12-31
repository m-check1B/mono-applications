"""
Course Schemas
"""

from pydantic import BaseModel
from typing import List, Optional


class Lesson(BaseModel):
    """Lesson metadata."""
    id: str
    title: str
    order: int


class Course(BaseModel):
    """Course list item."""
    slug: str
    title: str
    description: str
    lessons_count: int
    level: str
    duration_minutes: int
    is_free: bool


class CourseDetail(BaseModel):
    """Course with full lesson list."""
    slug: str
    title: str
    description: str
    lessons: List[Lesson]
    level: str
    duration_minutes: int
    is_free: bool


class LessonContent(BaseModel):
    """Lesson with full content."""
    id: str
    title: str
    content: str
