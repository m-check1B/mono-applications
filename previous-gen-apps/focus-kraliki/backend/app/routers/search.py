"""
Search Router

Provides semantic search endpoints for Focus by Kraliki.
Enables users to search across all their content using natural language.

Endpoints:
- POST /search - Semantic search across all content
- POST /search/index - Index specific entity
- POST /search/index-all - Index all user content
- DELETE /search/index/{entity_type}/{entity_id} - Remove from index
- GET /search/stats - Get index statistics
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.semantic_search import get_semantic_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


# Request/Response Models

class SearchRequest(BaseModel):
    """Search request"""
    query: str
    entityTypes: Optional[List[str]] = None  # task, project, knowledge_item
    limit: int = 20
    minScore: float = 0.3


class SearchResult(BaseModel):
    """Individual search result"""
    id: str
    entityType: str
    entityId: str
    content: str
    metadata: Optional[dict] = None
    score: float
    indexedAt: Optional[str] = None
    searchType: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response"""
    results: List[SearchResult]
    count: int
    query: str


class IndexRequest(BaseModel):
    """Index request for a single entity"""
    entityType: str  # task, project, knowledge_item
    entityId: str
    force: bool = False


class IndexAllRequest(BaseModel):
    """Index all request"""
    entityTypes: Optional[List[str]] = None
    force: bool = False


class IndexResponse(BaseModel):
    """Index response"""
    success: bool
    indexed: Optional[dict] = None
    message: Optional[str] = None


class StatsResponse(BaseModel):
    """Index statistics response"""
    total: int
    withEmbeddings: int
    byType: dict
    embeddingModel: str
    embeddingDimensions: int


# Endpoints

@router.post("/", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform semantic search across user's content.

    Uses vector embeddings for semantic similarity matching.
    Falls back to keyword search if embeddings unavailable.

    Searchable content types:
    - task: Tasks with titles and descriptions
    - project: Projects with names and descriptions
    - knowledge_item: Knowledge items (ideas, notes, tasks, plans)
    """
    search_service = get_semantic_search_service(db, current_user)

    try:
        results = search_service.search(
            query=request.query,
            entity_types=request.entityTypes,
            limit=request.limit,
            min_score=request.minScore
        )

        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            count=len(results),
            query=request.query
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/index", response_model=IndexResponse)
async def index_entity(
    request: IndexRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Index a single entity for semantic search.

    This creates/updates the search index entry for the specified entity.
    Use force=true to re-generate embeddings even if content unchanged.
    """
    search_service = get_semantic_search_service(db, current_user)

    try:
        result = search_service.index_entity(
            entity_type=request.entityType,
            entity_id=request.entityId,
            force=request.force
        )

        if result:
            return IndexResponse(
                success=True,
                indexed={request.entityType: 1},
                message=f"Indexed {request.entityType}/{request.entityId}"
            )
        else:
            return IndexResponse(
                success=False,
                message=f"Failed to index {request.entityType}/{request.entityId}"
            )
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/index-all", response_model=IndexResponse)
async def index_all_entities(
    request: IndexAllRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Index all entities of specified types for the user.

    This can take a while for users with many items.
    Use force=true to re-generate all embeddings.

    Default indexes: task, project, knowledge_item
    """
    search_service = get_semantic_search_service(db, current_user)

    try:
        results = search_service.index_all(
            entity_types=request.entityTypes,
            force=request.force
        )

        total = sum(results.values())
        return IndexResponse(
            success=True,
            indexed=results,
            message=f"Indexed {total} entities"
        )
    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.delete("/index/{entity_type}/{entity_id}")
async def delete_index(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an entity from the search index.

    Use when an entity is deleted or should no longer be searchable.
    """
    search_service = get_semantic_search_service(db, current_user)

    try:
        deleted = search_service.delete_index(entity_type, entity_id)
        return {
            "success": deleted,
            "deleted": entity_type + "/" + entity_id if deleted else None
        }
    except Exception as e:
        logger.error(f"Delete index failed: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_index_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the user's search index.

    Returns counts of indexed items by type and embedding status.
    """
    search_service = get_semantic_search_service(db, current_user)

    try:
        stats = search_service.get_index_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")
