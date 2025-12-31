from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class AssistantLiveRequest(BaseModel):
    message: str
    conversationHistory: List[ChatMessage] = []
    context: Optional[Dict[str, Any]] = None

class AssistantLiveResponse(BaseModel):
    response: str
    model: str
    toolCalls: List[Dict[str, Any]] = []
    metadata: Optional[Dict[str, Any]] = None
