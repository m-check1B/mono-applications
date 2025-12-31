from sqlalchemy import Column, String, DateTime, Index
from datetime import datetime
from app.core.database import Base


class FileSearchStore(Base):
    """
    FileSearchStore represents a Gemini File Search store.

    Stores metadata about File Search stores created in Gemini API.
    Each organization has one main store, and users can optionally have personal stores.

    Based on Gemini File Search API schema.
    """
    __tablename__ = "file_search_store"

    id = Column(String, primary_key=True, index=True)
    organizationId = Column(String, nullable=False, index=True)
    userId = Column(String, nullable=True)  # Nullable for org-level stores
    store_name = Column(String, unique=True, nullable=False)  # Full File Search store name (e.g., "fileSearchStores/xyz123")
    kind = Column(String, nullable=False)  # e.g., "org_main" or "user_personal"
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_file_search_store_org_kind', 'organizationId', 'kind'),
        Index('idx_file_search_store_name', 'store_name'),
    )
