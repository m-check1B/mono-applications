from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AIConversation(Base):
    __tablename__ = "ai_conversation"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False)

    # Conversation metadata
    title = Column(String, nullable=True)  # Auto-generated or user-set
    type = Column(String, default="chat", nullable=False)  # chat, voice, assistant

    # Messages
    messages = Column(JSON, nullable=False, default=[])
    """
    Example messages:
    [
        {
            "role": "user",
            "content": "Create a task for tomorrow",
            "timestamp": "2025-11-10T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I'll create that task for you...",
            "timestamp": "2025-11-10T10:00:02Z",
            "model": "claude-3-5-sonnet"
        }
    ]
    """

    # Context and memory
    context = Column(JSON, nullable=True)  # Persistent context
    summary = Column(String, nullable=True)  # AI-generated summary
    tags = Column(JSON, default=[], nullable=False)  # JSON for SQLite compatibility (was ARRAY)

    # AI metadata
    primaryModel = Column(String, nullable=True)  # claude-3-5-sonnet, gpt-4, etc.
    totalTokens = Column(Integer, default=0, nullable=False)
    totalCost = Column(Float, default=0.0, nullable=False)

    # Status
    isActive = Column(Boolean, default=True, nullable=False)
    isArchived = Column(Boolean, default=False, nullable=False)

    # Timestamps
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    lastMessageAt = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="ai_conversations")
