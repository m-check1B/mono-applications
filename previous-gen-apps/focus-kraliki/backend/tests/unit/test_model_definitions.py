"""
Unit tests for SQLAlchemy model definitions.
Ensures every model module registers tables and exposes columns.
"""

import pytest

from app.core.database import Base
from app.models.activity import Activity
from app.models.agent_session import AgentSession, AgentSessionEvent
from app.models.ai_conversation import AIConversation
from app.models.command_history import CommandHistory
from app.models.comment import Comment
from app.models.event import Event
from app.models.file_search_document import FileSearchDocument
from app.models.file_search_store import FileSearchStore
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.models.request_telemetry import RequestTelemetry
from app.models.search_index import SearchIndex
from app.models.session import Session
from app.models.shadow_profile import ShadowProfile, ShadowInsight
from app.models.task import Task, Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.voice_recording import VoiceRecording
from app.models.workflow_template import WorkflowTemplate
from app.models.workspace import Workspace, WorkspaceMember


MODEL_CLASSES = [
    Activity,
    AgentSession,
    AgentSessionEvent,
    AIConversation,
    CommandHistory,
    Comment,
    Event,
    FileSearchDocument,
    FileSearchStore,
    ItemType,
    KnowledgeItem,
    RequestTelemetry,
    SearchIndex,
    Session,
    ShadowProfile,
    ShadowInsight,
    Task,
    Project,
    TimeEntry,
    User,
    VoiceRecording,
    WorkflowTemplate,
    Workspace,
    WorkspaceMember,
]


@pytest.mark.parametrize("model_class", MODEL_CLASSES)
def test_model_registered_in_metadata(model_class):
    """Each model should register its table with SQLAlchemy metadata."""
    assert model_class.__tablename__ in Base.metadata.tables


@pytest.mark.parametrize("model_class", MODEL_CLASSES)
def test_model_has_columns(model_class):
    """Each model should define at least one column."""
    table = model_class.__table__
    assert table is not None
    assert len(table.columns) > 0
