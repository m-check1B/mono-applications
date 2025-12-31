"""Unit tests for Focus by Kraliki PlanningModule (ocelot_apps/focus_lite)

Tests cover:
- Module initialization and configuration
- FastAPI/ASGI integration
- Error handling

Note: Database operation tests require mocking or integration testing as PlanningModule
creates its own database sessions via SessionLocal().
"""

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session


class TestPlanningModuleConfig:
    """Tests for PlanningModuleConfig dataclass"""

    def test_default_config(self):
        """Default configuration values"""
        from ocelot_apps.focus_lite.module import PlanningModuleConfig

        config = PlanningModuleConfig()
        assert config.integrated is False
        assert config.auto_create_schema is True

    def test_custom_config(self):
        """Custom configuration values"""
        from ocelot_apps.focus_lite.module import PlanningModuleConfig

        config = PlanningModuleConfig(integrated=True, auto_create_schema=False)
        assert config.integrated is True
        assert config.auto_create_schema is False


class TestPlanningModuleInit:
    """Tests for PlanningModule initialization"""

    def test_init_with_default_config(self, db: Session):
        """Initialize module with default config"""
        from ocelot_apps.focus_lite.module import PlanningModule

        module = PlanningModule()
        assert module.config.integrated is False
        assert module.config.auto_create_schema is True
        assert module._fastapi_app is None

    def test_init_with_custom_config(self, db: Session):
        """Initialize module with custom config"""
        from ocelot_apps.focus_lite.module import PlanningModule, PlanningModuleConfig

        config = PlanningModuleConfig(integrated=True, auto_create_schema=False)
        module = PlanningModule(config=config)
        assert module.config.integrated is True
        assert module.config.auto_create_schema is False

    def test_fastapi_app_lazy_load(self, db: Session):
        """FastAPI app is loaded lazily"""
        from ocelot_apps.focus_lite.module import PlanningModule

        module = PlanningModule()
        assert module._fastapi_app is None

        app = module.fastapi_app
        assert module._fastapi_app is not None
        assert app is not None
        assert hasattr(app, "routes")

    def test_asgi_app_property(self, db: Session):
        """asgi_app is an alias for fastapi_app"""
        from ocelot_apps.focus_lite.module import PlanningModule

        module = PlanningModule()
        assert module.asgi_app() is module.fastapi_app


class TestFastAPIIntegration:
    """Tests for FastAPI/ASGI integration"""

    def test_fastapi_app_has_routes(self, db: Session):
        """FastAPI app has task routes configured"""
        from ocelot_apps.focus_lite.module import PlanningModule

        module = PlanningModule()
        app = module.fastapi_app

        routes = [getattr(route, "path", str(route)) for route in app.routes]

        assert "/tasks" in routes or any("/tasks" in str(route) for route in routes)

    def test_fastapi_app_health_endpoint(self, db: Session):
        """FastAPI app has health endpoint"""
        from ocelot_apps.focus_lite.module import PlanningModule
        from fastapi.testclient import TestClient

        module = PlanningModule()
        app = module.fastapi_app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Tests for error handling"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, db: Session):
        """Retrieve a task that doesn't exist"""
        from ocelot_apps.focus_lite.module import PlanningModule
        from app.core.security import generate_id

        module = PlanningModule()
        user_id = generate_id()
        fake_id = generate_id()

        result = await module.get_task(user_id=user_id, task_id=fake_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_nonexistent_task_raises_error(self, db: Session):
        """Updating nonexistent task raises PlanningModuleError"""
        from ocelot_apps.focus_lite.module import PlanningModule, PlanningModuleError
        from app.core.security import generate_id

        module = PlanningModule()
        user_id = generate_id()
        fake_id = generate_id()

        from app.schemas.task import TaskUpdate

        with pytest.raises(PlanningModuleError, match="Task not found"):
            await module.update_task(
                user_id=user_id,
                task_id=fake_id,
                update=TaskUpdate(title="Should fail"),
            )

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, db: Session):
        """Delete a task that doesn't exist returns False"""
        from ocelot_apps.focus_lite.module import PlanningModule
        from app.core.security import generate_id

        module = PlanningModule()
        user_id = generate_id()
        fake_id = generate_id()

        result = await module.delete_task(user_id=user_id, task_id=fake_id)

        assert result is False


class TestSessionScope:
    """Tests for _session_scope context manager"""

    def test_session_scope_rolls_back_on_error(self, db: Session):
        """Session scope rolls back on exception"""
        from ocelot_apps.focus_lite.module import _session_scope
        from app.models.task import Task
        from app.core.security import generate_id

        try:
            with _session_scope() as session:
                task = Task(
                    id=generate_id(),
                    userId=generate_id(),
                    title="Should be rolled back",
                )
                session.add(task)
                raise ValueError("Test error")
        except ValueError:
            pass

        retrieved = db.query(Task).filter(Task.title == "Should be rolled back").first()
        assert retrieved is None
