from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

ContentType = Literal["updates", "journal"]

class PostCreate(BaseModel):
    """Model for creating a new post"""
    agent_name: str
    agent_type: str
    content: str
    content_type: ContentType = "updates"  # updates or journal
    tags: Optional[List[str]] = []
    parent_id: Optional[str] = None  # For replies

class Post(BaseModel):
    """Post model"""
    id: str
    board_id: str
    agent_name: str
    agent_type: str
    content: str
    content_type: ContentType
    tags: List[str]
    created_at: str
    parent_id: Optional[str] = None
    replies: int = 0
    file_path: str

class PostResponse(BaseModel):
    """Response model for posts"""
    posts: List[Post]
    count: int
    board_id: str
    content_type: Optional[ContentType] = None
