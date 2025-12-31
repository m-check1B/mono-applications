"""User model for persistent storage."""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class User(Base):
    """User profile and subscription status."""
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Profile data
    birth_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Subscription status
    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    plan: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "first_name": self.first_name,
            "birth_date": self.birth_date,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "premium": self.premium,
            "premium_until": self.premium_until,
            "plan": self.plan,
        }
