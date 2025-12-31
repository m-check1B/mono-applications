"""
Unit tests for Project Templates Service
Tests template listing, project creation from templates, and template retrieval
"""

import pytest
from datetime import datetime, timedelta

from app.services.project_templates import ProjectTemplateService
from app.models.task import TaskStatus


class TestListTemplates:
    """Tests for list_templates method"""

    def test_list_all_templates(self):
        """List all available templates"""
        templates = ProjectTemplateService.list_templates()

        assert len(templates) == 5
        template_ids = [t["id"] for t in templates]
        assert "personal" in template_ids
        assert "work" in template_ids
        assert "study" in template_ids
        assert "event" in template_ids
        assert "software_dev" in template_ids

    def test_template_structure(self):
        """Each template has required fields"""
        templates = ProjectTemplateService.list_templates()

        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "color" in template
            assert "icon" in template
            assert "task_count" in template

    def test_task_counts(self):
        """Templates have correct task counts"""
        templates = ProjectTemplateService.list_templates()
        template_dict = {t["id"]: t for t in templates}

        assert template_dict["personal"]["task_count"] == 4
        assert template_dict["work"]["task_count"] == 7
        assert template_dict["study"]["task_count"] == 6
        assert template_dict["event"]["task_count"] == 7
        assert template_dict["software_dev"]["task_count"] == 8


class TestGetTemplate:
    """Tests for get_template method"""

    def test_get_personal_template(self):
        """Get personal template details"""
        template = ProjectTemplateService.get_template("personal")

        assert template["id"] == "personal"
        assert template["name"] == "Personal Goals"
        assert template["color"] == "#667eea"
        assert template["icon"] == "🎯"
        assert "tasks" in template
        assert len(template["tasks"]) == 4

    def test_get_work_template(self):
        """Get work template details"""
        template = ProjectTemplateService.get_template("work")

        assert template["id"] == "work"
        assert template["name"] == "Work Project"
        assert len(template["tasks"]) == 7

    def test_get_software_dev_template(self):
        """Get software_dev template details"""
        template = ProjectTemplateService.get_template("software_dev")

        assert template["id"] == "software_dev"
        assert template["name"] == "Software Development"
        assert template["icon"] == "💻"
        assert len(template["tasks"]) == 8

    def test_get_invalid_template_raises(self):
        """Get invalid template raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ProjectTemplateService.get_template("invalid_template")

        assert "Template 'invalid_template' not found" in str(exc_info.value)

    def test_template_task_structure(self):
        """Template tasks have required fields"""
        template = ProjectTemplateService.get_template("personal")

        for task in template["tasks"]:
            assert "title" in task
            assert "description" in task
            assert "priority" in task
            assert "estimated_hours" in task


class TestCreateFromTemplate:
    """Tests for create_from_template method"""

    def test_create_personal_project(self, db, test_user):
        """Create project from personal template"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        assert project.id is not None
        assert project.userId == test_user.id
        assert project.name == "Personal Goals"
        assert project.description == "Track and achieve your personal objectives"
        assert project.color == "#667eea"
        assert project.icon == "🎯"

    def test_create_with_custom_name(self, db, test_user):
        """Create project with custom name"""
        project = ProjectTemplateService.create_from_template(
            template_id="work",
            user_id=test_user.id,
            db=db,
            custom_name="Q1 Marketing Campaign"
        )

        assert project.name == "Q1 Marketing Campaign"
        # Other fields should still come from template
        assert project.description == "Professional project with full lifecycle"

    def test_creates_tasks(self, db, test_user):
        """Project creation includes template tasks"""
        from app.models.task import Task

        project = ProjectTemplateService.create_from_template(
            template_id="study",
            user_id=test_user.id,
            db=db
        )

        # Query tasks for this project
        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        assert len(tasks) == 6
        task_titles = [t.title for t in tasks]
        assert "Research topic" in task_titles
        assert "Create study schedule" in task_titles
        assert "Take comprehensive notes" in task_titles

    def test_tasks_have_correct_fields(self, db, test_user):
        """Created tasks have correct field values"""
        from app.models.task import Task

        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        first_task = next((t for t in tasks if t.title == "Define clear goals"), None)

        assert first_task is not None
        assert first_task.userId == test_user.id
        assert first_task.priority == 1  # high = 1
        assert first_task.status == TaskStatus.PENDING
        assert first_task.estimatedMinutes == 60  # 1 hour = 60 minutes

    def test_tasks_have_staggered_due_dates(self, db, test_user):
        """Tasks have staggered due dates (1 week apart)"""
        from app.models.task import Task

        before = datetime.utcnow()
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).order_by(Task.dueDate).all()

        # First task should be due ~1 week from now
        assert tasks[0].dueDate > before
        assert tasks[0].dueDate < before + timedelta(weeks=2)

        # Each subsequent task should be ~1 week later
        for i in range(1, len(tasks)):
            diff = tasks[i].dueDate - tasks[i - 1].dueDate
            assert timedelta(days=6) < diff < timedelta(days=8)

    def test_create_invalid_template_raises(self, db, test_user):
        """Create from invalid template raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            ProjectTemplateService.create_from_template(
                template_id="nonexistent",
                user_id=test_user.id,
                db=db
            )

        assert "Template 'nonexistent' not found" in str(exc_info.value)

    def test_create_software_dev_project(self, db, test_user):
        """Create software development project"""
        from app.models.task import Task

        project = ProjectTemplateService.create_from_template(
            template_id="software_dev",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        assert len(tasks) == 8
        task_titles = [t.title for t in tasks]
        assert "Technical specification" in task_titles
        assert "Database design" in task_titles
        assert "Backend API development" in task_titles
        assert "Frontend development" in task_titles
        assert "Unit & integration tests" in task_titles

    def test_create_event_project(self, db, test_user):
        """Create event planning project"""
        project = ProjectTemplateService.create_from_template(
            template_id="event",
            user_id=test_user.id,
            db=db
        )

        assert project.name == "Event Planning"
        assert project.icon == "🎉"


class TestTemplateContents:
    """Tests for template data integrity"""

    def test_all_templates_have_unique_ids(self):
        """All templates have unique IDs"""
        templates = ProjectTemplateService.list_templates()
        ids = [t["id"] for t in templates]
        assert len(ids) == len(set(ids))

    def test_all_templates_have_colors(self):
        """All templates have valid color codes"""
        for template_id in ProjectTemplateService.TEMPLATES.keys():
            template = ProjectTemplateService.get_template(template_id)
            assert template["color"].startswith("#")
            assert len(template["color"]) == 7  # #RRGGBB format

    def test_all_templates_have_icons(self):
        """All templates have icons"""
        for template_id in ProjectTemplateService.TEMPLATES.keys():
            template = ProjectTemplateService.get_template(template_id)
            assert template["icon"] is not None
            assert len(template["icon"]) > 0

    def test_all_tasks_have_valid_priorities(self):
        """All template tasks have valid priority values"""
        valid_priorities = {"high", "medium", "low"}

        for template_id in ProjectTemplateService.TEMPLATES.keys():
            template = ProjectTemplateService.get_template(template_id)
            for task in template["tasks"]:
                assert task["priority"] in valid_priorities, \
                    f"Invalid priority '{task['priority']}' in template '{template_id}'"

    def test_all_tasks_have_positive_hours(self):
        """All template tasks have positive estimated hours"""
        for template_id in ProjectTemplateService.TEMPLATES.keys():
            template = ProjectTemplateService.get_template(template_id)
            for task in template["tasks"]:
                assert task["estimated_hours"] > 0, \
                    f"Invalid hours in template '{template_id}'"


class TestTemplateServiceIntegration:
    """Integration tests for template service workflows"""

    def test_list_then_create_workflow(self, db, test_user):
        """List templates, select one, create project"""
        # 1. List available templates
        templates = ProjectTemplateService.list_templates()
        assert len(templates) > 0

        # 2. Select a template (e.g., by task count)
        selected = min(templates, key=lambda t: t["task_count"])
        assert selected["id"] == "personal"

        # 3. Get full template details
        full_template = ProjectTemplateService.get_template(selected["id"])
        assert "tasks" in full_template

        # 4. Create project
        project = ProjectTemplateService.create_from_template(
            template_id=selected["id"],
            user_id=test_user.id,
            db=db
        )
        assert project.id is not None

    def test_multiple_projects_from_same_template(self, db, test_user):
        """Create multiple projects from same template"""
        project1 = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db,
            custom_name="2024 Goals"
        )

        project2 = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db,
            custom_name="2025 Goals"
        )

        assert project1.id != project2.id
        assert project1.name == "2024 Goals"
        assert project2.name == "2025 Goals"
