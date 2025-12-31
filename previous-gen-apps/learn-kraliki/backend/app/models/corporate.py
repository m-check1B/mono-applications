"""
Corporate Team Model
Supports B2B corporate training packages
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    JSON,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class CorporateTeam(Base):
    """Represents a corporate team that purchased training."""

    __tablename__ = "corporate_teams"

    id = Column(String, primary_key=True)  # Team ID
    company_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_name = Column(String, nullable=False)

    # Package details
    package_type = Column(String, nullable=False)  # "team", "corporate", "enterprise"
    seat_count = Column(Integer, nullable=False)
    price_eur = Column(Float, nullable=False)
    currency = Column(String, default="EUR")

    # Billing
    billing_period = Column(
        String, default="one_time"
    )  # "one_time", "monthly", "yearly"
    paid_at = Column(DateTime, nullable=True)
    payment_id = Column(String, nullable=True)  # Stripe payment ID
    invoice_id = Column(String, nullable=True)

    # Customization
    custom_branding = Column(Boolean, default=False)
    company_logo_url = Column(String, nullable=True)
    custom_domain = Column(String, nullable=True)

    # Status
    status = Column(String, default="active")  # "active", "suspended", "cancelled"
    expires_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    members = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CorporateTeam id={self.id} company={self.company_name} seats={self.seat_count}>"


class TeamMember(Base):
    """Represents a team member enrolled in corporate training."""

    __tablename__ = "team_members"

    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("corporate_teams.id"), nullable=False)
    user_id = Column(String, nullable=False)  # External user ID (e.g., from Zitadel)
    user_email = Column(String, nullable=False)
    user_name = Column(String, nullable=True)

    # Enrollment status
    status = Column(
        String, default="invited"
    )  # "invited", "enrolled", "active", "completed"

    # Progress tracking (for each course)
    enrolled_courses = Column(
        JSON, default=list
    )  # [{"course_slug": "ai-fundamentals-cs", "completed_lessons": [...]}]

    # Certification
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String, nullable=True)
    certificate_issued_at = Column(DateTime, nullable=True)

    # Timestamps
    invited_at = Column(DateTime, default=utcnow)
    enrolled_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("CorporateTeam", back_populates="members")

    def __repr__(self):
        return f"<TeamMember id={self.id} email={self.user_email} team={self.team_id}>"
