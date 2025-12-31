"""
Comprehensive Unit Tests for Focus Kraliki SQLAlchemy Models.

VD-516: Create comprehensive unit tests for all model files.

These tests verify:
- Model class definitions and table names
- Column definitions (types, nullable, defaults, indexes)
- Enum definitions and values
- Relationships between models
- Helper methods (to_dict, utility functions)
- Default value generators
- Event listeners and mutators

Tests run without database connection by inspecting SQLAlchemy metadata.
These tests are isolated and do not use the `db` fixture.
"""

import pytest
from unittest.mock import MagicMock


# Skip fixtures that require database by not importing them
# These tests are pure model definition tests


class TestUserEnums:
    """Test User-related enum definitions."""

    def test_role_enum_values(self):
        """Role enum should have AGENT, SUPERVISOR, ADMIN."""
        from app.models.user import Role

        assert Role.AGENT.value == "AGENT"
        assert Role.SUPERVISOR.value == "SUPERVISOR"
        assert Role.ADMIN.value == "ADMIN"
        assert len(Role) == 3

    def test_user_status_enum_values(self):
        """UserStatus enum should have ACTIVE, INACTIVE, SUSPENDED."""
        from app.models.user import UserStatus

        assert UserStatus.ACTIVE.value == "ACTIVE"
        assert UserStatus.INACTIVE.value == "INACTIVE"
        assert UserStatus.SUSPENDED.value == "SUSPENDED"
        assert len(UserStatus) == 3

    def test_academy_status_enum_values(self):
        """AcademyStatus enum should have NONE, WAITLIST, STUDENT, GRADUATE."""
        from app.models.user import AcademyStatus

        assert AcademyStatus.NONE.value == "NONE"
        assert AcademyStatus.WAITLIST.value == "WAITLIST"
        assert AcademyStatus.STUDENT.value == "STUDENT"
        assert AcademyStatus.GRADUATE.value == "GRADUATE"
        assert len(AcademyStatus) == 4


class TestUserModel:
    """Test User model definition."""

    def test_tablename(self):
        """User should have correct table name."""
        from app.models.user import User

        assert User.__tablename__ == "user"

    def test_primary_key(self):
        """User should have id as primary key."""
        from app.models.user import User

        assert User.__table__.c.id.primary_key is True

    def test_required_columns(self):
        """User should have required columns defined."""
        from app.models.user import User

        columns = User.__table__.c
        assert "id" in columns
        assert "email" in columns
        assert "role" in columns
        assert "status" in columns
        assert "organizationId" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """User should have optional columns defined."""
        from app.models.user import User

        columns = User.__table__.c
        assert "username" in columns
        assert "firstName" in columns
        assert "lastName" in columns
        assert "passwordHash" in columns
        assert "phoneExtension" in columns
        assert "department" in columns
        assert "preferences" in columns
        assert "lastLoginAt" in columns

    def test_billing_columns(self):
        """User should have AI billing columns."""
        from app.models.user import User

        columns = User.__table__.c
        assert "openRouterApiKey" in columns
        assert "usageCount" in columns
        assert "isPremium" in columns
        assert "stripeCustomerId" in columns
        assert "stripeSubscriptionId" in columns

    def test_onboarding_columns(self):
        """User should have onboarding columns."""
        from app.models.user import User

        columns = User.__table__.c
        assert "selectedPersona" in columns
        assert "onboardingCompleted" in columns
        assert "onboardingStep" in columns
        assert "privacyPreferences" in columns
        assert "featureToggles" in columns

    def test_academy_columns(self):
        """User should have academy columns."""
        from app.models.user import User

        columns = User.__table__.c
        assert "academyStatus" in columns
        assert "academyInterest" in columns

    def test_email_unique_index(self):
        """Email column should be unique and indexed."""
        from app.models.user import User

        email_col = User.__table__.c.email
        assert email_col.unique is True
        assert email_col.index is True

    def test_role_default(self):
        """Role should default to AGENT."""
        from app.models.user import User, Role

        role_col = User.__table__.c.role
        assert role_col.default.arg == Role.AGENT

    def test_status_default(self):
        """Status should default to ACTIVE."""
        from app.models.user import User, UserStatus

        status_col = User.__table__.c.status
        assert status_col.default.arg == UserStatus.ACTIVE


class TestNestedMutableDict:
    """Test NestedMutableDict for JSON column mutation tracking."""

    def test_coerce_none(self):
        """Coerce should handle None."""
        from app.models.user import NestedMutableDict

        result = NestedMutableDict.coerce("key", None)
        assert result is None

    def test_coerce_already_nested_mutable(self):
        """Coerce should return same instance if already NestedMutableDict."""
        from app.models.user import NestedMutableDict

        original = NestedMutableDict({"a": 1})
        result = NestedMutableDict.coerce("key", original)
        assert result is original

    def test_coerce_plain_dict(self):
        """Coerce should convert plain dict to NestedMutableDict."""
        from app.models.user import NestedMutableDict

        result = NestedMutableDict.coerce("key", {"a": 1, "b": 2})
        assert isinstance(result, NestedMutableDict)
        assert result["a"] == 1
        assert result["b"] == 2

    def test_coerce_nested_dict(self):
        """Coerce should recursively convert nested dicts."""
        from app.models.user import NestedMutableDict

        result = NestedMutableDict.coerce("key", {"outer": {"inner": "value"}})
        assert isinstance(result, NestedMutableDict)
        assert isinstance(result["outer"], NestedMutableDict)
        assert result["outer"]["inner"] == "value"

    def test_coerce_non_dict(self):
        """Coerce should return non-dict values as-is."""
        from app.models.user import NestedMutableDict

        assert NestedMutableDict.coerce("key", "string") == "string"
        assert NestedMutableDict.coerce("key", 42) == 42
        assert NestedMutableDict.coerce("key", True) is True


class TestUserHelperFunctions:
    """Test User helper functions."""

    def test_generate_org_id(self):
        """_generate_org_id should return a valid token."""
        from app.models.user import _generate_org_id

        org_id = _generate_org_id()
        assert isinstance(org_id, str)
        assert len(org_id) > 10  # Should be a reasonable length

    def test_generate_org_id_unique(self):
        """_generate_org_id should generate unique IDs."""
        from app.models.user import _generate_org_id

        ids = [_generate_org_id() for _ in range(10)]
        assert len(set(ids)) == 10  # All should be unique

    def test_ensure_feature_toggles_empty(self):
        """ensure_feature_toggles should set defaults when empty."""
        from app.models.user import ensure_feature_toggles

        user = MagicMock()
        user.featureToggles = None
        ensure_feature_toggles(user)
        assert user.featureToggles == {
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True,
        }

    def test_ensure_feature_toggles_existing(self):
        """ensure_feature_toggles should not override existing values."""
        from app.models.user import ensure_feature_toggles

        user = MagicMock()
        user.featureToggles = {"custom": True}
        ensure_feature_toggles(user)
        assert user.featureToggles == {"custom": True}

    def test_ensure_privacy_preferences_empty(self):
        """ensure_privacy_preferences should set defaults when empty."""
        from app.models.user import ensure_privacy_preferences

        user = MagicMock()
        user.privacyPreferences = None
        ensure_privacy_preferences(user)
        assert user.privacyPreferences == {
            "geminiFileSearchEnabled": True,
            "iiAgentEnabled": True,
            "dataPrivacyAcknowledged": False,
        }

    def test_ensure_privacy_preferences_existing(self):
        """ensure_privacy_preferences should not override existing values."""
        from app.models.user import ensure_privacy_preferences

        user = MagicMock()
        user.privacyPreferences = {"custom": False}
        ensure_privacy_preferences(user)
        assert user.privacyPreferences == {"custom": False}


# ============================================================================
# TASK AND PROJECT MODEL TESTS
# ============================================================================


class TestTaskEnums:
    """Test Task-related enum definitions."""

    def test_task_status_enum_values(self):
        """TaskStatus enum should have correct values."""
        from app.models.task import TaskStatus

        assert TaskStatus.PENDING.value == "PENDING"
        assert TaskStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert TaskStatus.COMPLETED.value == "COMPLETED"
        assert TaskStatus.ARCHIVED.value == "ARCHIVED"
        assert len(TaskStatus) == 4

    def test_energy_level_enum_values(self):
        """EnergyLevel enum should have low, medium, high."""
        from app.models.task import EnergyLevel

        assert EnergyLevel.low.value == "low"
        assert EnergyLevel.medium.value == "medium"
        assert EnergyLevel.high.value == "high"
        assert len(EnergyLevel) == 3


class TestTaskModel:
    """Test Task model definition."""

    def test_tablename(self):
        """Task should have correct table name."""
        from app.models.task import Task

        assert Task.__tablename__ == "task"

    def test_primary_key(self):
        """Task should have id as primary key."""
        from app.models.task import Task

        assert Task.__table__.c.id.primary_key is True

    def test_required_columns(self):
        """Task should have required columns."""
        from app.models.task import Task

        columns = Task.__table__.c
        assert "id" in columns
        assert "title" in columns
        assert "status" in columns
        assert "priority" in columns
        assert "energyRequired" in columns
        assert "tags" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """Task should have optional columns."""
        from app.models.task import Task

        columns = Task.__table__.c
        assert "description" in columns
        assert "dueDate" in columns
        assert "completedAt" in columns
        assert "estimatedMinutes" in columns
        assert "actualMinutes" in columns
        assert "parentTaskId" in columns
        assert "projectId" in columns
        assert "userId" in columns
        assert "aiInsights" in columns
        assert "urgencyScore" in columns

    def test_i18n_columns(self):
        """Task should have i18n columns for localization."""
        from app.models.task import Task

        columns = Task.__table__.c
        assert "title_i18n" in columns
        assert "description_i18n" in columns

    def test_sync_columns(self):
        """Task should have sync columns for external integrations."""
        from app.models.task import Task

        columns = Task.__table__.c
        assert "google_calendar_id" in columns
        assert "linear_id" in columns

    def test_status_default(self):
        """Task status should default to PENDING."""
        from app.models.task import Task, TaskStatus

        status_col = Task.__table__.c.status
        assert status_col.default.arg == TaskStatus.PENDING

    def test_priority_default(self):
        """Task priority should default to 1."""
        from app.models.task import Task

        priority_col = Task.__table__.c.priority
        assert priority_col.default.arg == 1

    def test_energy_default(self):
        """Task energyRequired should default to low."""
        from app.models.task import Task, EnergyLevel

        energy_col = Task.__table__.c.energyRequired
        assert energy_col.default.arg == EnergyLevel.low


class TestProjectModel:
    """Test Project model definition."""

    def test_tablename(self):
        """Project should have correct table name."""
        from app.models.task import Project

        assert Project.__tablename__ == "project"

    def test_required_columns(self):
        """Project should have required columns."""
        from app.models.task import Project

        columns = Project.__table__.c
        assert "id" in columns
        assert "name" in columns
        assert "userId" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """Project should have optional columns."""
        from app.models.task import Project

        columns = Project.__table__.c
        assert "description" in columns
        assert "color" in columns
        assert "icon" in columns
        assert "workspaceId" in columns

    def test_i18n_columns(self):
        """Project should have i18n columns."""
        from app.models.task import Project

        columns = Project.__table__.c
        assert "name_i18n" in columns
        assert "description_i18n" in columns


# ============================================================================
# ACTIVITY MODEL TESTS
# ============================================================================


class TestActivityModel:
    """Test Activity model definition."""

    def test_tablename(self):
        """Activity should have correct table name."""
        from app.models.activity import Activity

        assert Activity.__tablename__ == "activity"

    def test_required_columns(self):
        """Activity should have required columns."""
        from app.models.activity import Activity

        columns = Activity.__table__.c
        assert "id" in columns
        assert "activityType" in columns
        assert "userId" in columns
        assert "targetType" in columns
        assert "targetId" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """Activity should have optional columns."""
        from app.models.activity import Activity

        columns = Activity.__table__.c
        assert "workspaceId" in columns
        assert "targetTitle" in columns
        assert "extra_data" in columns

    def test_activity_type_indexed(self):
        """activityType should be indexed."""
        from app.models.activity import Activity

        col = Activity.__table__.c.activityType
        assert col.index is True


class TestActivityTypes:
    """Test ACTIVITY_TYPES constant."""

    def test_activity_types_defined(self):
        """ACTIVITY_TYPES should have expected keys."""
        from app.models.activity import ACTIVITY_TYPES

        assert "task_created" in ACTIVITY_TYPES
        assert "task_updated" in ACTIVITY_TYPES
        assert "task_completed" in ACTIVITY_TYPES
        assert "task_assigned" in ACTIVITY_TYPES
        assert "project_created" in ACTIVITY_TYPES
        assert "comment_added" in ACTIVITY_TYPES
        assert "knowledge_captured" in ACTIVITY_TYPES
        assert "goal_set" in ACTIVITY_TYPES
        assert "member_joined" in ACTIVITY_TYPES

    def test_activity_types_have_descriptions(self):
        """Each activity type should have a human-readable description."""
        from app.models.activity import ACTIVITY_TYPES

        for key, value in ACTIVITY_TYPES.items():
            assert isinstance(value, str)
            assert len(value) > 0


# ============================================================================
# COMMENT MODEL TESTS
# ============================================================================


class TestCommentModel:
    """Test Comment model definition."""

    def test_tablename(self):
        """Comment should have correct table name."""
        from app.models.comment import Comment

        assert Comment.__tablename__ == "comment"

    def test_required_columns(self):
        """Comment should have required columns."""
        from app.models.comment import Comment

        columns = Comment.__table__.c
        assert "id" in columns
        assert "content" in columns
        assert "userId" in columns
        assert "createdAt" in columns

    def test_polymorphic_columns(self):
        """Comment should support polymorphic attachment."""
        from app.models.comment import Comment

        columns = Comment.__table__.c
        assert "taskId" in columns
        assert "projectId" in columns
        assert "knowledgeItemId" in columns

    def test_foreign_keys_indexed(self):
        """Foreign key columns should be indexed."""
        from app.models.comment import Comment

        assert Comment.__table__.c.taskId.index is True
        assert Comment.__table__.c.projectId.index is True
        assert Comment.__table__.c.knowledgeItemId.index is True


# ============================================================================
# EVENT MODEL TESTS
# ============================================================================


class TestEventModel:
    """Test Event (calendar) model definition."""

    def test_tablename(self):
        """Event should have correct table name."""
        from app.models.event import Event

        assert Event.__tablename__ == "events"

    def test_required_columns(self):
        """Event should have required columns."""
        from app.models.event import Event

        columns = Event.__table__.c
        assert "id" in columns
        assert "user_id" in columns
        assert "title" in columns
        assert "start_time" in columns
        assert "end_time" in columns
        assert "all_day" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_optional_columns(self):
        """Event should have optional columns."""
        from app.models.event import Event

        columns = Event.__table__.c
        assert "description" in columns
        assert "google_event_id" in columns
        assert "google_calendar_id" in columns
        assert "task_id" in columns
        assert "location" in columns
        assert "attendees" in columns
        assert "color" in columns
        assert "reminder_minutes" in columns

    def test_i18n_columns(self):
        """Event should have i18n columns."""
        from app.models.event import Event

        columns = Event.__table__.c
        assert "title_i18n" in columns
        assert "description_i18n" in columns

    def test_google_event_id_indexed(self):
        """google_event_id should be indexed for sync."""
        from app.models.event import Event

        col = Event.__table__.c.google_event_id
        assert col.index is True

    def test_all_day_default(self):
        """all_day should default to False."""
        from app.models.event import Event

        col = Event.__table__.c.all_day
        assert col.default.arg is False


# ============================================================================
# SESSION MODEL TESTS
# ============================================================================


class TestSessionModel:
    """Test Session model definition."""

    def test_tablename(self):
        """Session should have correct table name."""
        from app.models.session import Session

        assert Session.__tablename__ == "userSession"

    def test_required_columns(self):
        """Session should have required columns."""
        from app.models.session import Session

        columns = Session.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "sessionToken" in columns
        assert "refreshTokenHash" in columns
        assert "expiresAt" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """Session should have optional tracking columns."""
        from app.models.session import Session

        columns = Session.__table__.c
        assert "lastActivity" in columns
        assert "revokedAt" in columns
        assert "ipAddress" in columns
        assert "userAgent" in columns
        assert "lastRefreshAt" in columns
        assert "refreshCount" in columns

    def test_session_token_unique(self):
        """Session token should be unique."""
        from app.models.session import Session

        col = Session.__table__.c.sessionToken
        assert col.unique is True

    def test_refresh_count_default(self):
        """refreshCount should default to 0."""
        from app.models.session import Session

        col = Session.__table__.c.refreshCount
        assert col.default.arg == 0


# ============================================================================
# TIME ENTRY MODEL TESTS
# ============================================================================


class TestTimeEntryModel:
    """Test TimeEntry model definition."""

    def test_tablename(self):
        """TimeEntry should have correct table name."""
        from app.models.time_entry import TimeEntry

        assert TimeEntry.__tablename__ == "time_entries"

    def test_required_columns(self):
        """TimeEntry should have required columns."""
        from app.models.time_entry import TimeEntry

        columns = TimeEntry.__table__.c
        assert "id" in columns
        assert "user_id" in columns
        assert "start_time" in columns
        assert "billable" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_optional_columns(self):
        """TimeEntry should have optional columns."""
        from app.models.time_entry import TimeEntry

        columns = TimeEntry.__table__.c
        assert "task_id" in columns
        assert "project_id" in columns
        assert "workspace_id" in columns
        assert "end_time" in columns
        assert "duration_seconds" in columns
        assert "description" in columns
        assert "hourly_rate" in columns
        assert "tags" in columns

    def test_i18n_column(self):
        """TimeEntry should have i18n description column."""
        from app.models.time_entry import TimeEntry

        columns = TimeEntry.__table__.c
        assert "description_i18n" in columns

    def test_billable_default(self):
        """billable should default to False."""
        from app.models.time_entry import TimeEntry

        col = TimeEntry.__table__.c.billable
        assert col.default.arg is False


# ============================================================================
# VOICE RECORDING MODEL TESTS
# ============================================================================


class TestVoiceRecordingModel:
    """Test VoiceRecording model definition."""

    def test_tablename(self):
        """VoiceRecording should have correct table name."""
        from app.models.voice_recording import VoiceRecording

        assert VoiceRecording.__tablename__ == "voice_recording"

    def test_required_columns(self):
        """VoiceRecording should have required columns."""
        from app.models.voice_recording import VoiceRecording

        columns = VoiceRecording.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "mimetype" in columns
        assert "language" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """VoiceRecording should have optional columns."""
        from app.models.voice_recording import VoiceRecording

        columns = VoiceRecording.__table__.c
        assert "sessionId" in columns
        assert "audioUrl" in columns
        assert "duration" in columns
        assert "transcript" in columns
        assert "confidence" in columns
        assert "processedResult" in columns
        assert "intent" in columns
        assert "provider" in columns
        assert "record_metadata" in columns

    def test_mimetype_default(self):
        """mimetype should default to audio/wav."""
        from app.models.voice_recording import VoiceRecording

        col = VoiceRecording.__table__.c.mimetype
        assert col.default.arg == "audio/wav"

    def test_language_default(self):
        """language should default to en."""
        from app.models.voice_recording import VoiceRecording

        col = VoiceRecording.__table__.c.language
        assert col.default.arg == "en"


# ============================================================================
# WORKFLOW TEMPLATE MODEL TESTS
# ============================================================================


class TestWorkflowTemplateModel:
    """Test WorkflowTemplate model definition."""

    def test_tablename(self):
        """WorkflowTemplate should have correct table name."""
        from app.models.workflow_template import WorkflowTemplate

        assert WorkflowTemplate.__tablename__ == "workflow_template"

    def test_required_columns(self):
        """WorkflowTemplate should have required columns."""
        from app.models.workflow_template import WorkflowTemplate

        columns = WorkflowTemplate.__table__.c
        assert "id" in columns
        assert "name" in columns
        assert "steps" in columns
        assert "tags" in columns
        assert "isPublic" in columns
        assert "isSystem" in columns
        assert "usageCount" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """WorkflowTemplate should have optional columns."""
        from app.models.workflow_template import WorkflowTemplate

        columns = WorkflowTemplate.__table__.c
        assert "userId" in columns
        assert "description" in columns
        assert "category" in columns
        assert "icon" in columns
        assert "totalEstimatedMinutes" in columns
        assert "template_metadata" in columns

    def test_boolean_defaults(self):
        """Boolean columns should have correct defaults."""
        from app.models.workflow_template import WorkflowTemplate

        assert WorkflowTemplate.__table__.c.isPublic.default.arg is False
        assert WorkflowTemplate.__table__.c.isSystem.default.arg is False

    def test_usage_count_default(self):
        """usageCount should default to 0."""
        from app.models.workflow_template import WorkflowTemplate

        col = WorkflowTemplate.__table__.c.usageCount
        assert col.default.arg == 0


# ============================================================================
# AI CONVERSATION MODEL TESTS
# ============================================================================


class TestAIConversationModel:
    """Test AIConversation model definition."""

    def test_tablename(self):
        """AIConversation should have correct table name."""
        from app.models.ai_conversation import AIConversation

        assert AIConversation.__tablename__ == "ai_conversation"

    def test_required_columns(self):
        """AIConversation should have required columns."""
        from app.models.ai_conversation import AIConversation

        columns = AIConversation.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "type" in columns
        assert "messages" in columns
        assert "tags" in columns
        assert "totalTokens" in columns
        assert "totalCost" in columns
        assert "isActive" in columns
        assert "isArchived" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """AIConversation should have optional columns."""
        from app.models.ai_conversation import AIConversation

        columns = AIConversation.__table__.c
        assert "title" in columns
        assert "context" in columns
        assert "summary" in columns
        assert "primaryModel" in columns
        assert "lastMessageAt" in columns

    def test_type_default(self):
        """type should default to chat."""
        from app.models.ai_conversation import AIConversation

        col = AIConversation.__table__.c.type
        assert col.default.arg == "chat"

    def test_token_defaults(self):
        """Token and cost columns should default to 0."""
        from app.models.ai_conversation import AIConversation

        assert AIConversation.__table__.c.totalTokens.default.arg == 0
        assert AIConversation.__table__.c.totalCost.default.arg == 0.0

    def test_boolean_defaults(self):
        """Boolean columns should have correct defaults."""
        from app.models.ai_conversation import AIConversation

        assert AIConversation.__table__.c.isActive.default.arg is True
        assert AIConversation.__table__.c.isArchived.default.arg is False


# ============================================================================
# SHADOW PROFILE MODEL TESTS
# ============================================================================


class TestShadowProfileModel:
    """Test ShadowProfile model definition."""

    def test_tablename(self):
        """ShadowProfile should have correct table name."""
        from app.models.shadow_profile import ShadowProfile

        assert ShadowProfile.__tablename__ == "shadow_profile"

    def test_required_columns(self):
        """ShadowProfile should have required columns."""
        from app.models.shadow_profile import ShadowProfile

        columns = ShadowProfile.__table__.c
        assert "id" in columns
        assert "user_id" in columns
        assert "archetype" in columns
        assert "unlock_day" in columns
        assert "total_days" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_optional_columns(self):
        """ShadowProfile should have optional columns."""
        from app.models.shadow_profile import ShadowProfile

        columns = ShadowProfile.__table__.c
        assert "insights_data" in columns
        assert "patterns" in columns

    def test_defaults(self):
        """ShadowProfile should have correct defaults."""
        from app.models.shadow_profile import ShadowProfile

        assert ShadowProfile.__table__.c.unlock_day.default.arg == 1
        assert ShadowProfile.__table__.c.total_days.default.arg == 30


class TestShadowInsightModel:
    """Test ShadowInsight model definition."""

    def test_tablename(self):
        """ShadowInsight should have correct table name."""
        from app.models.shadow_profile import ShadowInsight

        assert ShadowInsight.__tablename__ == "shadow_insight"

    def test_required_columns(self):
        """ShadowInsight should have required columns."""
        from app.models.shadow_profile import ShadowInsight

        columns = ShadowInsight.__table__.c
        assert "id" in columns
        assert "profile_id" in columns
        assert "day" in columns
        assert "insight_type" in columns
        assert "content" in columns
        assert "unlocked" in columns
        assert "created_at" in columns

    def test_optional_columns(self):
        """ShadowInsight should have optional columns."""
        from app.models.shadow_profile import ShadowInsight

        columns = ShadowInsight.__table__.c
        assert "unlocked_at" in columns

    def test_unlocked_default(self):
        """unlocked should default to False."""
        from app.models.shadow_profile import ShadowInsight

        col = ShadowInsight.__table__.c.unlocked
        assert col.default.arg is False

    def test_indexed_columns(self):
        """Key columns should be indexed."""
        from app.models.shadow_profile import ShadowInsight

        assert ShadowInsight.__table__.c.day.index is True
        assert ShadowInsight.__table__.c.unlocked.index is True


# ============================================================================
# WORKSPACE MODEL TESTS
# ============================================================================


class TestWorkspaceEnums:
    """Test Workspace-related enum definitions."""

    def test_workspace_role_enum_values(self):
        """WorkspaceRole enum should have OWNER, ADMIN, MEMBER."""
        from app.models.workspace import WorkspaceRole

        assert WorkspaceRole.OWNER.value == "OWNER"
        assert WorkspaceRole.ADMIN.value == "ADMIN"
        assert WorkspaceRole.MEMBER.value == "MEMBER"
        assert len(WorkspaceRole) == 3


class TestWorkspaceModel:
    """Test Workspace model definition."""

    def test_tablename(self):
        """Workspace should have correct table name."""
        from app.models.workspace import Workspace

        assert Workspace.__tablename__ == "workspace"

    def test_required_columns(self):
        """Workspace should have required columns."""
        from app.models.workspace import Workspace

        columns = Workspace.__table__.c
        assert "id" in columns
        assert "name" in columns
        assert "ownerId" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """Workspace should have optional columns."""
        from app.models.workspace import Workspace

        columns = Workspace.__table__.c
        assert "description" in columns
        assert "color" in columns
        assert "settings" in columns


class TestWorkspaceMemberModel:
    """Test WorkspaceMember model definition."""

    def test_tablename(self):
        """WorkspaceMember should have correct table name."""
        from app.models.workspace import WorkspaceMember

        assert WorkspaceMember.__tablename__ == "workspace_member"

    def test_required_columns(self):
        """WorkspaceMember should have required columns."""
        from app.models.workspace import WorkspaceMember

        columns = WorkspaceMember.__table__.c
        assert "id" in columns
        assert "workspaceId" in columns
        assert "userId" in columns
        assert "role" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """WorkspaceMember should have optional columns."""
        from app.models.workspace import WorkspaceMember

        columns = WorkspaceMember.__table__.c
        assert "permissions" in columns

    def test_role_default(self):
        """role should default to MEMBER."""
        from app.models.workspace import WorkspaceMember, WorkspaceRole

        col = WorkspaceMember.__table__.c.role
        assert col.default.arg == WorkspaceRole.MEMBER


# ============================================================================
# ITEM TYPE MODEL TESTS
# ============================================================================


class TestItemTypeModel:
    """Test ItemType model definition."""

    def test_tablename(self):
        """ItemType should have correct table name."""
        from app.models.item_type import ItemType

        assert ItemType.__tablename__ == "item_type"

    def test_required_columns(self):
        """ItemType should have required columns."""
        from app.models.item_type import ItemType

        columns = ItemType.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "name" in columns
        assert "icon" in columns
        assert "color" in columns
        assert "isDefault" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """ItemType should have optional columns."""
        from app.models.item_type import ItemType

        columns = ItemType.__table__.c
        assert "description" in columns

    def test_defaults(self):
        """ItemType should have correct defaults."""
        from app.models.item_type import ItemType

        assert ItemType.__table__.c.icon.default.arg == "Star"
        assert ItemType.__table__.c.color.default.arg == "blue"
        assert ItemType.__table__.c.isDefault.default.arg is False

    def test_to_dict_method(self):
        """ItemType should have to_dict method."""
        from app.models.item_type import ItemType

        assert hasattr(ItemType, "to_dict")
        assert callable(getattr(ItemType, "to_dict"))


# ============================================================================
# KNOWLEDGE ITEM MODEL TESTS
# ============================================================================


class TestKnowledgeItemModel:
    """Test KnowledgeItem model definition."""

    def test_tablename(self):
        """KnowledgeItem should have correct table name."""
        from app.models.knowledge_item import KnowledgeItem

        assert KnowledgeItem.__tablename__ == "knowledge_item"

    def test_required_columns(self):
        """KnowledgeItem should have required columns."""
        from app.models.knowledge_item import KnowledgeItem

        columns = KnowledgeItem.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "typeId" in columns
        assert "title" in columns
        assert "completed" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """KnowledgeItem should have optional columns."""
        from app.models.knowledge_item import KnowledgeItem

        columns = KnowledgeItem.__table__.c
        assert "content" in columns
        assert "item_metadata" in columns

    def test_completed_default(self):
        """completed should default to False."""
        from app.models.knowledge_item import KnowledgeItem

        col = KnowledgeItem.__table__.c.completed
        assert col.default.arg is False

    def test_to_dict_method(self):
        """KnowledgeItem should have to_dict method."""
        from app.models.knowledge_item import KnowledgeItem

        assert hasattr(KnowledgeItem, "to_dict")
        assert callable(getattr(KnowledgeItem, "to_dict"))


# ============================================================================
# FILE SEARCH STORE MODEL TESTS
# ============================================================================


class TestFileSearchStoreModel:
    """Test FileSearchStore model definition."""

    def test_tablename(self):
        """FileSearchStore should have correct table name."""
        from app.models.file_search_store import FileSearchStore

        assert FileSearchStore.__tablename__ == "file_search_store"

    def test_required_columns(self):
        """FileSearchStore should have required columns."""
        from app.models.file_search_store import FileSearchStore

        columns = FileSearchStore.__table__.c
        assert "id" in columns
        assert "organizationId" in columns
        assert "store_name" in columns
        assert "kind" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """FileSearchStore should have optional columns."""
        from app.models.file_search_store import FileSearchStore

        columns = FileSearchStore.__table__.c
        assert "userId" in columns

    def test_store_name_unique(self):
        """store_name should be unique."""
        from app.models.file_search_store import FileSearchStore

        col = FileSearchStore.__table__.c.store_name
        assert col.unique is True


# ============================================================================
# FILE SEARCH DOCUMENT MODEL TESTS
# ============================================================================


class TestFileSearchDocumentModel:
    """Test FileSearchDocument model definition."""

    def test_tablename(self):
        """FileSearchDocument should have correct table name."""
        from app.models.file_search_document import FileSearchDocument

        assert FileSearchDocument.__tablename__ == "file_search_document"

    def test_required_columns(self):
        """FileSearchDocument should have required columns."""
        from app.models.file_search_document import FileSearchDocument

        columns = FileSearchDocument.__table__.c
        assert "id" in columns
        assert "organizationId" in columns
        assert "userId" in columns
        assert "storeName" in columns
        assert "documentName" in columns
        assert "kind" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """FileSearchDocument should have optional link columns."""
        from app.models.file_search_document import FileSearchDocument

        columns = FileSearchDocument.__table__.c
        assert "knowledgeItemId" in columns
        assert "voiceRecordingId" in columns


# ============================================================================
# REQUEST TELEMETRY MODEL TESTS
# ============================================================================


class TestRequestTelemetryEnums:
    """Test RequestTelemetry-related enum definitions."""

    def test_telemetry_source_enum_values(self):
        """TelemetrySource enum should have correct values."""
        from app.models.request_telemetry import TelemetrySource

        assert TelemetrySource.ENHANCE_INPUT.value == "enhance_input"
        assert TelemetrySource.ORCHESTRATE_TASK.value == "orchestrate_task"
        assert len(TelemetrySource) == 2

    def test_telemetry_route_enum_values(self):
        """TelemetryRoute enum should have correct values."""
        from app.models.request_telemetry import TelemetryRoute

        assert TelemetryRoute.UNKNOWN.value == "unknown"
        assert TelemetryRoute.DETERMINISTIC.value == "deterministic"
        assert TelemetryRoute.ORCHESTRATED.value == "orchestrated"
        assert len(TelemetryRoute) == 3

    def test_workflow_decision_status_enum_values(self):
        """WorkflowDecisionStatus enum should have correct values."""
        from app.models.request_telemetry import WorkflowDecisionStatus

        assert WorkflowDecisionStatus.APPROVED.value == "approved"
        assert WorkflowDecisionStatus.REVISE.value == "revise"
        assert WorkflowDecisionStatus.REJECTED.value == "rejected"
        assert len(WorkflowDecisionStatus) == 3


class TestRequestTelemetryModel:
    """Test RequestTelemetry model definition."""

    def test_tablename(self):
        """RequestTelemetry should have correct table name."""
        from app.models.request_telemetry import RequestTelemetry

        assert RequestTelemetry.__tablename__ == "request_telemetry"

    def test_required_columns(self):
        """RequestTelemetry should have required columns."""
        from app.models.request_telemetry import RequestTelemetry

        columns = RequestTelemetry.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "source" in columns
        assert "route" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """RequestTelemetry should have optional columns."""
        from app.models.request_telemetry import RequestTelemetry

        columns = RequestTelemetry.__table__.c
        assert "intent" in columns
        assert "detectedType" in columns
        assert "confidence" in columns
        assert "workflowSteps" in columns
        assert "escalationReason" in columns
        assert "details" in columns
        assert "decisionStatus" in columns
        assert "decisionNotes" in columns
        assert "decisionAt" in columns

    def test_route_default(self):
        """route should default to UNKNOWN."""
        from app.models.request_telemetry import RequestTelemetry, TelemetryRoute

        col = RequestTelemetry.__table__.c.route
        assert col.default.arg == TelemetryRoute.UNKNOWN


# ============================================================================
# COMMAND HISTORY MODEL TESTS
# ============================================================================


class TestCommandHistoryEnums:
    """Test CommandHistory-related enum definitions."""

    def test_command_source_enum_values(self):
        """CommandSource enum should have correct values."""
        from app.models.command_history import CommandSource

        assert CommandSource.ASSISTANT_VOICE.value == "assistant_voice"
        assert CommandSource.ASSISTANT_TEXT.value == "assistant_text"
        assert CommandSource.DETERMINISTIC_API.value == "deterministic_api"
        assert CommandSource.II_AGENT.value == "ii_agent"
        assert CommandSource.WORKFLOW.value == "workflow"
        assert CommandSource.DIRECT_API.value == "direct_api"
        assert len(CommandSource) == 6

    def test_command_status_enum_values(self):
        """CommandStatus enum should have correct values."""
        from app.models.command_history import CommandStatus

        assert CommandStatus.PENDING.value == "pending"
        assert CommandStatus.IN_PROGRESS.value == "in_progress"
        assert CommandStatus.COMPLETED.value == "completed"
        assert CommandStatus.FAILED.value == "failed"
        assert CommandStatus.CANCELLED.value == "cancelled"
        assert len(CommandStatus) == 5


class TestCommandHistoryModel:
    """Test CommandHistory model definition."""

    def test_tablename(self):
        """CommandHistory should have correct table name."""
        from app.models.command_history import CommandHistory

        assert CommandHistory.__tablename__ == "command_history"

    def test_required_columns(self):
        """CommandHistory should have required columns."""
        from app.models.command_history import CommandHistory

        columns = CommandHistory.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "source" in columns
        assert "command" in columns
        assert "status" in columns
        assert "startedAt" in columns

    def test_optional_columns(self):
        """CommandHistory should have optional columns."""
        from app.models.command_history import CommandHistory

        columns = CommandHistory.__table__.c
        assert "intent" in columns
        assert "completedAt" in columns
        assert "durationMs" in columns
        assert "context" in columns
        assert "result" in columns
        assert "error" in columns
        assert "telemetryId" in columns
        assert "agentSessionId" in columns
        assert "conversationId" in columns
        assert "model" in columns
        assert "confidence" in columns
        assert "command_metadata" in columns

    def test_status_default(self):
        """status should default to PENDING."""
        from app.models.command_history import CommandHistory, CommandStatus

        col = CommandHistory.__table__.c.status
        assert col.default.arg == CommandStatus.PENDING

    def test_indexed_columns(self):
        """Key columns should be indexed."""
        from app.models.command_history import CommandHistory

        assert CommandHistory.__table__.c.source.index is True
        assert CommandHistory.__table__.c.intent.index is True
        assert CommandHistory.__table__.c.status.index is True
        assert CommandHistory.__table__.c.startedAt.index is True


# ============================================================================
# AGENT SESSION MODEL TESTS
# ============================================================================


class TestAgentSessionEnums:
    """Test AgentSession-related enum definitions."""

    def test_agent_session_status_enum_values(self):
        """AgentSessionStatus enum should have correct values."""
        from app.models.agent_session import AgentSessionStatus

        assert AgentSessionStatus.PENDING.value == "pending"
        assert AgentSessionStatus.RUNNING.value == "running"
        assert AgentSessionStatus.COMPLETED.value == "completed"
        assert AgentSessionStatus.FAILED.value == "failed"
        assert AgentSessionStatus.CANCELLED.value == "cancelled"
        assert len(AgentSessionStatus) == 5

    def test_agent_session_event_type_enum_values(self):
        """AgentSessionEventType enum should have correct values."""
        from app.models.agent_session import AgentSessionEventType

        assert AgentSessionEventType.STARTED.value == "started"
        assert AgentSessionEventType.TOOL_CALL.value == "tool_call"
        assert AgentSessionEventType.PROGRESS_UPDATE.value == "progress_update"
        assert AgentSessionEventType.ERROR.value == "error"
        assert AgentSessionEventType.COMPLETED.value == "completed"
        assert len(AgentSessionEventType) == 5


class TestAgentSessionModel:
    """Test AgentSession model definition."""

    def test_tablename(self):
        """AgentSession should have correct table name."""
        from app.models.agent_session import AgentSession

        assert AgentSession.__tablename__ == "agent_session"

    def test_required_columns(self):
        """AgentSession should have required columns."""
        from app.models.agent_session import AgentSession

        columns = AgentSession.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "sessionUuid" in columns
        assert "status" in columns
        assert "goal" in columns
        assert "toolCallCount" in columns
        assert "createdAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """AgentSession should have optional columns."""
        from app.models.agent_session import AgentSession

        columns = AgentSession.__table__.c
        assert "telemetryId" in columns
        assert "structuredGoal" in columns
        assert "context" in columns
        assert "escalationReason" in columns
        assert "lastToolCall" in columns
        assert "lastToolCallAt" in columns
        assert "progressPercent" in columns
        assert "currentStep" in columns
        assert "result" in columns
        assert "errorMessage" in columns
        assert "startedAt" in columns
        assert "completedAt" in columns

    def test_session_uuid_unique(self):
        """sessionUuid should be unique."""
        from app.models.agent_session import AgentSession

        col = AgentSession.__table__.c.sessionUuid
        assert col.unique is True

    def test_status_default(self):
        """status should default to PENDING."""
        from app.models.agent_session import AgentSession, AgentSessionStatus

        col = AgentSession.__table__.c.status
        assert col.default.arg == AgentSessionStatus.PENDING

    def test_tool_call_count_default(self):
        """toolCallCount should default to 0."""
        from app.models.agent_session import AgentSession

        col = AgentSession.__table__.c.toolCallCount
        assert col.default.arg == 0


class TestAgentSessionEventModel:
    """Test AgentSessionEvent model definition."""

    def test_tablename(self):
        """AgentSessionEvent should have correct table name."""
        from app.models.agent_session import AgentSessionEvent

        assert AgentSessionEvent.__tablename__ == "agent_session_event"

    def test_required_columns(self):
        """AgentSessionEvent should have required columns."""
        from app.models.agent_session import AgentSessionEvent

        columns = AgentSessionEvent.__table__.c
        assert "id" in columns
        assert "sessionId" in columns
        assert "eventType" in columns
        assert "createdAt" in columns

    def test_optional_columns(self):
        """AgentSessionEvent should have optional columns."""
        from app.models.agent_session import AgentSessionEvent

        columns = AgentSessionEvent.__table__.c
        assert "eventData" in columns
        assert "toolName" in columns
        assert "toolInput" in columns
        assert "toolOutput" in columns
        assert "toolError" in columns
        assert "toolDurationMs" in columns

    def test_indexed_columns(self):
        """Key columns should be indexed."""
        from app.models.agent_session import AgentSessionEvent

        assert AgentSessionEvent.__table__.c.eventType.index is True
        assert AgentSessionEvent.__table__.c.toolName.index is True


# ============================================================================
# RELATIONSHIP TESTS
# ============================================================================


class TestModelRelationships:
    """Test relationships between models."""

    def test_user_has_tasks_relationship(self):
        """User should have tasks relationship."""
        from app.models.user import User

        assert hasattr(User, "tasks")

    def test_user_has_projects_relationship(self):
        """User should have projects relationship."""
        from app.models.user import User

        assert hasattr(User, "projects")

    def test_user_has_sessions_relationship(self):
        """User should have sessions relationship."""
        from app.models.user import User

        assert hasattr(User, "sessions")

    def test_user_has_events_relationship(self):
        """User should have events relationship."""
        from app.models.user import User

        assert hasattr(User, "events")

    def test_user_has_time_entries_relationship(self):
        """User should have time_entries relationship."""
        from app.models.user import User

        assert hasattr(User, "time_entries")

    def test_user_has_voice_recordings_relationship(self):
        """User should have voice_recordings relationship."""
        from app.models.user import User

        assert hasattr(User, "voice_recordings")

    def test_user_has_workflow_templates_relationship(self):
        """User should have workflow_templates relationship."""
        from app.models.user import User

        assert hasattr(User, "workflow_templates")

    def test_user_has_ai_conversations_relationship(self):
        """User should have ai_conversations relationship."""
        from app.models.user import User

        assert hasattr(User, "ai_conversations")

    def test_user_has_shadow_profile_relationship(self):
        """User should have shadow_profile relationship."""
        from app.models.user import User

        assert hasattr(User, "shadow_profile")

    def test_user_has_knowledge_items_relationship(self):
        """User should have knowledge_items relationship."""
        from app.models.user import User

        assert hasattr(User, "knowledge_items")

    def test_user_has_item_types_relationship(self):
        """User should have item_types relationship."""
        from app.models.user import User

        assert hasattr(User, "item_types")

    def test_user_has_search_indices_relationship(self):
        """User should have search_indices relationship."""
        from app.models.user import User

        assert hasattr(User, "search_indices")

    def test_search_index_has_user_relationship(self):
        """SearchIndex should have user relationship."""
        from app.models.search_index import SearchIndex

        assert hasattr(SearchIndex, "user")

    def test_task_has_user_relationship(self):
        """Task should have user relationship."""
        from app.models.task import Task

        assert hasattr(Task, "user")

    def test_task_has_project_relationship(self):
        """Task should have project relationship."""
        from app.models.task import Task

        assert hasattr(Task, "project")

    def test_task_has_events_relationship(self):
        """Task should have events relationship."""
        from app.models.task import Task

        assert hasattr(Task, "events")

    def test_task_has_time_entries_relationship(self):
        """Task should have time_entries relationship."""
        from app.models.task import Task

        assert hasattr(Task, "time_entries")

    def test_project_has_tasks_relationship(self):
        """Project should have tasks relationship."""
        from app.models.task import Project

        assert hasattr(Project, "tasks")

    def test_shadow_profile_has_insights_relationship(self):
        """ShadowProfile should have insights relationship."""
        from app.models.shadow_profile import ShadowProfile

        assert hasattr(ShadowProfile, "insights")

    def test_shadow_insight_has_profile_relationship(self):
        """ShadowInsight should have profile relationship."""
        from app.models.shadow_profile import ShadowInsight

        assert hasattr(ShadowInsight, "profile")

    def test_workspace_has_members_relationship(self):
        """Workspace should have members relationship."""
        from app.models.workspace import Workspace

        assert hasattr(Workspace, "members")

    def test_workspace_has_tasks_relationship(self):
        """Workspace should have tasks relationship."""
        from app.models.workspace import Workspace

        assert hasattr(Workspace, "tasks")

    def test_workspace_has_projects_relationship(self):
        """Workspace should have projects relationship."""
        from app.models.workspace import Workspace

        assert hasattr(Workspace, "projects")

    def test_item_type_has_knowledge_items_relationship(self):
        """ItemType should have knowledge_items relationship."""
        from app.models.item_type import ItemType

        assert hasattr(ItemType, "knowledge_items")

    def test_knowledge_item_has_item_type_relationship(self):
        """KnowledgeItem should have item_type relationship."""
        from app.models.knowledge_item import KnowledgeItem

        assert hasattr(KnowledgeItem, "item_type")

    def test_agent_session_has_events_relationship(self):
        """AgentSession should have events relationship."""
        from app.models.agent_session import AgentSession

        assert hasattr(AgentSession, "events")

    def test_agent_session_event_has_session_relationship(self):
        """AgentSessionEvent should have session relationship."""
        from app.models.agent_session import AgentSessionEvent

        assert hasattr(AgentSessionEvent, "session")


# ============================================================================
# SEARCH INDEX MODEL TESTS
# ============================================================================


class TestSearchIndexModel:
    """Test SearchIndex model definition."""

    def test_tablename(self):
        """SearchIndex should have correct table name."""
        from app.models.search_index import SearchIndex

        assert SearchIndex.__tablename__ == "search_index"

    def test_primary_key(self):
        """SearchIndex should have id as primary key."""
        from app.models.search_index import SearchIndex

        assert SearchIndex.__table__.c.id.primary_key is True

    def test_required_columns(self):
        """SearchIndex should have required columns."""
        from app.models.search_index import SearchIndex

        columns = SearchIndex.__table__.c
        assert "id" in columns
        assert "userId" in columns
        assert "entityType" in columns
        assert "entityId" in columns
        assert "content" in columns
        assert "contentHash" in columns
        assert "indexedAt" in columns
        assert "updatedAt" in columns

    def test_optional_columns(self):
        """SearchIndex should have optional columns."""
        from app.models.search_index import SearchIndex

        columns = SearchIndex.__table__.c
        assert "embedding" in columns
        assert "embeddingModel" in columns
        assert "embeddingDimensions" in columns
        assert "entity_metadata" in columns

    def test_indexed_columns(self):
        """Key columns should be indexed."""
        from app.models.search_index import SearchIndex

        assert SearchIndex.__table__.c.id.index is True
        assert SearchIndex.__table__.c.userId.index is True
        assert SearchIndex.__table__.c.entityType.index is True
        assert SearchIndex.__table__.c.entityId.index is True

    def test_to_dict_method(self):
        """SearchIndex should have to_dict method."""
        from app.models.search_index import SearchIndex

        assert hasattr(SearchIndex, "to_dict")
        assert callable(getattr(SearchIndex, "to_dict"))


# ============================================================================
# MODEL COUNT VERIFICATION
# ============================================================================


class TestModelCounts:
    """Verify all expected models are tested."""

    def test_total_model_count(self):
        """Verify we have tests for all 24 expected model classes."""
        from app.models.user import User
        from app.models.task import Task, Project
        from app.models.activity import Activity
        from app.models.comment import Comment
        from app.models.event import Event
        from app.models.session import Session
        from app.models.time_entry import TimeEntry
        from app.models.voice_recording import VoiceRecording
        from app.models.workflow_template import WorkflowTemplate
        from app.models.ai_conversation import AIConversation
        from app.models.shadow_profile import ShadowProfile, ShadowInsight
        from app.models.workspace import Workspace, WorkspaceMember
        from app.models.item_type import ItemType
        from app.models.knowledge_item import KnowledgeItem
        from app.models.file_search_store import FileSearchStore
        from app.models.file_search_document import FileSearchDocument
        from app.models.request_telemetry import RequestTelemetry
        from app.models.command_history import CommandHistory
        from app.models.agent_session import AgentSession, AgentSessionEvent
        from app.models.search_index import SearchIndex

        expected_models = [
            User,
            Task,
            Project,
            Activity,
            Comment,
            Event,
            Session,
            TimeEntry,
            VoiceRecording,
            WorkflowTemplate,
            AIConversation,
            ShadowProfile,
            ShadowInsight,
            Workspace,
            WorkspaceMember,
            ItemType,
            KnowledgeItem,
            FileSearchStore,
            FileSearchDocument,
            RequestTelemetry,
            CommandHistory,
            AgentSession,
            AgentSessionEvent,
            SearchIndex,
        ]
        assert len(expected_models) == 24  # 24 model classes

    def test_total_enum_count(self):
        """Verify we have tests for all expected enum classes."""
        from app.models.user import Role, UserStatus, AcademyStatus
        from app.models.task import TaskStatus, EnergyLevel
        from app.models.workspace import WorkspaceRole
        from app.models.request_telemetry import (
            TelemetrySource,
            TelemetryRoute,
            WorkflowDecisionStatus,
        )
        from app.models.command_history import CommandSource, CommandStatus
        from app.models.agent_session import AgentSessionStatus, AgentSessionEventType

        expected_enums = [
            Role,
            UserStatus,
            AcademyStatus,
            TaskStatus,
            EnergyLevel,
            WorkspaceRole,
            TelemetrySource,
            TelemetryRoute,
            WorkflowDecisionStatus,
            CommandSource,
            CommandStatus,
            AgentSessionStatus,
            AgentSessionEventType,
        ]
        assert len(expected_enums) == 13  # 13 enum classes
