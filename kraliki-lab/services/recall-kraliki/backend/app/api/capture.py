"""Capture API routes - create and manage memory items"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.storage import StorageService
from ..services.glm import GLMService

router = APIRouter(prefix="/capture", tags=["capture"])
storage = StorageService()
glm = GLMService()


class CaptureRequest(BaseModel):
    """Request model for capturing new items"""
    content: str
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    auto_categorize: bool = True
    auto_link: bool = True


class CaptureResponse(BaseModel):
    """Response model for capture"""
    id: str
    category: str
    tags: list[str]
    wikilinks: list[str]
    related_items: list[str]
    file_path: str


@router.post("/", response_model=CaptureResponse)
async def capture_item(request: CaptureRequest):
    """
    Capture a new memory item

    - Auto-categorizes if category not provided
    - Suggests tags using GLM 4.6
    - Generates wikilinks to related items
    - Finds related existing items
    """
    try:
        # Auto-categorize if needed
        if not request.category and request.auto_categorize:
            categorization = glm.categorize_content(request.content)
            category = categorization["category"]
            suggested_tags = categorization["tags"]
        else:
            category = request.category or "general"
            suggested_tags = []

        # Merge tags
        tags = list(set((request.tags or []) + suggested_tags))

        # Get all existing items for linking
        existing_items = []
        if request.auto_link:
            all_categories = ["decisions", "insights", "ideas", "learnings",
                            "customers", "competitors", "research", "sessions"]
            for cat in all_categories:
                existing_items.extend(storage.list_items(category=cat, limit=100))

        # Find related items
        related_item_ids = []
        if request.auto_link and existing_items:
            related_item_ids = glm.find_related_items(request.content, existing_items)

        # Generate item ID
        item_id = storage.generate_id(category)

        # Generate wikilinks
        wikilinks = []
        if request.auto_link:
            wikilinks = glm.generate_wikilinks(request.content, item_id)

        # Prepare metadata
        metadata = request.metadata or {}
        metadata.update({
            "tags": tags,
            "related": related_item_ids,
            "wikilinks": wikilinks
        })

        # Save item
        file_path = storage.save_item(
            category=category,
            data=metadata,
            content=request.content
        )

        return CaptureResponse(
            id=item_id,
            category=category,
            tags=tags,
            wikilinks=wikilinks,
            related_items=related_item_ids,
            file_path=file_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture item: {str(e)}")


@router.get("/{category}/{item_id}")
async def get_item(category: str, item_id: str):
    """Get a specific memory item"""
    item = storage.load_item(category, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/categories")
async def list_categories():
    """List all available categories"""
    return {
        "categories": [
            "decisions",
            "insights",
            "ideas",
            "learnings",
            "customers",
            "competitors",
            "research",
            "sessions"
        ]
    }


@router.get("/recent")
async def recent_items(limit: int = 20, category: Optional[str] = None):
    """Get recent memory items"""
    items = storage.list_items(category=category, limit=limit)
    return {"items": items, "count": len(items)}
