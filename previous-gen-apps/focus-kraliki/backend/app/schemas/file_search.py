from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# File Search Query Schemas

class FileSearchQueryRequest(BaseModel):
    """
    Request schema for File Search query endpoint.

    Used to search the organization's knowledge base using Gemini AI.
    """
    query: str = Field(..., description="Search query or question", min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context for filtering or additional parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the main tasks for this week?",
                "context": {"filter_by_type": "Tasks", "completed": False}
            }
        }


class CitationMetadata(BaseModel):
    """Metadata for a search result citation"""
    knowledge_item_id: Optional[str] = None
    title: Optional[str] = None
    type_id: Optional[str] = None
    completed: Optional[bool] = None
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    kind: Optional[str] = None


class Citation(BaseModel):
    """Citation/source for a File Search answer"""
    text: str = Field(..., description="Cited text excerpt")
    source: str = Field(default="Unknown", description="Source identifier")
    knowledge_item_id: Optional[str] = Field(None, description="ID of the knowledge item if citation is from one")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the citation")


class FileSearchQueryResponse(BaseModel):
    """
    Response schema for File Search query endpoint.

    Contains the AI-generated answer and citations from the knowledge base.
    """
    answer: str = Field(..., description="AI-generated answer based on knowledge base")
    citations: List[Citation] = Field(default_factory=list, description="List of citations/sources")
    model: Optional[str] = Field(None, description="AI model used for the query")
    store_name: Optional[str] = Field(None, description="File Search store name used")
    fallback: Optional[str] = Field(None, description="Fallback method used if Gemini unavailable")
    note: Optional[str] = Field(None, description="Additional notes or warnings")
    error: Optional[str] = Field(None, description="Error code if query failed")
    total: Optional[int] = Field(None, description="Total results found (for SQL fallback)")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on your knowledge base, you have 3 main tasks for this week: 1) Complete project proposal, 2) Review design mockups, 3) Schedule team meeting.",
                "citations": [
                    {
                        "text": "Complete project proposal by Friday",
                        "source": "Tasks",
                        "knowledge_item_id": "abc123",
                        "metadata": {"title": "Project Proposal Task", "type_id": "tasks"}
                    }
                ],
                "model": "gemini-2.0-flash-exp",
                "store_name": "fileSearchStores/xyz789"
            }
        }


# File Search Store Schemas

class FileSearchStoreBase(BaseModel):
    """Base schema for File Search store"""
    organizationId: str
    userId: Optional[str] = None
    store_name: str
    kind: str


class FileSearchStoreResponse(FileSearchStoreBase):
    """Response schema for File Search store"""
    id: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Import/Document Schemas

class DocumentImportRequest(BaseModel):
    """Request to manually import a knowledge item to File Search"""
    knowledge_item_id: str = Field(..., description="ID of the knowledge item to import")


class DocumentImportResponse(BaseModel):
    """Response after importing a document"""
    success: bool
    document_name: Optional[str] = None
    knowledge_item_id: str
    message: str


class StoreStatusResponse(BaseModel):
    """Response with File Search store status"""
    store_exists: bool
    store_name: Optional[str] = None
    organization_id: str
    document_count: Optional[int] = None
    gemini_available: bool


class DocumentListItem(BaseModel):
    """Information about a document in the File Search store"""
    name: str
    display_name: str
    size_bytes: Optional[int] = None
    create_time: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response with list of documents in store"""
    documents: List[DocumentListItem]
    total: int
    store_name: str
