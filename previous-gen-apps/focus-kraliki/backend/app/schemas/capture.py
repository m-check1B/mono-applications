from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class CaptureCreate(BaseModel):
    """Create a new capture from various sources"""
    source_type: Literal["image", "url", "text", "file"] = Field(
        description="Type of captured content"
    )
    content: str = Field(
        description="Raw content: base64 for images, URL string, or text content"
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional title (auto-generated if not provided)"
    )
    context: Optional[str] = Field(
        default=None,
        description="Optional context about why this was captured"
    )


class CaptureProcessed(BaseModel):
    """AI-processed capture metadata"""
    summary: str = Field(description="AI-generated summary of the content")
    key_points: List[str] = Field(default_factory=list, description="Extracted key points")
    entities: List[str] = Field(default_factory=list, description="Named entities found")
    suggested_tags: List[str] = Field(default_factory=list, description="Suggested categorization tags")
    action_items: List[str] = Field(default_factory=list, description="Potential action items extracted")
    relevance_context: Optional[str] = Field(
        default=None,
        description="How this relates to user's current work context"
    )


class CaptureResponse(BaseModel):
    """Full capture response with AI processing"""
    id: str
    userId: str
    source_type: str
    title: str
    content: Optional[str] = None
    original_content: str = Field(description="Original raw content (URL, text, or file reference)")
    processed: CaptureProcessed
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class CaptureListResponse(BaseModel):
    """List of captures"""
    captures: List[CaptureResponse]
    total: int


class CaptureContextResponse(BaseModel):
    """Captures formatted for AI chat context injection"""
    context_summary: str = Field(
        description="Combined summary of recent captures for AI context"
    )
    captures: List[Dict[str, Any]] = Field(
        description="Recent captures with relevance scores"
    )
    total_captures: int
