from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class FileSearchDocument(Base):
    """
    FileSearchDocument represents a document imported to Gemini File Search.

    This table provides fine-grained citation mapping between knowledge items
    and their corresponding File Search documents. It enables:
    - Tracking which knowledge items are indexed
    - Deleting specific documents when items are removed
    - Audit trail of imports
    - Citation mapping for search results

    Based on Gemini File Search API schema.
    """
    __tablename__ = "file_search_document"

    id = Column(String, primary_key=True, index=True)
    organizationId = Column(String, nullable=False, index=True)
    userId = Column(String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)

    # Link to source knowledge item (nullable for voice transcripts)
    knowledgeItemId = Column(String, ForeignKey("knowledge_item.id", ondelete="CASCADE"), nullable=True, index=True)

    # Link to voice recording (nullable for knowledge items)
    voiceRecordingId = Column(String, ForeignKey("voice_recording.id", ondelete="CASCADE"), nullable=True, index=True)

    # File Search identifiers
    storeName = Column(String, nullable=False)  # Full store name from Gemini API
    documentName = Column(String, nullable=False)  # Full document name from Gemini API

    # Document metadata
    kind = Column(String, nullable=False)  # "knowledge_item" or "voice_transcript"

    # Timestamps
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    knowledge_item = relationship("KnowledgeItem", foreign_keys=[knowledgeItemId])
    voice_recording = relationship("VoiceRecording", foreign_keys=[voiceRecordingId])

    __table_args__ = (
        Index('idx_file_search_doc_org', 'organizationId'),
        Index('idx_file_search_doc_user', 'userId'),
        Index('idx_file_search_doc_knowledge', 'knowledgeItemId'),
        Index('idx_file_search_doc_voice', 'voiceRecordingId'),
        Index('idx_file_search_doc_store', 'storeName'),
        Index('idx_file_search_doc_kind', 'kind'),
    )
