"""
Unit tests for Focus Brain Service - The Central AI Intelligence
Tests goal understanding, daily planning, Q&A, next action suggestions, and knowledge capture
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task, TaskStatus, Project
from app.models.knowledge_item import KnowledgeItem
from app.models.item_type import ItemType
from app.services.brain import FocusBrain
from app.core.security_v2 import generate_id


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing"""
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value='{"goal_title": "Test Goal", "suggested_tasks": [{"title": "Task 1", "priority": 5, "estimated_minutes": 60}]}')
    return provider


@pytest.fixture
def mock_flow_memory():
    """Mock FlowMemoryService for testing"""
    memory = MagicMock()
    memory.store = AsyncMock(return_value=True)
    memory.get_recent = AsyncMock(return_value=[])
    return memory


@pytest.fixture
def mock_scheduler():
    """Mock AISchedulerService for testing"""
    scheduler = MagicMock()
    scheduler.prioritize_tasks = MagicMock(return_value=[])
    scheduler.get_focus_recommendations = MagicMock(return_value={"peak_productivity_hours": [9, 10, 14]})
    return scheduler


@pytest.fixture
def brain(test_user, db, mock_flow_memory, mock_scheduler):
    """Create FocusBrain instance with mocks"""
    with patch('app.services.brain.FlowMemoryService') as mock_memory_class:
        mock_memory_class.return_value = mock_flow_memory
        with patch('app.services.brain.AISchedulerService') as mock_sched_class:
            mock_sched_class.return_value = mock_scheduler
            brain = FocusBrain(test_user, db)
    brain.memory = mock_flow_memory
    brain.scheduler = mock_scheduler
    return brain


class TestFocusBrainInit:
    """Test FocusBrain initialization"""

    def test_brain_init_with_user(self, test_user, db):
        """Brain initializes with user and db"""
        with patch('app.services.brain.FlowMemoryService'):
            brain = FocusBrain(test_user, db)

        assert brain.user == test_user
        assert brain.user_id == str(test_user.id)
        assert brain.db == db
        assert brain.scheduler is not None
        assert brain.memory is not None


class TestUnderstandGoal:
    """Test goal understanding and parsing"""

    @pytest.mark.asyncio
    async def test_understand_goal_success(self, brain, mock_ai_provider, mock_flow_memory):
        """Successfully parse a goal into structured format"""
        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Parse this goal"):
                result = await brain.understand_goal("Launch my product by February 2026")

        assert result["success"] == True
        assert result["original"] == "Launch my product by February 2026"
        assert "parsed" in result
        assert "message" in result

    @pytest.mark.asyncio
    async def test_understand_goal_extracts_json_from_markdown(self, brain, mock_ai_provider, mock_flow_memory):
        """Parse goal when AI response contains markdown code blocks"""
        mock_ai_provider.generate = AsyncMock(return_value='```json\n{"goal_title": "Test", "suggested_tasks": []}\n```')

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Parse this goal"):
                result = await brain.understand_goal("Test goal")

        assert result["success"] == True
        assert "parsed" in result

    @pytest.mark.asyncio
    async def test_understand_goal_handles_invalid_json(self, brain, mock_ai_provider, mock_flow_memory):
        """Handle gracefully when AI returns invalid JSON"""
        mock_ai_provider.generate = AsyncMock(return_value="This is not valid JSON at all")

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Parse this goal"):
                result = await brain.understand_goal("Bad goal")

        assert result["success"] == False
        assert "error" in result
        assert "couldn't parse" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_understand_goal_stores_in_memory(self, brain, mock_ai_provider, mock_flow_memory):
        """Goal parsing stores result in memory"""
        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Parse this goal"):
                await brain.understand_goal("Test goal")

        mock_flow_memory.store.assert_called_once()

    @pytest.mark.asyncio
    async def test_understand_goal_handles_ai_error(self, brain, mock_ai_provider):
        """Handle gracefully when AI provider fails"""
        mock_ai_provider.generate = AsyncMock(side_effect=Exception("API Error"))

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Parse this goal"):
                result = await brain.understand_goal("Test goal")

        assert result["success"] == False
        assert "API Error" in result["error"]


class TestCreateFromGoal:
    """Test project/task creation from parsed goal"""

    @pytest.mark.asyncio
    async def test_create_project_from_goal(self, brain, db, test_user):
        """Create project from parsed goal"""
        parsed_goal = {
            "suggested_project_name": "Product Launch",
            "goal_description": "Launch product by Q1",
            "suggested_tasks": [
                {"title": "Define MVP", "priority": 5, "estimated_minutes": 120},
                {"title": "Build landing page", "priority": 3, "estimated_minutes": 180}
            ]
        }

        result = await brain.create_from_goal(parsed_goal)

        assert "project" in result
        assert result["project"]["name"] == "Product Launch"
        assert len(result["tasks"]) == 2
        assert "message" in result

    @pytest.mark.asyncio
    async def test_create_tasks_with_deadline(self, brain, db, test_user):
        """Tasks get deadline from goal"""
        deadline = (datetime.utcnow() + timedelta(days=30)).isoformat()
        parsed_goal = {
            "suggested_project_name": "Test Project",
            "deadline": deadline,
            "suggested_tasks": [
                {"title": "Task 1", "priority": 5, "estimated_minutes": 60}
            ]
        }

        result = await brain.create_from_goal(parsed_goal)

        # Verify task was created with due date
        task = db.query(Task).filter(Task.userId == test_user.id).first()
        assert task is not None
        assert task.dueDate is not None

    @pytest.mark.asyncio
    async def test_create_tasks_default_values(self, brain, db, test_user):
        """Tasks use default values when not specified"""
        parsed_goal = {
            "suggested_project_name": "Test Project",
            "suggested_tasks": [
                {"title": "Minimal Task"}  # No priority or estimate
            ]
        }

        result = await brain.create_from_goal(parsed_goal)

        task = db.query(Task).filter(Task.userId == test_user.id).first()
        assert task.priority == 3  # Default integer priority
        assert task.estimatedMinutes == 60


class TestGetDailyPlan:
    """Test daily plan generation"""

    @pytest.mark.asyncio
    async def test_get_daily_plan_no_tasks(self, brain, test_user, mock_scheduler):
        """Daily plan with no active tasks"""
        mock_scheduler.prioritize_tasks.return_value = []
        mock_scheduler.get_focus_recommendations.return_value = {"peak_productivity_hours": [9, 10, 14]}

        with patch.object(brain, 'scheduler', mock_scheduler):
            result = await brain.get_daily_plan()

        assert "greeting" in result
        assert "message" in result
        assert result["total_active"] == 0
        assert result["top_tasks"] == []

    @pytest.mark.asyncio
    async def test_get_daily_plan_with_tasks(self, brain, db, test_user, mock_scheduler):
        """Daily plan prioritizes and shows top tasks"""
        # Create some tasks
        tasks = []
        for i in range(5):
            task = Task(
                id=generate_id(),
                userId=test_user.id,
                title=f"Test Task {i}",
                status=TaskStatus.PENDING,
                priority=3,
                createdAt=datetime.utcnow()
            )
            db.add(task)
            tasks.append(task)
        db.commit()

        # Mock scheduler to return prioritized tasks
        prioritized = [
            {"task": t, "priority_score": 50+i*10, "recommendation": f"Do task {i}"}
            for i, t in enumerate(tasks[:3])
        ]
        mock_scheduler.prioritize_tasks.return_value = prioritized
        mock_scheduler.get_focus_recommendations.return_value = {"peak_productivity_hours": [9, 10, 14]}

        result = await brain.get_daily_plan()

        assert result["total_active"] == 5
        assert len(result["top_tasks"]) <= 3

    @pytest.mark.asyncio
    async def test_get_daily_plan_greeting_by_time(self, brain, mock_scheduler):
        """Greeting changes based on time of day"""
        mock_scheduler.prioritize_tasks.return_value = []
        mock_scheduler.get_focus_recommendations.return_value = {"peak_productivity_hours": []}

        result = await brain.get_daily_plan()

        hour = datetime.utcnow().hour
        if hour < 12:
            assert "morning" in result["greeting"].lower()
        elif hour < 17:
            assert "afternoon" in result["greeting"].lower()
        else:
            assert "evening" in result["greeting"].lower()


class TestAsk:
    """Test Brain Q&A functionality"""

    @pytest.mark.asyncio
    async def test_ask_basic_question(self, brain, mock_ai_provider, mock_flow_memory):
        """Ask Brain a basic question"""
        mock_ai_provider.generate = AsyncMock(return_value="You should focus on your highest priority task.")

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Answer this question"):
                result = await brain.ask("What should I work on?")

        assert result["success"] == True
        assert result["question"] == "What should I work on?"
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_ask_handles_error(self, brain, mock_ai_provider):
        """Ask handles AI errors gracefully"""
        mock_ai_provider.generate = AsyncMock(side_effect=Exception("Service unavailable"))

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Answer"):
                result = await brain.ask("Test question")

        assert result["success"] == False
        assert "trouble thinking" in result["answer"].lower()


class TestSuggestNextAction:
    """Test next action suggestions"""

    @pytest.mark.asyncio
    async def test_suggest_no_tasks(self, brain, mock_scheduler):
        """Suggest adding a goal when no tasks exist"""
        mock_scheduler.prioritize_tasks.return_value = []

        result = await brain.suggest_next_action()

        assert result["action"] == "add_goal"
        assert "no active tasks" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_suggest_continue_in_progress(self, brain, db, test_user, mock_scheduler):
        """Suggest continuing in-progress task"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Work In Progress",
            status=TaskStatus.IN_PROGRESS,
            priority=3,
            createdAt=datetime.utcnow()
        )
        db.add(task)
        db.commit()

        # Mock scheduler
        mock_scheduler.prioritize_tasks.return_value = [
            {"task": task, "priority_score": 50, "recommendation": "Continue"}
        ]

        result = await brain.suggest_next_action()

        assert result["action"] == "continue"
        assert "Work In Progress" in result["message"]
        assert result["task"]["title"] == "Work In Progress"


class TestCapture:
    """Test AI-First Capture functionality"""

    @pytest.fixture
    def setup_item_types(self, db, test_user):
        """Create default item types for user"""
        types = [
            ItemType(id=generate_id(), userId=test_user.id, name="Notes", icon="📝", color="#blue"),
            ItemType(id=generate_id(), userId=test_user.id, name="Ideas", icon="💡", color="#yellow"),
            ItemType(id=generate_id(), userId=test_user.id, name="Tasks", icon="✅", color="#green"),
            ItemType(id=generate_id(), userId=test_user.id, name="Plans", icon="📋", color="#purple"),
        ]
        for t in types:
            db.add(t)
        db.commit()
        return types

    @pytest.mark.asyncio
    async def test_capture_classify_idea(self, brain, mock_ai_provider, setup_item_types):
        """Capture classifies 'idea' input correctly"""
        mock_ai_provider.generate = AsyncMock(return_value='{"type": "Ideas", "title": "New App Idea", "content": "Build a productivity app", "confidence": 0.9}')

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Classify input"):
                with patch('app.services.brain.ensure_default_item_types'):
                    result = await brain.capture("I have an idea for a new app")

        assert result["success"] == True
        assert result["classified"]["type"] == "Ideas"
        assert result["classified"]["confidence"] >= 0.8

    @pytest.mark.asyncio
    async def test_capture_without_creating(self, brain, mock_ai_provider, setup_item_types, db, test_user):
        """Capture without create_item=True doesn't persist"""
        mock_ai_provider.generate = AsyncMock(return_value='{"type": "Notes", "title": "Test Note", "content": "Content", "confidence": 0.9}')

        initial_count = db.query(KnowledgeItem).filter(KnowledgeItem.userId == test_user.id).count()

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Classify"):
                with patch('app.services.brain.ensure_default_item_types'):
                    result = await brain.capture("Note to self: test", create_item=False)

        final_count = db.query(KnowledgeItem).filter(KnowledgeItem.userId == test_user.id).count()

        assert result["success"] == True
        assert "created" not in result
        assert initial_count == final_count

    @pytest.mark.asyncio
    async def test_capture_handles_ai_error(self, brain, mock_ai_provider, setup_item_types):
        """Capture handles AI errors gracefully"""
        mock_ai_provider.generate = AsyncMock(side_effect=Exception("API Error"))

        with patch('app.services.brain.get_ai_provider', return_value=mock_ai_provider):
            with patch('app.services.brain.get_prompt', return_value="Classify"):
                with patch('app.services.brain.ensure_default_item_types'):
                    result = await brain.capture("Test input")

        assert result["success"] == False
        assert "couldn't classify" in result["message"].lower()


class TestGetKnowledgeSummary:
    """Test knowledge summary functionality"""

    @pytest.mark.asyncio
    async def test_get_summary_empty(self, brain):
        """Summary with no items"""
        with patch('app.services.brain.ensure_default_item_types'):
            result = await brain.get_knowledge_summary()

        assert result["total_items"] == 0
        assert "types" in result

    @pytest.mark.asyncio
    async def test_get_summary_with_items(self, brain, db, test_user):
        """Summary counts items by type"""
        # Create item type
        item_type = ItemType(
            id=generate_id(),
            userId=test_user.id,
            name="Notes",
            icon="📝",
            color="#blue"
        )
        db.add(item_type)
        db.flush()

        # Create knowledge items
        for i in range(3):
            item = KnowledgeItem(
                id=generate_id(),
                userId=test_user.id,
                typeId=item_type.id,
                title=f"Note {i}",
                content=f"Content {i}",
                completed=False
            )
            db.add(item)
        db.commit()

        with patch('app.services.brain.ensure_default_item_types'):
            result = await brain.get_knowledge_summary()

        assert result["total_items"] == 3
        notes_type = next((t for t in result["types"] if t["type"] == "Notes"), None)
        assert notes_type is not None
        assert notes_type["count"] == 3
        assert len(notes_type["recent"]) <= 5
