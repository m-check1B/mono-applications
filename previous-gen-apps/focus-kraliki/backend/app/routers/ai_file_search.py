"""
AI File Search Router

Provides semantic search over user's knowledge using Gemini File Search.
Implements Phase 1: Backend Foundations for Gemini File Search Integration.

Key Features:
- Semantic search with AI-powered understanding
- Organization-scoped File Search stores
- Graceful fallback to SQL search when Gemini unavailable
- Automatic knowledge item import on creation/update
- Citation tracking and source mapping

Endpoints:
- POST /ai/file-search/query - Semantic search over knowledge base
- GET /ai/file-search/status - Check File Search availability and store status
- POST /ai/file-search/import - Manually import knowledge item to File Search
- GET /ai/file-search/documents - List documents in File Search store
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.knowledge_item import KnowledgeItem
from app.schemas.file_search import (
    FileSearchQueryRequest,
    FileSearchQueryResponse,
    DocumentImportRequest,
    DocumentImportResponse,
    StoreStatusResponse,
    DocumentListResponse,
    DocumentListItem
)
from app.services.gemini_file_search import (
    query_store,
    get_or_create_org_store,
    import_knowledge_item,
    is_gemini_available,
    list_store_documents
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/file-search", tags=["AI File Search"])


@router.post("/query", response_model=FileSearchQueryResponse)
async def file_search_query(
    query_request: FileSearchQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search over user's knowledge using Gemini File Search.

    This endpoint provides AI-powered semantic search across the organization's
    knowledge base. It uses Gemini's File Search capability to understand natural
    language queries and return relevant answers with citations.

    **Features:**
    - Natural language understanding
    - Semantic similarity matching
    - Automatic citation extraction
    - Organization-scoped search
    - Graceful fallback to SQL search

    **Request:**
    ```json
    {
        "query": "What are the main tasks for this week?",
        "context": {"filter_by_type": "Tasks"}
    }
    ```

    **Response:**
    ```json
    {
        "answer": "Based on your knowledge base, you have 3 main tasks...",
        "citations": [...],
        "model": "gemini-2.0-flash-exp",
        "store_name": "fileSearchStores/xyz789"
    }
    ```

    **Fallback Behavior:**
    If Gemini is unavailable, the endpoint falls back to SQL ILIKE search
    and returns a note indicating the fallback method.
    """
    logger.info(f"File Search query from user {current_user.id}: {query_request.query}")

    try:
        # Query the File Search store (handles Gemini unavailability internally)
        result = await query_store(
            db=db,
            user=current_user,
            prompt=query_request.query,
            context=query_request.context
        )

        # Convert result to Pydantic response
        return FileSearchQueryResponse(**result)

    except Exception as e:
        logger.error(f"Error in file_search_query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File Search query failed: {str(e)}"
        )


@router.get("/status", response_model=StoreStatusResponse)
async def get_file_search_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check File Search availability and store status.

    Returns information about:
    - Whether Gemini File Search is available
    - Whether the organization has a File Search store
    - Store name and document count (if available)

    This endpoint is useful for the frontend to determine whether to show
    File Search features and provide appropriate user messaging.

    **Response:**
    ```json
    {
        "store_exists": true,
        "store_name": "fileSearchStores/xyz789",
        "organization_id": "org123",
        "document_count": 42,
        "gemini_available": true
    }
    ```
    """
    logger.info(f"Checking File Search status for user {current_user.id}")

    try:
        # Check if Gemini is available
        gemini_available = is_gemini_available()

        # Try to get existing store (won't create if doesn't exist)
        from app.models.file_search_store import FileSearchStore
        existing_store = db.query(FileSearchStore).filter(
            FileSearchStore.organizationId == current_user.organizationId,
            FileSearchStore.kind == "org_main"
        ).first()

        if existing_store:
            # Try to get document count if Gemini is available
            document_count = None
            if gemini_available:
                try:
                    documents = await list_store_documents(db, current_user, limit=1000)
                    if documents:
                        document_count = len(documents)
                except Exception as e:
                    logger.debug(f"Could not get document count: {e}")

            return StoreStatusResponse(
                store_exists=True,
                store_name=existing_store.store_name,
                organization_id=current_user.organizationId,
                document_count=document_count,
                gemini_available=gemini_available
            )
        else:
            return StoreStatusResponse(
                store_exists=False,
                store_name=None,
                organization_id=current_user.organizationId,
                document_count=None,
                gemini_available=gemini_available
            )

    except Exception as e:
        logger.error(f"Error checking File Search status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check File Search status: {str(e)}"
        )


@router.post("/import", response_model=DocumentImportResponse)
async def import_knowledge_item_to_file_search(
    import_request: DocumentImportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually import a knowledge item to File Search.

    This endpoint allows manual import/re-import of knowledge items to the
    File Search store. Normally, knowledge items are automatically imported
    on creation/update, but this endpoint is useful for:
    - Re-importing after Gemini was unavailable
    - Bulk import of existing knowledge items
    - Troubleshooting import issues

    **Request:**
    ```json
    {
        "knowledge_item_id": "abc123"
    }
    ```

    **Response:**
    ```json
    {
        "success": true,
        "document_name": "files/xyz789",
        "knowledge_item_id": "abc123",
        "message": "Knowledge item imported successfully"
    }
    ```
    """
    logger.info(f"Manual import request for knowledge item {import_request.knowledge_item_id}")

    # Verify the knowledge item exists and belongs to the user
    knowledge_item = db.query(KnowledgeItem).filter(
        KnowledgeItem.id == import_request.knowledge_item_id,
        KnowledgeItem.userId == current_user.id
    ).first()

    if not knowledge_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found or does not belong to you"
        )

    # Check if Gemini is available
    if not is_gemini_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini File Search is not available. Please configure GEMINI_API_KEY."
        )

    try:
        # Import the knowledge item
        document_name = await import_knowledge_item(db, current_user, knowledge_item)

        if document_name:
            return DocumentImportResponse(
                success=True,
                document_name=document_name,
                knowledge_item_id=knowledge_item.id,
                message="Knowledge item imported successfully to File Search"
            )
        else:
            return DocumentImportResponse(
                success=False,
                document_name=None,
                knowledge_item_id=knowledge_item.id,
                message="Import failed - check server logs for details"
            )

    except Exception as e:
        logger.error(f"Error importing knowledge item {import_request.knowledge_item_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_file_search_documents(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List documents in the organization's File Search store.

    Returns a list of all documents stored in the organization's Gemini File
    Search store, including metadata like size and creation time.

    This endpoint is useful for:
    - Monitoring what's indexed
    - Debugging import issues
    - Understanding store contents

    **Query Parameters:**
    - limit: Maximum number of documents to return (default: 100)

    **Response:**
    ```json
    {
        "documents": [
            {
                "name": "files/abc123",
                "display_name": "Task_xyz.txt",
                "size_bytes": 1024,
                "create_time": "2024-11-14T10:00:00Z"
            }
        ],
        "total": 42,
        "store_name": "fileSearchStores/xyz789"
    }
    ```
    """
    logger.info(f"Listing File Search documents for user {current_user.id}")

    # Check if Gemini is available
    if not is_gemini_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini File Search is not available. Please configure GEMINI_API_KEY."
        )

    try:
        # Get the store name
        store_name = await get_or_create_org_store(db, current_user)
        if not store_name:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File Search store not found for your organization"
            )

        # List documents
        documents = await list_store_documents(db, current_user, limit=limit)

        if documents is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list documents from File Search store"
            )

        # Convert to Pydantic models
        document_items = [DocumentListItem(**doc) for doc in documents]

        return DocumentListResponse(
            documents=document_items,
            total=len(document_items),
            store_name=store_name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing File Search documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


# Health check endpoint for File Search
@router.get("/health")
async def file_search_health_check():
    """
    Quick health check for File Search service.

    Returns:
    - gemini_available: Whether google-generativeai is installed
    - api_key_configured: Whether GEMINI_API_KEY is set

    This is a simple diagnostic endpoint that doesn't require authentication.
    """
    from app.core.config import settings

    return {
        "gemini_available": is_gemini_available(),
        "api_key_configured": bool(settings.GEMINI_API_KEY),
        "service": "File Search",
        "status": "healthy" if is_gemini_available() else "degraded"
    }
