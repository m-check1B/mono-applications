"""
Search Index Model

Stores embeddings for semantic search across all indexable entities.
Supports tasks, projects, knowledge items, and future entity types.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class SearchIndex(Base):
    """
    SearchIndex stores vector embeddings for semantic search.

    This enables fast semantic search across all user content without
    requiring external services like Gemini File Search.

    Design:
    - Each indexed entity gets one row
    - Embeddings stored as JSON array (SQLite compatible)
    - Content hash for change detection
    - Entity type for filtering (task, project, knowledge_item, etc.)
    """
    __tablename__ = "search_index"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)

    # Entity reference
    entityType = Column(String(50), nullable=False, index=True)  # task, project, knowledge_item
    entityId = Column(String, nullable=False, index=True)

    # Searchable content (concatenated title + description/content)
    content = Column(String, nullable=False)
    contentHash = Column(String(64), nullable=False)  # SHA256 hash for change detection

    # Vector embedding (stored as JSON array for SQLite compatibility)
    # For production PostgreSQL, consider using pgvector extension
    embedding = Column(JSON, nullable=True)
    embeddingModel = Column(String(100), nullable=True)  # e.g., "voyage-3-lite"
    embeddingDimensions = Column(Integer, nullable=True)  # e.g., 512, 1024

    # Entity metadata for filtering
    entity_metadata = Column(JSON, nullable=True)  # {status, priority, tags, etc.}

    # Timestamps
    indexedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="search_indices")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "entityType": self.entityType,
            "entityId": self.entityId,
            "content": self.content[:200] + "..." if len(self.content) > 200 else self.content,
            "embeddingModel": self.embeddingModel,
            "embeddingDimensions": self.embeddingDimensions,
            "metadata": self.entity_metadata,
            "indexedAt": self.indexedAt.isoformat() if self.indexedAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }
