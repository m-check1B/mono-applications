from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ItemType(Base):
    """
    ItemType represents a category or type of knowledge item
    (e.g., idea, note, task, plan, custom types)
    Based on Focus-Mind's itemTypes schema

    Default types: Ideas, Notes, Tasks, Plans
    Users can create custom types
    """
    __tablename__ = "item_type"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)  # Description of the type
    icon = Column(String, nullable=False, default="Star")  # Icon name
    color = Column(String, nullable=False, default="blue")  # Color code
    isDefault = Column(Boolean, default=False, nullable=False)  # True for Ideas, Notes, Tasks, Plans
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="item_types")
    knowledge_items = relationship("KnowledgeItem", back_populates="item_type", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "color": self.color,
            "isDefault": self.isDefault,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None
        }
