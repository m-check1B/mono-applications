"""
ProjectTemplateService Unit Tests
Coverage target: 100% of project_templates.py
"""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.project_templates import ProjectTemplateService
from app.models.task import Project, Task, TaskStatus


class TestProjectTemplateList:
    """Test listing project templates."""

    def test_list_templates_returns_all(self):
        """Test that list_templates returns all defined templates."""
        templates = ProjectTemplateService.list_templates()

        assert len(templates) == 5
        template_ids = [t["id"] for t in templates]
        assert "personal" in template_ids
        assert "work" in template_ids
        assert "study" in template_ids
        assert "event" in template_ids
        assert "software_dev" in template_ids

    def test_list_templates_structure(self):
        """Test that each template has required fields."""
        templates = ProjectTemplateService.list_templates()

        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "color" in template
            assert "icon" in template
            assert "task_count" in template
            assert isinstance(template["task_count"], int)
            assert template["task_count"] > 0

    def test_list_templates_colors_are_hex(self):
        """Test that template colors are valid hex colors."""
        templates = ProjectTemplateService.list_templates()

        for template in templates:
            color = template["color"]
            assert color.startswith("#")
            assert len(color) == 7


class TestGetTemplate:
    """Test getting individual templates."""

    def test_get_template_personal(self):
        """Test getting personal template."""
        template = ProjectTemplateService.get_template("personal")

        assert template["id"] == "personal"
        assert template["name"] == "Personal Goals"
        assert "tasks" in template
        assert len(template["tasks"]) == 4

    def test_get_template_work(self):
        """Test getting work template."""
        template = ProjectTemplateService.get_template("work")

        assert template["id"] == "work"
        assert template["name"] == "Work Project"
        assert len(template["tasks"]) == 7

    def test_get_template_study(self):
        """Test getting study template."""
        template = ProjectTemplateService.get_template("study")

        assert template["id"] == "study"
        assert template["name"] == "Study Plan"

    def test_get_template_event(self):
        """Test getting event template."""
        template = ProjectTemplateService.get_template("event")

        assert template["id"] == "event"
        assert template["name"] == "Event Planning"

    def test_get_template_software_dev(self):
        """Test getting software_dev template."""
        template = ProjectTemplateService.get_template("software_dev")

        assert template["id"] == "software_dev"
        assert template["name"] == "Software Development"
        assert len(template["tasks"]) == 8

    def test_get_template_not_found(self):
        """Test getting non-existent template raises error."""
        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            ProjectTemplateService.get_template("nonexistent")

    def test_get_template_returns_copy(self):
        """Test that get_template returns a copy, not the original."""
        template = ProjectTemplateService.get_template("personal")
        original = ProjectTemplateService.TEMPLATES["personal"]

        # Modify the returned template
        template["name"] = "Modified"

        # Original should be unchanged
        assert original["name"] == "Personal Goals"


class TestCreateFromTemplate:
    """Test creating projects from templates."""

    def test_create_from_template_personal(self, db: Session, test_user):
        """Test creating project from personal template."""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        assert project.name == "Personal Goals"
        assert project.description == "Track and achieve your personal objectives"
        assert project.color == "#667eea"
        assert project.icon == "🎯"
        assert project.userId == test_user.id

    def test_create_from_template_with_custom_name(self, db: Session, test_user):
        """Test creating project with custom name."""
        project = ProjectTemplateService.create_from_template(
            template_id="work",
            user_id=test_user.id,
            db=db,
            custom_name="My Custom Project"
        )

        assert project.name == "My Custom Project"
        assert project.description == "Professional project with full lifecycle"

    def test_create_from_template_creates_tasks(self, db: Session, test_user):
        """Test that template creates all tasks."""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        assert len(tasks) == 4

        task_titles = [t.title for t in tasks]
        assert "Define clear goals" in task_titles
        assert "Create action plan" in task_titles

    def test_create_from_template_task_properties(self, db: Session, test_user):
        """Test that tasks have correct properties."""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        for task in tasks:
            assert task.userId == test_user.id
            assert task.status == TaskStatus.PENDING
            assert task.projectId == project.id
            assert task.dueDate is not None
            assert task.priority in [1, 2, 3]  # high, medium, low

    def test_create_from_template_priority_mapping(self, db: Session, test_user):
        """Test that priority strings are mapped to integers."""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        # Personal template has high, high, medium, medium priorities
        priorities = sorted([t.priority for t in tasks])
        # 1 = high, 2 = medium
        assert 1 in priorities  # At least one high priority
        assert 2 in priorities  # At least one medium priority

    def test_create_from_template_estimated_minutes(self, db: Session, test_user):
        """Test that estimated hours are converted to minutes."""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        # Personal template tasks have 1h, 2h, 1h, 1h estimated hours
        # Should be converted to 60, 120, 60, 60 minutes
        estimated_minutes = sorted([t.estimatedMinutes for t in tasks])
        assert estimated_minutes == [60, 60, 60, 120]

    def test_create_from_template_invalid_template(self, db: Session, test_user):
        """Test that invalid template raises error."""
        with pytest.raises(ValueError, match="Template 'invalid' not found"):
            ProjectTemplateService.create_from_template(
                template_id="invalid",
                user_id=test_user.id,
                db=db
            )

    def test_create_from_template_work(self, db: Session, test_user):
        """Test creating work project template."""
        project = ProjectTemplateService.create_from_template(
            template_id="work",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        assert len(tasks) == 7
        assert project.icon == "💼"

    def test_create_from_template_software_dev(self, db: Session, test_user):
        """Test creating software_dev project template."""
        project = ProjectTemplateService.create_from_template(
            template_id="software_dev",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        assert len(tasks) == 8

        # Verify specific tasks exist
        task_titles = [t.title for t in tasks]
        assert "Technical specification" in task_titles
        assert "Database design" in task_titles
        assert "Backend API development" in task_titles

    def test_create_from_template_generates_unique_ids(self, db: Session, test_user):
        """Test that each project and task gets unique IDs."""
        project1 = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        project2 = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        assert project1.id != project2.id

        tasks1 = db.query(Task).filter(Task.projectId == project1.id).all()
        tasks2 = db.query(Task).filter(Task.projectId == project2.id).all()

        task_ids_1 = {t.id for t in tasks1}
        task_ids_2 = {t.id for t in tasks2}

        # No overlap in task IDs
        assert len(task_ids_1 & task_ids_2) == 0


class TestTemplateData:
    """Test template data integrity."""

    def test_all_templates_have_tasks(self):
        """Test that all templates have at least one task."""
        for template_id in ProjectTemplateService.TEMPLATES:
            template = ProjectTemplateService.TEMPLATES[template_id]
            assert len(template["tasks"]) > 0

    def test_all_tasks_have_required_fields(self):
        """Test that all tasks in templates have required fields."""
        for template_id, template in ProjectTemplateService.TEMPLATES.items():
            for task in template["tasks"]:
                assert "title" in task, f"Missing title in {template_id}"
                assert "description" in task, f"Missing description in {template_id}"
                assert "priority" in task, f"Missing priority in {template_id}"

    def test_all_priorities_are_valid(self):
        """Test that all task priorities are valid strings."""
        valid_priorities = {"high", "medium", "low"}

        for template_id, template in ProjectTemplateService.TEMPLATES.items():
            for task in template["tasks"]:
                priority = task.get("priority", "medium")
                assert priority in valid_priorities, f"Invalid priority {priority} in {template_id}"

    def test_all_templates_have_metadata(self):
        """Test that all templates have required metadata."""
        required_fields = ["name", "description", "color", "icon", "tasks"]

        for template_id, template in ProjectTemplateService.TEMPLATES.items():
            for field in required_fields:
                assert field in template, f"Missing {field} in {template_id}"
