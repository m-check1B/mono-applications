"""
Project Template Service
Provides pre-configured project templates with tasks
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.models.task import Project, Task, TaskStatus


class ProjectTemplateService:
    """Service for creating projects from templates."""

    TEMPLATES = {
        "personal": {
            "name": "Personal Goals",
            "description": "Track and achieve your personal objectives",
            "color": "#667eea",
            "icon": "🎯",
            "tasks": [
                {
                    "title": "Define clear goals",
                    "description": "Write down specific, measurable goals",
                    "priority": "high",
                    "estimated_hours": 1
                },
                {
                    "title": "Create action plan",
                    "description": "Break down goals into actionable steps",
                    "priority": "high",
                    "estimated_hours": 2
                },
                {
                    "title": "Set milestones",
                    "description": "Define checkpoints to track progress",
                    "priority": "medium",
                    "estimated_hours": 1
                },
                {
                    "title": "Weekly review",
                    "description": "Review progress and adjust plan",
                    "priority": "medium",
                    "estimated_hours": 1
                }
            ]
        },
        "work": {
            "name": "Work Project",
            "description": "Professional project with full lifecycle",
            "color": "#f59e0b",
            "icon": "💼",
            "tasks": [
                {
                    "title": "Project kickoff meeting",
                    "description": "Align team on goals and deliverables",
                    "priority": "high",
                    "estimated_hours": 2
                },
                {
                    "title": "Requirements gathering",
                    "description": "Document all project requirements",
                    "priority": "high",
                    "estimated_hours": 8
                },
                {
                    "title": "Design & planning",
                    "description": "Create technical design and timeline",
                    "priority": "high",
                    "estimated_hours": 16
                },
                {
                    "title": "Implementation phase 1",
                    "description": "Build core functionality",
                    "priority": "medium",
                    "estimated_hours": 40
                },
                {
                    "title": "Testing & QA",
                    "description": "Comprehensive testing",
                    "priority": "medium",
                    "estimated_hours": 16
                },
                {
                    "title": "Deployment",
                    "description": "Deploy to production",
                    "priority": "low",
                    "estimated_hours": 4
                },
                {
                    "title": "Post-launch monitoring",
                    "description": "Monitor and fix issues",
                    "priority": "low",
                    "estimated_hours": 8
                }
            ]
        },
        "study": {
            "name": "Study Plan",
            "description": "Structured learning project",
            "color": "#10b981",
            "icon": "📚",
            "tasks": [
                {
                    "title": "Research topic",
                    "description": "Gather learning resources",
                    "priority": "high",
                    "estimated_hours": 2
                },
                {
                    "title": "Create study schedule",
                    "description": "Plan dedicated study time",
                    "priority": "high",
                    "estimated_hours": 1
                },
                {
                    "title": "Take comprehensive notes",
                    "description": "Document key concepts",
                    "priority": "medium",
                    "estimated_hours": 20
                },
                {
                    "title": "Practice exercises",
                    "description": "Apply knowledge through practice",
                    "priority": "medium",
                    "estimated_hours": 15
                },
                {
                    "title": "Review & self-test",
                    "description": "Test understanding",
                    "priority": "medium",
                    "estimated_hours": 5
                },
                {
                    "title": "Final assessment",
                    "description": "Comprehensive evaluation",
                    "priority": "low",
                    "estimated_hours": 2
                }
            ]
        },
        "event": {
            "name": "Event Planning",
            "description": "Organize and execute an event",
            "color": "#ef4444",
            "icon": "🎉",
            "tasks": [
                {
                    "title": "Define event concept",
                    "description": "Theme, purpose, and target audience",
                    "priority": "high",
                    "estimated_hours": 2
                },
                {
                    "title": "Budget planning",
                    "description": "Create detailed budget",
                    "priority": "high",
                    "estimated_hours": 3
                },
                {
                    "title": "Venue selection",
                    "description": "Find and book venue",
                    "priority": "high",
                    "estimated_hours": 5
                },
                {
                    "title": "Vendor coordination",
                    "description": "Catering, AV, decorations",
                    "priority": "medium",
                    "estimated_hours": 8
                },
                {
                    "title": "Marketing & invitations",
                    "description": "Promote event and manage RSVPs",
                    "priority": "medium",
                    "estimated_hours": 10
                },
                {
                    "title": "Day-of coordination",
                    "description": "Execute event plan",
                    "priority": "high",
                    "estimated_hours": 12
                },
                {
                    "title": "Post-event follow-up",
                    "description": "Thank sponsors, gather feedback",
                    "priority": "low",
                    "estimated_hours": 3
                }
            ]
        },
        "software_dev": {
            "name": "Software Development",
            "description": "Full-stack development project",
            "color": "#8b5cf6",
            "icon": "💻",
            "tasks": [
                {
                    "title": "Technical specification",
                    "description": "Document architecture and tech stack",
                    "priority": "high",
                    "estimated_hours": 8
                },
                {
                    "title": "Database design",
                    "description": "Schema, relationships, migrations",
                    "priority": "high",
                    "estimated_hours": 6
                },
                {
                    "title": "Backend API development",
                    "description": "Build REST/GraphQL APIs",
                    "priority": "high",
                    "estimated_hours": 40
                },
                {
                    "title": "Frontend development",
                    "description": "Build user interface",
                    "priority": "medium",
                    "estimated_hours": 50
                },
                {
                    "title": "Authentication & authorization",
                    "description": "Implement security layer",
                    "priority": "high",
                    "estimated_hours": 12
                },
                {
                    "title": "Unit & integration tests",
                    "description": "Write comprehensive tests",
                    "priority": "medium",
                    "estimated_hours": 20
                },
                {
                    "title": "CI/CD setup",
                    "description": "Automated deployment pipeline",
                    "priority": "low",
                    "estimated_hours": 8
                },
                {
                    "title": "Documentation",
                    "description": "API docs, user guide, README",
                    "priority": "low",
                    "estimated_hours": 10
                }
            ]
        }
    }

    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        """List all available project templates."""
        return [
            {
                "id": template_id,
                "name": template["name"],
                "description": template["description"],
                "color": template["color"],
                "icon": template["icon"],
                "task_count": len(template["tasks"])
            }
            for template_id, template in cls.TEMPLATES.items()
        ]

    @classmethod
    def create_from_template(
        cls,
        template_id: str,
        user_id: str,
        db: Session,
        custom_name: str = None
    ) -> Project:
        """
        Create a new project from a template.

        Args:
            template_id: Template identifier
            user_id: User ID to assign project to
            db: Database session
            custom_name: Custom project name (overrides template)

        Returns:
            Created project with tasks
        """
        if template_id not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_id}' not found")

        template = cls.TEMPLATES[template_id]

        # Create project - use camelCase column names matching the model
        project = Project(
            id=str(uuid.uuid4()),
            userId=user_id,
            name=custom_name or template["name"],
            description=template["description"],
            color=template["color"],
            icon=template["icon"],
            createdAt=datetime.utcnow()
        )

        db.add(project)
        db.flush()  # Get project ID

        # Priority mapping: template uses strings, model uses integers
        priority_map = {"high": 1, "medium": 2, "low": 3}

        # Create tasks from template
        base_date = datetime.utcnow()
        for idx, task_data in enumerate(template["tasks"]):
            # Stagger due dates (each task gets +1 week)
            due_date = base_date + timedelta(weeks=idx + 1)

            # Convert priority string to integer
            priority_str = task_data.get("priority", "medium")
            priority_int = priority_map.get(priority_str, 2)

            # Convert hours to minutes
            estimated_hours = task_data.get("estimated_hours", 0)
            estimated_minutes = int(estimated_hours * 60) if estimated_hours else None

            task = Task(
                id=str(uuid.uuid4()),
                userId=user_id,
                projectId=project.id,
                title=task_data["title"],
                description=task_data["description"],
                priority=priority_int,
                status=TaskStatus.PENDING,
                dueDate=due_date,
                estimatedMinutes=estimated_minutes,
                createdAt=datetime.utcnow()
            )
            db.add(task)

        db.commit()
        db.refresh(project)

        return project

    @classmethod
    def get_template(cls, template_id: str) -> Dict[str, Any]:
        """Get template details by ID."""
        if template_id not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_id}' not found")

        template = cls.TEMPLATES[template_id].copy()
        template["id"] = template_id
        return template
