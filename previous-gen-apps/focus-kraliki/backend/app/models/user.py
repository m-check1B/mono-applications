import logging

import secrets
from sqlalchemy import (
    Column,
    String,
    DateTime,
    JSON,
    Enum as SQLEnum,
    Integer,
    Boolean,
    ForeignKey,
    event,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

logger = logging.getLogger(__name__)


class Role(str, enum.Enum):
    AGENT = "AGENT"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class AcademyStatus(str, enum.Enum):
    NONE = "NONE"
    WAITLIST = "WAITLIST"
    STUDENT = "STUDENT"
    GRADUATE = "GRADUATE"


class NestedMutableDict(MutableDict):
    """Mutable dict that also mutates nested dictionaries."""

    @classmethod
    def coerce(cls, key, value):
        """Convert plain dicts (including nested) into NestedMutableDict."""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            coerced = cls()
            for k, v in value.items():
                coerced[k] = cls.coerce(k, v)
            return coerced
        # Non-dict values are returned as-is so JSON values like booleans/strings work
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, self.coerce(key, value))


def _generate_org_id() -> str:
    """Generate a fallback organization ID for tests and local usage."""
    return secrets.token_urlsafe(16)


class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    firstName = Column(String, nullable=True)
    lastName = Column(String, nullable=True)
    passwordHash = Column(String, nullable=True)
    role = Column(SQLEnum(Role), default=Role.AGENT, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    organizationId = Column(String, nullable=False, default=_generate_org_id)
    phoneExtension = Column(String, nullable=True)
    department = Column(String, nullable=True)
    preferences = Column(NestedMutableDict.as_mutable(JSON), nullable=True)
    lastLoginAt = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # AI Billing & BYOK fields (Phase 1)
    openRouterApiKey = Column(String, nullable=True)
    usageCount = Column(Integer, default=0, nullable=False)
    isPremium = Column(Boolean, default=False, nullable=False)
    stripeCustomerId = Column(String, nullable=True)
    stripeSubscriptionId = Column(String, nullable=True)
    activeWorkspaceId = Column(
        String,
        ForeignKey(
            "workspace.id",
            use_alter=True,
            name="fk_user_active_workspace",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # Persona & Privacy Preferences (Track 5)
    selectedPersona = Column(
        String, nullable=True
    )  # 'solo-developer', 'freelancer', etc.
    onboardingCompleted = Column(Boolean, default=False, nullable=False)
    onboardingStep = Column(Integer, default=0, nullable=False)
    privacyPreferences = Column(
        NestedMutableDict.as_mutable(JSON), nullable=True
    )  # BYOK acknowledgment, data privacy settings
    featureToggles = Column(
        NestedMutableDict.as_mutable(JSON), nullable=True
    )  # Gemini File Search, II-Agent, etc.

    # AI Academy Status
    academyStatus = Column(
        SQLEnum(AcademyStatus), default=AcademyStatus.NONE, nullable=False
    )
    academyInterest = Column(String, nullable=True)  # e.g., 'L1_STUDENT'

    # Relationships
    tasks = relationship("Task", back_populates="user", foreign_keys="Task.userId")
    assigned_tasks = relationship(
        "Task", foreign_keys="Task.assignedUserId", viewonly=True
    )
    projects = relationship("Project", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    events = relationship("Event", back_populates="user")
    time_entries = relationship("TimeEntry", back_populates="user")
    voice_recordings = relationship("VoiceRecording", back_populates="user")
    workflow_templates = relationship("WorkflowTemplate", back_populates="user")
    ai_conversations = relationship("AIConversation", back_populates="user")
    shadow_profile = relationship("ShadowProfile", back_populates="user", uselist=False)
    item_types = relationship(
        "ItemType", back_populates="user", cascade="all, delete-orphan"
    )
    knowledge_items = relationship(
        "KnowledgeItem", back_populates="user", cascade="all, delete-orphan"
    )
    search_indices = relationship("SearchIndex", back_populates="user")
    owned_workspaces = relationship(
        "Workspace", back_populates="owner", foreign_keys="Workspace.ownerId"
    )
    workspace_memberships = relationship(
        "WorkspaceMember",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="WorkspaceMember.userId",
    )
    active_workspace = relationship("Workspace", foreign_keys=[activeWorkspaceId])


# Mark JSON columns dirty when replaced (helps nested mutation detection in tests)
def _safe_flag_modified(target, attr):
    try:
        from sqlalchemy.orm.attributes import flag_modified as _flag_modified

        _flag_modified(target, attr)
    except InvalidRequestError as e:
        logger.warning(f"Failed to flag attribute {attr} as modified: {e}")
        return


@event.listens_for(User.preferences, "set", retval=True)
def _preferences_set(target, value, oldvalue, initiator):
    _safe_flag_modified(target, "preferences")
    return value


@event.listens_for(User.privacyPreferences, "set", retval=True)
def _privacy_preferences_set(target, value, oldvalue, initiator):
    _safe_flag_modified(target, "privacyPreferences")
    return value


@event.listens_for(User.featureToggles, "set", retval=True)
def _feature_toggles_set(target, value, oldvalue, initiator):
    _safe_flag_modified(target, "featureToggles")
    return value


# Utility functions to ensure defaults when loading legacy users
def ensure_feature_toggles(user):
    if not user.featureToggles:
        user.featureToggles = {
            "geminiFileSearch": True,
            "iiAgent": True,
            "voiceTranscription": True,
        }


def ensure_privacy_preferences(user):
    if not user.privacyPreferences:
        user.privacyPreferences = {
            "geminiFileSearchEnabled": True,
            "iiAgentEnabled": True,
            "dataPrivacyAcknowledged": False,
        }
