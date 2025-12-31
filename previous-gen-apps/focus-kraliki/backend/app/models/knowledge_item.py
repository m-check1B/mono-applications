from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class KnowledgeItem(Base):
    """
    KnowledgeItem represents a generic knowledge entry
    (idea, note, task, plan, etc.) with flexible metadata
    Based on Focus-Mind's knowledgeItems schema

    Unified model for all knowledge types - replaces separate tables
    """
    __tablename__ = "knowledge_item"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    typeId = Column(String, ForeignKey("item_type.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)  # Main content/description
    item_metadata = Column(JSON, nullable=True)  # Flexible metadata for type-specific data
    completed = Column(Boolean, default=False, nullable=False)  # For task-like items
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="knowledge_items")
    item_type = relationship("ItemType", back_populates="knowledge_items")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "typeId": self.typeId,
            "title": self.title,
            "content": self.content,
            "metadata": self.item_metadata,  # Map to 'metadata' for API consistency
            "completed": self.completed,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
            # Include type information for convenience
            "typeName": self.item_type.name if self.item_type else None,
            "typeIcon": self.item_type.icon if self.item_type else None,
            "typeColor": self.item_type.color if self.item_type else None
        }
