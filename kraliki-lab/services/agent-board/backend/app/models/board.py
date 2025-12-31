from pydantic import BaseModel
from typing import List, Optional

class BoardConfig(BaseModel):
    """Board configuration model"""
    name: str
    description: str
    icon: str
    allowed_agents: List[str]
    tags: List[str]
    color: str

class Board(BaseModel):
    """Board model"""
    id: str
    name: str
    description: str
    icon: str
    color: str
    post_count: int = 0
    agent_count: int = 0
