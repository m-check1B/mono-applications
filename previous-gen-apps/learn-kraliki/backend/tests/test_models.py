"""
Test database models
"""

from datetime import datetime, timezone
from app.models.progress import UserProgress


def test_user_progress_model():
    """Test UserProgress model attributes."""
    progress = UserProgress(
        user_id="test-user",
        course_slug="test-course",
        completed_lessons=["lesson1", "lesson2"],
        current_lesson="lesson3",
    )

    assert progress.user_id == "test-user"
    assert progress.course_slug == "test-course"
    assert progress.completed_lessons == ["lesson1", "lesson2"]
    assert progress.current_lesson == "lesson3"


def test_user_progress_defaults():
    """Test UserProgress model with default values."""
    progress = UserProgress(
        user_id="test-user",
        course_slug="test-course",
    )

    assert progress.user_id == "test-user"
    assert progress.course_slug == "test-course"
    assert progress.completed_lessons is None or progress.completed_lessons == []
    assert progress.current_lesson is None
    # Note: Default timestamps are set by SQLAlchemy when inserting to DB,
    # not when instantiating the model directly
    assert progress.completed_at is None  # Should not be completed by default


def test_user_progress_repr():
    """Test UserProgress string representation."""
    progress = UserProgress(
        user_id="test-user",
        course_slug="test-course",
    )

    repr_str = repr(progress)
    assert "test-user" in repr_str
    assert "test-course" in repr_str


def test_user_progress_with_timestamps():
    """Test UserProgress with explicit timestamps."""
    now = datetime.now(timezone.utc)

    progress = UserProgress(
        user_id="test-user",
        course_slug="test-course",
        completed_lessons=["lesson1"],
        current_lesson="lesson2",
        started_at=now,
        completed_at=now,
    )

    assert progress.started_at == now
    assert progress.completed_at == now
