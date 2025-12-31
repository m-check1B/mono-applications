"""
Test API routes for courses
"""

from fastapi.testclient import TestClient


def test_list_courses(client: TestClient, temp_content_dir_with_progress):
    """Test listing all courses."""
    response = client.get("/api/courses")
    assert response.status_code == 200

    courses = response.json()
    assert len(courses) == 2

    # Check course structure
    course = courses[0]
    assert "slug" in course
    assert "title" in course
    assert "description" in course
    assert "lessons_count" in course
    assert "level" in course
    assert "duration_minutes" in course
    assert "is_free" in course


def test_get_course(client: TestClient, temp_content_dir_with_progress):
    """Test getting a specific course."""
    response = client.get("/api/courses/getting-started")
    assert response.status_code == 200

    course = response.json()
    assert course["slug"] == "getting-started"
    assert course["title"] == "Getting Started"
    assert "lessons" in course
    assert len(course["lessons"]) == 2


def test_get_course_not_found(client: TestClient, temp_content_dir_with_progress):
    """Test getting a non-existent course."""
    response = client.get("/api/courses/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_lesson(client: TestClient, temp_content_dir_with_progress):
    """Test getting lesson content."""
    response = client.get("/api/courses/getting-started/lessons/01-introduction")
    assert response.status_code == 200

    lesson = response.json()
    assert lesson["id"] == "01-introduction"
    assert "title" in lesson
    assert "content" in lesson
    assert "Introduction" in lesson["title"]


def test_get_lesson_not_found(client: TestClient, temp_content_dir_with_progress):
    """Test getting a non-existent lesson."""
    response = client.get("/api/courses/getting-started/lessons/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_lesson_from_nonexistent_course(
    client: TestClient, temp_content_dir_with_progress
):
    """Test getting a lesson from a non-existent course."""
    response = client.get("/api/courses/nonexistent/lessons/01-introduction")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
