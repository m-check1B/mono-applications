"""Search API routes - hybrid search (keyword + semantic)"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.storage import StorageService
from ..services.glm import GLMService
from ..services.usage import get_usage_service

router = APIRouter(prefix="/search", tags=["search"])
storage = StorageService()
glm = GLMService()
usage = get_usage_service()


class SearchRequest(BaseModel):
    """Request model for search"""
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20
    search_type: str = "hybrid"  # "keyword", "semantic", "hybrid"


class SearchResult(BaseModel):
    """Search result item"""
    id: str
    category: str
    title: str
    content: str
    tags: List[str]
    score: float
    file_path: str


class SearchResponse(BaseModel):
    """Response model for search"""
    results: List[SearchResult]
    count: int
    search_type: str


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Hybrid search across memory items

    - keyword: BM25/Whoosh full-text search
    - semantic: GLM 4.6 embedding similarity
    - hybrid: Combined ranking (default)
    """
    # Log usage
    usage.log_operation(
        action="retrieve",
        agent="unknown",
        key=f"search:{request.query[:50]}"
    )
    
    try:
        if request.search_type == "keyword":
            # Keyword-only search
            results = storage.search_items(
                query=request.query,
                category=request.category
            )

            # Filter by tags if provided
            if request.tags:
                results = [
                    r for r in results
                    if any(tag in r.get("tags", []) for tag in request.tags)
                ]

            # Format results
            formatted_results = [
                SearchResult(
                    id=r["id"],
                    category=r["category"],
                    title=r.get("title", r["id"]),
                    content=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                    tags=r.get("tags", []),
                    score=1.0,  # Keyword search doesn't provide scores
                    file_path=r["file_path"]
                )
                for r in results[:request.limit]
            ]

            return SearchResponse(
                results=formatted_results,
                count=len(formatted_results),
                search_type="keyword"
            )

        elif request.search_type == "semantic":
            # Semantic-only search
            all_items = storage.list_items(category=request.category, limit=1000)

            # Filter by tags if provided
            if request.tags:
                all_items = [
                    item for item in all_items
                    if any(tag in item.get("tags", []) for tag in request.tags)
                ]

            # Find semantically similar items
            similar_ids = glm.find_related_items(request.query, all_items)

            # Load full items
            results = []
            for item_id in similar_ids[:request.limit]:
                # Parse category/id from wikilink format
                if "/" in item_id:
                    cat, id_only = item_id.split("/", 1)
                    item = storage.load_item(cat, id_only)
                    if item:
                        results.append(item)

            formatted_results = [
                SearchResult(
                    id=r["id"],
                    category=r["category"],
                    title=r.get("title", r["id"]),
                    content=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                    tags=r.get("tags", []),
                    score=1.0,
                    file_path=r["file_path"]
                )
                for r in results
            ]

            return SearchResponse(
                results=formatted_results,
                count=len(formatted_results),
                search_type="semantic"
            )

        else:  # hybrid
            # Keyword search
            keyword_results = storage.search_items(
                query=request.query,
                category=request.category
            )

            # Semantic search
            all_items = storage.list_items(category=request.category, limit=1000)

            # Filter by tags if provided
            if request.tags:
                keyword_results = [
                    r for r in keyword_results
                    if any(tag in r.get("tags", []) for tag in request.tags)
                ]
                all_items = [
                    item for item in all_items
                    if any(tag in item.get("tags", []) for tag in request.tags)
                ]

            semantic_ids = glm.find_related_items(request.query, all_items)

            # Combine results (keyword first, then semantic)
            seen_ids = set()
            combined_results = []

            # Add keyword results
            for r in keyword_results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    combined_results.append(r)

            # Add semantic results not in keyword
            for item_id in semantic_ids:
                if "/" in item_id:
                    cat, id_only = item_id.split("/", 1)
                    full_id = f"{cat}/{id_only}"
                    if full_id not in seen_ids:
                        item = storage.load_item(cat, id_only)
                        if item:
                            seen_ids.add(full_id)
                            combined_results.append(item)

            # Limit results
            combined_results = combined_results[:request.limit]

            formatted_results = [
                SearchResult(
                    id=r["id"],
                    category=r["category"],
                    title=r.get("title", r["id"]),
                    content=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                    tags=r.get("tags", []),
                    score=1.0,
                    file_path=r["file_path"]
                )
                for r in combined_results
            ]

            return SearchResponse(
                results=formatted_results,
                count=len(formatted_results),
                search_type="hybrid"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions")
async def get_suggestions(query: str, limit: int = 5):
    """Get search suggestions as user types"""
    # Quick keyword search for suggestions
    results = storage.search_items(query=query, category=None)
    suggestions = [
        {
            "id": r["id"],
            "title": r.get("title", r["id"]),
            "category": r["category"]
        }
        for r in results[:limit]
    ]
    return {"suggestions": suggestions}
