"""
Progress Router
Endpoints for tracking user learning progress
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.progress import UserProgress
from app.schemas.progress import Progress
from app.services.course_service import course_service

router = APIRouter(prefix="/progress", tags=["progress"])


# Placeholder user ID - will be replaced with SSO
def get_current_user_id() -> str:
    """Get current user ID (placeholder for SSO integration)."""
    return "anonymous"


@router.get("", response_model=List[Progress])
async def list_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List progress for all courses."""
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    records = result.scalars().all()

    progress_list = []
    for record in records:
        course = course_service.get_course(record.course_slug)
        total_lessons = len(course.lessons) if course else 1
        percent = (len(record.completed_lessons or []) / total_lessons) * 100

        progress_list.append(Progress(
            course_slug=record.course_slug,
            completed_lessons=record.completed_lessons or [],
            current_lesson=record.current_lesson,
            percent_complete=percent,
            started_at=record.started_at,
            completed_at=record.completed_at,
        ))

    return progress_list


@router.get("/{course_slug}", response_model=Progress)
async def get_course_progress(
    course_slug: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get progress for a specific course."""
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.course_slug == course_slug
        )
    )
    record = result.scalar_one_or_none()

    course = course_service.get_course(course_slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    total_lessons = len(course.lessons)

    if not record:
        return Progress(
            course_slug=course_slug,
            completed_lessons=[],
            current_lesson=course.lessons[0].id if course.lessons else None,
            percent_complete=0,
        )

    percent = (len(record.completed_lessons or []) / total_lessons) * 100

    return Progress(
        course_slug=record.course_slug,
        completed_lessons=record.completed_lessons or [],
        current_lesson=record.current_lesson,
        percent_complete=percent,
        started_at=record.started_at,
        completed_at=record.completed_at,
    )


@router.post("/{course_slug}/{lesson_id}", response_model=Progress)
async def mark_lesson_complete(
    course_slug: str,
    lesson_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Mark a lesson as complete."""
    course = course_service.get_course(course_slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if lesson exists
    lesson_ids = [l.id for l in course.lessons]
    if lesson_id not in lesson_ids:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get or create progress record
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.course_slug == course_slug
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        record = UserProgress(
            user_id=user_id,
            course_slug=course_slug,
            completed_lessons=[],
            current_lesson=lesson_id,
        )
        db.add(record)

    # Add lesson to completed if not already
    if lesson_id not in (record.completed_lessons or []):
        record.completed_lessons = (record.completed_lessons or []) + [lesson_id]

    # Update current lesson to next one if available
    current_idx = lesson_ids.index(lesson_id)
    if current_idx < len(lesson_ids) - 1:
        record.current_lesson = lesson_ids[current_idx + 1]
    else:
        record.current_lesson = lesson_id
        # Mark course as complete if all lessons done
        if set(record.completed_lessons) == set(lesson_ids):
            record.completed_at = datetime.now(timezone.utc)

    record.last_activity = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)

    total_lessons = len(course.lessons)
    percent = (len(record.completed_lessons or []) / total_lessons) * 100

    return Progress(
        course_slug=record.course_slug,
        completed_lessons=record.completed_lessons or [],
        current_lesson=record.current_lesson,
        percent_complete=percent,
        started_at=record.started_at,
        completed_at=record.completed_at,
    )
