"""
Courses Router
Endpoints for listing and viewing courses
"""

from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.course import Course, CourseDetail, LessonContent
from app.services.course_service import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[Course])
async def list_courses():
    """List all available courses."""
    return course_service.get_all_courses()


@router.get("/{slug}", response_model=CourseDetail)
async def get_course(slug: str):
    """Get course details with lesson list."""
    course = course_service.get_course(slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{slug}/lessons/{lesson_id}", response_model=LessonContent)
async def get_lesson(slug: str, lesson_id: str):
    """Get lesson content."""
    lesson = course_service.get_lesson(slug, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
