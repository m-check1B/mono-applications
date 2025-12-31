"""Team models - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
import enum
from sqlalchemy import String, DateTime, JSON, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TeamRole(str, enum.Enum):
    """Team member roles"""
    MEMBER = "MEMBER"
    LEAD = "LEAD"
    SUPERVISOR = "SUPERVISOR"


class Team(Base):
    """Team model"""

    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    organization_id: Mapped[str] = mapped_column(String(30), ForeignKey("organizations.id", ondelete="CASCADE"))
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # organization: Mapped["Organization"] = relationship(back_populates="teams")
    # members: Mapped[list["TeamMember"]] = relationship(back_populates="team")

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class TeamMember(Base):
    """Team membership model"""

    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(30), ForeignKey("users.id", ondelete="CASCADE"))
    team_id: Mapped[str] = mapped_column(String(30), ForeignKey("teams.id", ondelete="CASCADE"))
    role: Mapped[TeamRole] = mapped_column(SQLEnum(TeamRole), default=TeamRole.MEMBER)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    # user: Mapped["User"] = relationship(back_populates="team_members")
    # team: Mapped["Team"] = relationship(back_populates="members")

    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
    )

    def __repr__(self) -> str:
        return f"<TeamMember {self.user_id} in {self.team_id}>"
