from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class VoiceRecording(Base):
    __tablename__ = "voice_recording"

    id = Column(String, primary_key=True, index=True)
    userId = Column(String, ForeignKey("user.id"), nullable=False)
    sessionId = Column(String, nullable=True)

    # Audio metadata
    audioUrl = Column(String, nullable=True)  # S3/storage URL
    duration = Column(Float, nullable=True)  # seconds
    mimetype = Column(String, default="audio/wav", nullable=False)

    # Transcription
    transcript = Column(String, nullable=True)
    language = Column(String, default="en", nullable=False)
    confidence = Column(Float, nullable=True)

    # AI Processing
    processedResult = Column(JSON, nullable=True)  # Structured output
    intent = Column(String, nullable=True)  # create_task, question, etc.

    # Metadata
    provider = Column(String, nullable=True)  # deepgram, gemini, openai
    record_metadata = Column(JSON, nullable=True)

    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="voice_recordings")
