"""Integration facade for the Focus by Kraliki planning backend.

The `PlanningModule` class wraps the existing FastAPI application and domain
services so other Python services in the Ocelot ecosystem can import Focus by Kraliki
as a library instead of going through the HTTP interface. The facade offers a
small, well-typed surface area for common workflows (task creation, listing,
lookup) while still exposing the underlying FastAPI application when needed
(e.g. mounting on another ASGI server).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from contextlib import contextmanager

from app.core.database import SessionLocal, Base, engine
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse, TaskUpdate
from app.models.task import Task, TaskStatus
from app.core.security import generate_id


class PlanningModuleError(Exception):
    """Raised when Focus by Kraliki cannot complete a requested module operation."""


@dataclass(slots=True)
class PlanningModuleConfig:
    """Configuration values for the `PlanningModule` facade."""

    integrated: bool = False
    auto_create_schema: bool = True


@contextmanager
def _session_scope():
    """Provide a transactional scope around a series of operations."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class PlanningModule:
    """Expose Focus by Kraliki planning capabilities to other services."""

    def __init__(self, config: Optional[PlanningModuleConfig] = None) -> None:
        self.config = config or PlanningModuleConfig()
        self._fastapi_app = None

        if self.config.auto_create_schema:
            Base.metadata.create_all(bind=engine)

    # ------------------------------------------------------------------
    # ASGI / FastAPI integration
    # ------------------------------------------------------------------
    @property
    def fastapi_app(self):
        """Return the FastAPI application for mounting or inspection."""

        if self._fastapi_app is None:
            from app.main import app as fastapi_app  # Lazy import to avoid side effects

            self._fastapi_app = fastapi_app
        return self._fastapi_app

    def asgi_app(self):
        """Alias for `fastapi_app` to support Starlette-style mounting."""

        return self.fastapi_app

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------
    async def create_task(self, *, user_id: str, data: TaskCreate | Dict[str, Any]) -> TaskResponse:
        """Create a task on behalf of `user_id`.

        Parameters
        ----------
        user_id:
            The owner of the new task. In standalone mode this is typically the
            authenticated user; in integrated mode the caller must supply the
            correct user identifier from the shared directory.
        data:
            Task payload (Pydantic model or raw mapping). Only fields defined in
            `TaskCreate` are accepted.
        """

        return await asyncio.to_thread(self._create_task_sync, user_id, data)

    async def get_task(self, *, user_id: str, task_id: str) -> Optional[TaskResponse]:
        """Return a single task or `None` if it does not exist for the user."""

        return await asyncio.to_thread(self._get_task_sync, user_id, task_id)

    async def list_tasks(
        self,
        *,
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 50,
    ) -> TaskListResponse:
        """Return a limited set of tasks for the given user."""

        return await asyncio.to_thread(self._list_tasks_sync, user_id, status, limit)

    async def update_task(
        self,
        *,
        user_id: str,
        task_id: str,
        update: TaskUpdate | Dict[str, Any],
    ) -> TaskResponse:
        """Apply a partial update to a task owned by `user_id`. Raises if missing."""

        return await asyncio.to_thread(self._update_task_sync, user_id, task_id, update)

    async def delete_task(self, *, user_id: str, task_id: str) -> bool:
        """Delete a task owned by `user_id`. Returns True if the task existed."""

        return await asyncio.to_thread(self._delete_task_sync, user_id, task_id)

    # ------------------------------------------------------------------
    # Synchronous helpers executed in worker threads
    # ------------------------------------------------------------------
    def _create_task_sync(self, user_id: str, data: TaskCreate | Dict[str, Any]) -> TaskResponse:
        payload = data if isinstance(data, TaskCreate) else TaskCreate.model_validate(data)

        with _session_scope() as session:
            task = Task(
                id=generate_id(),
                userId=user_id,
                **payload.model_dump(exclude_unset=True),
            )
            session.add(task)
            session.flush()
            session.refresh(task)
            return TaskResponse.model_validate(task)

    def _get_task_sync(self, user_id: str, task_id: str) -> Optional[TaskResponse]:
        with _session_scope() as session:
            task = (
                session.query(Task)
                .filter(Task.id == task_id, Task.userId == user_id)
                .first()
            )
            return TaskResponse.model_validate(task) if task else None

    def _list_tasks_sync(
        self, user_id: str, status: Optional[TaskStatus], limit: int
    ) -> TaskListResponse:
        with _session_scope() as session:
            query = session.query(Task).filter(Task.userId == user_id)
            if status is not None:
                query = query.filter(Task.status == status)
            tasks = query.order_by(Task.createdAt.desc()).limit(limit).all()
            total = (
                session.query(Task).filter(Task.userId == user_id).count()
            )

            return TaskListResponse(
                tasks=[TaskResponse.model_validate(t) for t in tasks],
                total=total,
            )

    def _update_task_sync(
        self,
        user_id: str,
        task_id: str,
        update: TaskUpdate | Dict[str, Any],
    ) -> TaskResponse:
        payload = update if isinstance(update, TaskUpdate) else TaskUpdate.model_validate(update)

        with _session_scope() as session:
            task = (
                session.query(Task)
                .filter(Task.id == task_id, Task.userId == user_id)
                .first()
            )
            if task is None:
                raise PlanningModuleError("Task not found")

            update_data = payload.model_dump(exclude_unset=True)
            if (
                "status" in update_data
                and update_data["status"] == TaskStatus.COMPLETED
                and task.status != TaskStatus.COMPLETED
            ):
                update_data.setdefault("completedAt", datetime.utcnow())

            for key, value in update_data.items():
                setattr(task, key, value)

            session.flush()
            session.refresh(task)
            return TaskResponse.model_validate(task)

    def _delete_task_sync(self, user_id: str, task_id: str) -> bool:
        with _session_scope() as session:
            task = (
                session.query(Task)
                .filter(Task.id == task_id, Task.userId == user_id)
                .first()
            )
            if task is None:
                return False

            session.delete(task)
            session.flush()
            return True


__all__ = ["PlanningModule", "PlanningModuleConfig", "PlanningModuleError"]
