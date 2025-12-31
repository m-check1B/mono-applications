"""
Course Service
Loads courses and lessons from the content directory
"""

import json
import os
from typing import List, Optional
from pathlib import Path

from app.core.config import settings
from app.schemas.course import Course, CourseDetail, Lesson, LessonContent


class CourseService:
    """Service for loading course content from filesystem."""

    def __init__(self):
        self.content_dir = Path(settings.content_dir)

    def get_all_courses(self) -> List[Course]:
        """Get all available courses."""
        courses = []

        if not self.content_dir.exists():
            return courses

        for course_dir in self.content_dir.iterdir():
            if course_dir.is_dir():
                course = self._load_course_metadata(course_dir)
                if course:
                    courses.append(course)

        # Sort by title
        courses.sort(key=lambda c: c.title)
        return courses

    def get_course(self, slug: str) -> Optional[CourseDetail]:
        """Get a course with full lesson list."""
        course_dir = self.content_dir / slug

        if not course_dir.exists():
            return None

        course_json = course_dir / "course.json"
        if not course_json.exists():
            return None

        with open(course_json, "r") as f:
            data = json.load(f)

        lessons = self._load_lessons(course_dir, data.get("lessons", []))

        return CourseDetail(
            slug=slug,
            title=data.get("title", slug),
            description=data.get("description", ""),
            lessons=lessons,
            level=data.get("level", "beginner"),
            duration_minutes=data.get("duration_minutes", 0),
            is_free=data.get("is_free", True),
        )

    def get_lesson(self, course_slug: str, lesson_id: str) -> Optional[LessonContent]:
        """Get a lesson with full content."""
        course_dir = self.content_dir / course_slug

        if not course_dir.exists():
            return None

        # Find the lesson file
        for filename in os.listdir(course_dir):
            if filename.endswith(".md"):
                file_id = self._get_lesson_id(filename)
                if file_id == lesson_id:
                    lesson_path = course_dir / filename
                    with open(lesson_path, "r") as f:
                        content = f.read()

                    # Extract title from first H1 or use filename
                    title = self._extract_title(content) or lesson_id

                    return LessonContent(
                        id=lesson_id,
                        title=title,
                        content=content,
                    )

        return None

    def _load_course_metadata(self, course_dir: Path) -> Optional[Course]:
        """Load course.json metadata."""
        course_json = course_dir / "course.json"

        if not course_json.exists():
            return None

        with open(course_json, "r") as f:
            data = json.load(f)

        lessons_count = len(data.get("lessons", []))

        return Course(
            slug=course_dir.name,
            title=data.get("title", course_dir.name),
            description=data.get("description", ""),
            lessons_count=lessons_count,
            level=data.get("level", "beginner"),
            duration_minutes=data.get("duration_minutes", 0),
            is_free=data.get("is_free", True),
        )

    def _load_lessons(self, course_dir: Path, lesson_files: List[str]) -> List[Lesson]:
        """Load lesson metadata from file list."""
        lessons = []

        for i, filename in enumerate(lesson_files):
            lesson_path = course_dir / filename
            if lesson_path.exists():
                with open(lesson_path, "r") as f:
                    content = f.read()

                title = self._extract_title(content) or filename.replace(".md", "")
                lesson_id = self._get_lesson_id(filename)

                lessons.append(Lesson(
                    id=lesson_id,
                    title=title,
                    order=i + 1,
                ))

        return lessons

    def _get_lesson_id(self, filename: str) -> str:
        """Generate lesson ID from filename."""
        # Remove .md extension and return as ID
        return filename.replace(".md", "")

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from markdown content (first H1)."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return None


# Singleton instance
course_service = CourseService()
