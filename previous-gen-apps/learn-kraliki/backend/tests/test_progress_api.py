"""
Test API routes for progress tracking
"""

from fastapi.testclient import TestClient
from datetime import datetime


def test_list_progress_empty(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test listing progress when no progress exists."""
    response = client.get("/api/progress")
    assert response.status_code == 200

    progress_list = response.json()
    assert len(progress_list) == 0


def test_get_course_progress_not_started(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test getting progress for a course that hasn't been started."""
    response = client.get("/api/progress/getting-started")
    assert response.status_code == 200

    progress = response.json()
    assert progress["course_slug"] == "getting-started"
    assert progress["completed_lessons"] == []
    assert progress["percent_complete"] == 0
    assert "current_lesson" in progress


def test_get_course_progress_nonexistent_course(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test getting progress for a non-existent course."""
    response = client.get("/api/progress/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_mark_lesson_complete_first(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking a lesson as complete for the first time."""
    response = client.post("/api/progress/getting-started/01-introduction")
    assert response.status_code == 200

    progress = response.json()
    assert progress["course_slug"] == "getting-started"
    assert "01-introduction" in progress["completed_lessons"]
    assert progress["percent_complete"] == 50.0  # 1 out of 2 lessons
    assert progress["current_lesson"] == "02-basics"


def test_mark_lesson_complete_duplicate(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking the same lesson as complete twice (should be idempotent)."""
    client.post("/api/progress/getting-started/01-introduction")

    response = client.post("/api/progress/getting-started/01-introduction")
    assert response.status_code == 200

    progress = response.json()
    assert progress["completed_lessons"].count("01-introduction") == 1
    assert progress["percent_complete"] == 50.0


def test_mark_lesson_complete_all(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking all lessons as complete."""
    # Mark first lesson
    client.post("/api/progress/getting-started/01-introduction")

    # Mark second lesson
    response = client.post("/api/progress/getting-started/02-basics")
    assert response.status_code == 200

    progress = response.json()
    assert len(progress["completed_lessons"]) == 2
    assert progress["percent_complete"] == 100.0
    assert progress["current_lesson"] == "02-basics"  # Last lesson
    assert progress["completed_at"] is not None


def test_mark_lesson_complete_in_order(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking lessons in order."""
    # Mark lessons in order
    client.post("/api/progress/getting-started/01-introduction")
    response = client.post("/api/progress/getting-started/02-basics")

    progress = response.json()
    assert progress["completed_lessons"] == ["01-introduction", "02-basics"]


def test_mark_lesson_complete_out_of_order(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking lessons out of order."""
    # Mark second lesson first
    response = client.post("/api/progress/getting-started/02-basics")

    progress = response.json()
    assert "02-basics" in progress["completed_lessons"]
    assert progress["percent_complete"] == 50.0


def test_mark_lesson_nonexistent(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking a non-existent lesson as complete."""
    response = client.post("/api/progress/getting-started/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_mark_lesson_nonexistent_course(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test marking a lesson for a non-existent course."""
    response = client.post("/api/progress/nonexistent/01-introduction")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_progress_with_courses(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test listing progress after starting courses."""
    # Start one course
    client.post("/api/progress/getting-started/01-introduction")

    # Start another course
    client.post("/api/progress/ai-fundamentals/01-neural-networks")

    response = client.get("/api/progress")
    assert response.status_code == 200

    progress_list = response.json()
    assert len(progress_list) == 2

    # Check course slugs
    course_slugs = [p["course_slug"] for p in progress_list]
    assert "getting-started" in course_slugs
    assert "ai-fundamentals" in course_slugs


def test_get_course_progress_partial(
    client: TestClient, test_db, temp_content_dir_with_progress
):
    """Test getting progress for a partially completed course."""
    # Mark first lesson
    client.post("/api/progress/getting-started/01-introduction")

    response = client.get("/api/progress/getting-started")
    assert response.status_code == 200

    progress = response.json()
    assert len(progress["completed_lessons"]) == 1
    assert progress["percent_complete"] == 50.0
    assert progress["started_at"] is not None
