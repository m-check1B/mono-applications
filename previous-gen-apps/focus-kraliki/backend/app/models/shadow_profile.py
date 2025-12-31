from sqlalchemy import Column, String, DateTime, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ShadowProfile(Base):
    """Shadow Analysis Profile - Jungian archetype-based personality insights"""
    __tablename__ = "shadow_profile"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    archetype = Column(String(50), nullable=False)  # warrior, sage, lover, creator, caregiver, explorer
    unlock_day = Column(Integer, default=1, nullable=False)
    total_days = Column(Integer, default=30, nullable=False)
    insights_data = Column(JSON, default=dict, nullable=True)  # Stores aggregated insights
    patterns = Column(JSON, default=dict, nullable=True)  # Behavioral patterns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="shadow_profile")
    insights = relationship("ShadowInsight", back_populates="profile", cascade="all, delete-orphan")


class ShadowInsight(Base):
    """Individual shadow insights unlocked progressively over 30 days"""
    __tablename__ = "shadow_insight"

    id = Column(String, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("shadow_profile.id", ondelete="CASCADE"), nullable=False, index=True)
    day = Column(Integer, nullable=False, index=True)
    insight_type = Column(String(50), nullable=False)  # awareness, understanding, integration
    content = Column(String, nullable=False)  # The actual insight text
    unlocked = Column(Boolean, default=False, nullable=False, index=True)
    unlocked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = relationship("ShadowProfile", back_populates="insights")
