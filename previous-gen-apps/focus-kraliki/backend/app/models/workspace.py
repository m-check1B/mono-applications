"""
Workspace Models
Defines collaborative workspace and membership tables
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class WorkspaceRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class Workspace(Base):
    __tablename__ = "workspace"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)
    ownerId = Column(String, ForeignKey("user.id"), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="owned_workspaces", foreign_keys=[ownerId])
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="workspace")
    projects = relationship("Project", back_populates="workspace")
    time_entries = relationship("TimeEntry", back_populates="workspace")


class WorkspaceMember(Base):
    __tablename__ = "workspace_member"

    id = Column(String, primary_key=True, index=True)
    workspaceId = Column(String, ForeignKey("workspace.id"), nullable=False)
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    role = Column(SQLEnum(WorkspaceRole), default=WorkspaceRole.MEMBER, nullable=False)
    permissions = Column(JSON, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")
