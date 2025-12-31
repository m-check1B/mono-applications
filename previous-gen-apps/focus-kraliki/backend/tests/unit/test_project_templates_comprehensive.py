"""
Comprehensive Unit tests for Project Templates Service
Tests template listing, creation, and task generation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.services.project_templates import ProjectTemplateService
from app.models.task import Project, Task, TaskStatus


class TestTemplateConstants:
    """Tests for template definitions"""

    def test_templates_exist(self):
        """All expected templates exist"""
        expected_templates = ["personal", "work", "study", "event", "software_dev"]
        for template_id in expected_templates:
            assert template_id in ProjectTemplateService.TEMPLATES

    def test_template_structure(self):
        """Templates have required fields"""
        for template_id, template in ProjectTemplateService.TEMPLATES.items():
            assert "name" in template
            assert "description" in template
            assert "color" in template
            assert "icon" in template
            assert "tasks" in template
            assert isinstance(template["tasks"], list)
            assert len(template["tasks"]) > 0

    def test_task_structure(self):
        """Template tasks have required fields"""
        for template_id, template in ProjectTemplateService.TEMPLATES.items():
            for task in template["tasks"]:
                assert "title" in task
                assert "description" in task
                assert "priority" in task
                assert "estimated_hours" in task
                assert task["priority"] in ["high", "medium", "low"]


class TestListTemplates:
    """Tests for list_templates method"""

    def test_list_templates_returns_all(self):
        """List returns all templates"""
        templates = ProjectTemplateService.list_templates()
        assert len(templates) == len(ProjectTemplateService.TEMPLATES)

    def test_list_templates_structure(self):
        """Listed templates have correct structure"""
        templates = ProjectTemplateService.list_templates()
        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "color" in template
            assert "icon" in template
            assert "task_count" in template
            assert template["task_count"] > 0

    def test_list_templates_task_count_accurate(self):
        """Task count matches actual tasks"""
        templates = ProjectTemplateService.list_templates()
        for template in templates:
            original = ProjectTemplateService.TEMPLATES[template["id"]]
            assert template["task_count"] == len(original["tasks"])


class TestGetTemplate:
    """Tests for get_template method"""

    def test_get_existing_template(self):
        """Get template by valid ID"""
        template = ProjectTemplateService.get_template("personal")
        assert template["id"] == "personal"
        assert template["name"] == "Personal Goals"
        assert "tasks" in template

    def test_get_all_templates_by_id(self):
        """Get each template by ID"""
        for template_id in ProjectTemplateService.TEMPLATES:
            template = ProjectTemplateService.get_template(template_id)
            assert template["id"] == template_id

    def test_get_nonexistent_template(self):
        """Get non-existent template raises error"""
        with pytest.raises(ValueError) as exc_info:
            ProjectTemplateService.get_template("nonexistent")
        assert "not found" in str(exc_info.value)

    def test_get_template_returns_copy(self):
        """Get template returns copy, not original"""
        template = ProjectTemplateService.get_template("personal")
        template["name"] = "Modified"

        # Original should be unchanged
        original = ProjectTemplateService.TEMPLATES["personal"]
        assert original["name"] == "Personal Goals"


class TestCreateFromTemplate:
    """Tests for create_from_template method"""

    def test_create_project_from_personal_template(self, db, test_user):
        """Create project from personal template"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        assert project is not None
        assert project.name == "Personal Goals"
        assert project.userId == test_user.id
        assert project.color == "#667eea"
        assert project.icon == "🎯"

        # Check tasks were created
        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        assert len(tasks) == 4  # Personal template has 4 tasks

    def test_create_project_from_work_template(self, db, test_user):
        """Create project from work template"""
        project = ProjectTemplateService.create_from_template(
            template_id="work",
            user_id=test_user.id,
            db=db
        )

        assert project.name == "Work Project"
        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        assert len(tasks) == 7  # Work template has 7 tasks

    def test_create_project_with_custom_name(self, db, test_user):
        """Create project with custom name"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db,
            custom_name="My Custom Project"
        )

        assert project.name == "My Custom Project"
        # Description should still be from template
        assert "Track and achieve" in project.description

    def test_create_project_task_priorities(self, db, test_user):
        """Tasks have correct priority mapping"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        # Check priority mapping (high=1, medium=2, low=3)
        priorities = {task.title: task.priority for task in tasks}

        # First two tasks are high priority
        assert priorities["Define clear goals"] == 1
        assert priorities["Create action plan"] == 1
        # Next two are medium
        assert priorities["Set milestones"] == 2
        assert priorities["Weekly review"] == 2

    def test_create_project_task_status(self, db, test_user):
        """All tasks start as pending"""
        project = ProjectTemplateService.create_from_template(
            template_id="study",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        for task in tasks:
            assert task.status == TaskStatus.PENDING

    def test_create_project_task_due_dates(self, db, test_user):
        """Tasks have staggered due dates"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).order_by(Task.dueDate).all()

        # Due dates should be staggered by 1 week
        for i, task in enumerate(tasks):
            assert task.dueDate is not None
            if i > 0:
                diff = task.dueDate - tasks[i-1].dueDate
                assert diff.days >= 6  # Approximately 1 week

    def test_create_project_estimated_minutes(self, db, test_user):
        """Tasks have estimated minutes converted from hours"""
        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        # Find a specific task and check its estimate
        for task in tasks:
            if task.title == "Create action plan":
                # Template says 2 hours = 120 minutes
                assert task.estimatedMinutes == 120
                break

    def test_create_project_from_invalid_template(self, db, test_user):
        """Create from invalid template raises error"""
        with pytest.raises(ValueError) as exc_info:
            ProjectTemplateService.create_from_template(
                template_id="nonexistent",
                user_id=test_user.id,
                db=db
            )
        assert "not found" in str(exc_info.value)

    def test_create_all_templates(self, db, test_user):
        """Create projects from all templates"""
        for template_id in ProjectTemplateService.TEMPLATES:
            project = ProjectTemplateService.create_from_template(
                template_id=template_id,
                user_id=test_user.id,
                db=db
            )

            assert project is not None
            assert project.userId == test_user.id

            # Verify task count matches template
            tasks = db.query(Task).filter(Task.projectId == project.id).all()
            expected_count = len(ProjectTemplateService.TEMPLATES[template_id]["tasks"])
            assert len(tasks) == expected_count

    def test_create_project_timestamps(self, db, test_user):
        """Project and tasks have creation timestamps"""
        before = datetime.utcnow()

        project = ProjectTemplateService.create_from_template(
            template_id="personal",
            user_id=test_user.id,
            db=db
        )

        after = datetime.utcnow()

        assert project.createdAt is not None
        assert before <= project.createdAt <= after

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        for task in tasks:
            assert task.createdAt is not None
            assert before <= task.createdAt <= after


class TestSoftwareDevTemplate:
    """Specific tests for software development template"""

    def test_software_dev_has_all_phases(self, db, test_user):
        """Software dev template covers all development phases"""
        project = ProjectTemplateService.create_from_template(
            template_id="software_dev",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        task_titles = [task.title for task in tasks]

        # Check for key development phases
        expected_phases = [
            "Technical specification",
            "Database design",
            "Backend API development",
            "Frontend development",
            "Unit & integration tests"
        ]

        for phase in expected_phases:
            assert phase in task_titles

    def test_software_dev_estimates_realistic(self, db, test_user):
        """Software dev estimates are reasonable"""
        project = ProjectTemplateService.create_from_template(
            template_id="software_dev",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()

        # Total estimate should be substantial for full-stack project
        total_minutes = sum(task.estimatedMinutes or 0 for task in tasks)
        total_hours = total_minutes / 60

        # Based on template: should be around 154 hours
        assert total_hours >= 100
        assert total_hours <= 200


class TestEventTemplate:
    """Specific tests for event planning template"""

    def test_event_has_pre_and_post_tasks(self, db, test_user):
        """Event template has pre and post-event tasks"""
        project = ProjectTemplateService.create_from_template(
            template_id="event",
            user_id=test_user.id,
            db=db
        )

        tasks = db.query(Task).filter(Task.projectId == project.id).all()
        task_titles = [task.title for task in tasks]

        # Pre-event planning
        assert "Define event concept" in task_titles
        assert "Budget planning" in task_titles
        assert "Venue selection" in task_titles

        # Post-event
        assert "Post-event follow-up" in task_titles
