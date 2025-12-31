"""
Test course service
"""

from app.services.course_service import CourseService
from app.schemas.course import Course, CourseDetail, Lesson, LessonContent


def test_get_all_courses(temp_content_dir_with_progress):
    """Test getting all courses."""
    service = CourseService()
    courses = service.get_all_courses()

    assert len(courses) == 2

    # Check course sorting by title
    assert courses[0].title < courses[1].title


def test_get_course(temp_content_dir_with_progress):
    """Test getting a specific course."""
    service = CourseService()
    course = service.get_course("getting-started")

    assert course is not None
    assert course.slug == "getting-started"
    assert course.title == "Getting Started"
    assert course.description == "Introduction to AI"
    assert course.level == "beginner"
    assert course.duration_minutes == 30
    assert course.is_free is True
    assert len(course.lessons) == 2


def test_get_course_not_found(temp_content_dir):
    """Test getting a non-existent course."""
    service = CourseService()
    course = service.get_course("nonexistent")

    assert course is None


def test_get_lesson(temp_content_dir_with_progress):
    """Test getting lesson content."""
    service = CourseService()
    lesson = service.get_lesson("getting-started", "01-introduction")

    assert lesson is not None
    assert lesson.id == "01-introduction"
    assert "Introduction" in lesson.title
    assert "Welcome to the course!" in lesson.content


def test_get_lesson_not_found(temp_content_dir_with_progress):
    """Test getting a non-existent lesson."""
    service = CourseService()
    lesson = service.get_lesson("getting-started", "nonexistent")

    assert lesson is None


def test_get_lesson_from_nonexistent_course(temp_content_dir):
    """Test getting a lesson from a non-existent course."""
    service = CourseService()
    lesson = service.get_lesson("nonexistent", "01-introduction")

    assert lesson is None


def test_extract_title():
    """Test extracting title from markdown content."""
    service = CourseService()

    # Title from H1
    content1 = "# My Title\n\nSome content"
    assert service._extract_title(content1) == "My Title"

    # No title
    content2 = "No title here"
    assert service._extract_title(content2) is None

    # Title with extra spaces
    content3 = "#   Spaced Title   \n\nContent"
    assert service._extract_title(content3) == "Spaced Title"


def test_get_lesson_id():
    """Test generating lesson ID from filename."""
    service = CourseService()

    assert service._get_lesson_id("01-introduction.md") == "01-introduction"
    assert service._get_lesson_id("lesson.md") == "lesson"
    assert service._get_lesson_id("multiple-words.md") == "multiple-words"


def test_course_service_empty_content_dir():
    """Test course service with empty content directory."""
    import tempfile
    from app.core.config import settings

    # Create empty temp directory
    empty_dir = tempfile.mkdtemp()

    original_content_dir = settings.content_dir
    settings.content_dir = empty_dir

    service = CourseService()
    courses = service.get_all_courses()

    assert len(courses) == 0

    # Cleanup
    settings.content_dir = original_content_dir


def test_get_course_without_course_json():
    """Test getting course from directory without course.json."""
    import tempfile
    from pathlib import Path
    from app.core.config import settings

    # Create temp directory with markdown but no course.json
    temp_dir = tempfile.mkdtemp()
    course_dir = Path(temp_dir) / "test-course"
    course_dir.mkdir()

    (course_dir / "01-lesson.md").write_text("# Lesson\n\nContent")

    original_content_dir = settings.content_dir
    settings.content_dir = temp_dir

    try:
        service = CourseService()
        courses = service.get_all_courses()

        # Should skip courses without course.json
        assert len(courses) == 0
    finally:
        settings.content_dir = original_content_dir


def test_get_course_with_missing_lesson_files():
    """Test getting course with lesson files that don't exist."""
    import tempfile
    from pathlib import Path
    import json
    from app.core.config import settings

    # Create temp directory with course.json but missing lesson files
    temp_dir = tempfile.mkdtemp()
    course_dir = Path(temp_dir) / "test-course"
    course_dir.mkdir()

    metadata = {
        "title": "Test Course",
        "description": "Test",
        "lessons": ["01-missing.md"],
    }

    with open(course_dir / "course.json", "w") as f:
        json.dump(metadata, f)

    original_content_dir = settings.content_dir
    settings.content_dir = temp_dir

    try:
        service = CourseService()
        course = service.get_course("test-course")

        assert course is not None
        assert len(course.lessons) == 0  # Missing files should be skipped
    finally:
        settings.content_dir = original_content_dir
