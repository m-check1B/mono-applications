from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Session(Base):
    __tablename__ = "userSession"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    sessionToken = Column(String, unique=True, nullable=False)
    refreshTokenHash = Column(String, nullable=False)
    expiresAt = Column(DateTime, nullable=False)
    lastActivity = Column(DateTime, nullable=True)
    revokedAt = Column(DateTime, nullable=True)
    ipAddress = Column(String, nullable=True)
    userAgent = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    lastRefreshAt = Column(DateTime, nullable=True)
    refreshCount = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
