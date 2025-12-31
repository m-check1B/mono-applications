"""Organization model - SQLAlchemy 2.0"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organization(Base):
    """Organization model"""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # users: Mapped[list["User"]] = relationship(back_populates="organization")
    # teams: Mapped[list["Team"]] = relationship(back_populates="organization")
    # campaigns: Mapped[list["Campaign"]] = relationship(back_populates="organization")
    # calls: Mapped[list["Call"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"
