from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db, SessionLocal
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.item_type import ItemType
from app.models.knowledge_item import KnowledgeItem
from app.schemas.knowledge import (
    ItemTypeCreate,
    ItemTypeUpdate,
    ItemTypeResponse,
    ItemTypeListResponse,
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
    KnowledgeItemListResponse,
)
from app.services.knowledge_defaults import ensure_default_item_types
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# ========== Background Tasks for File Search Integration ==========


def _index_knowledge_item_background(user_id: str, item_id: str):
    """
    Background task to index knowledge item for semantic search (VD-340).
    Runs alongside Gemini File Search import.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from app.services.semantic_search import get_semantic_search_service

            search_service = get_semantic_search_service(db, user)
            search_service.index_entity("knowledge_item", item_id)
            logger.debug(f"Indexed knowledge item {item_id} for semantic search")
    except Exception as e:
        logger.warning(f"Failed to index knowledge item {item_id}: {e}")
    finally:
        db.close()


def _delete_knowledge_item_index_background(user_id: str, item_id: str):
    """Background task to remove knowledge item from search index"""
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            from app.services.semantic_search import get_semantic_search_service

            search_service = get_semantic_search_service(db, user)
            search_service.delete_index("knowledge_item", item_id)
            logger.debug(f"Removed knowledge item {item_id} from search index")
    except Exception as e:
        logger.warning(f"Failed to remove knowledge item {item_id} from index: {e}")
    finally:
        db.close()


async def import_knowledge_item_background(user_id: str, item_id: str):
    """
    Background task to import knowledge item to Gemini File Search.

    This runs asynchronously after item creation/update to avoid blocking
    the API response. Gracefully handles Gemini unavailability.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        item = (
            db.query(KnowledgeItem)
            .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == user_id)
            .first()
        )

        if not user or not item:
            logger.warning("Skipping File Search import - user or item not found")
            return

        from app.services.gemini_file_search import import_knowledge_item

        result = await import_knowledge_item(db, user, item)
        if result:
            logger.info(
                f"Successfully imported knowledge item {item.id} to File Search as {result}"
            )
        else:
            logger.warning(
                f"Failed to import knowledge item {item.id} - Gemini unavailable or error occurred"
            )
    except ImportError:
        logger.debug("Gemini File Search service not available - skipping import")
    except Exception as e:
        logger.error(
            f"Error importing knowledge item {item_id} to File Search: {e}",
            exc_info=True,
        )
    finally:
        db.close()


async def update_knowledge_item_background(user_id: str, item_id: str):
    """
    Background task to re-import updated knowledge item to Gemini File Search.

    This is called when content changes to keep the File Search index in sync.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        item = (
            db.query(KnowledgeItem)
            .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == user_id)
            .first()
        )

        if not user or not item:
            logger.warning("Skipping File Search re-import - user or item not found")
            return

        from app.services.gemini_file_search import import_knowledge_item

        result = await import_knowledge_item(db, user, item)
        if result:
            logger.info(
                f"Successfully re-imported knowledge item {item.id} to File Search after update"
            )
        else:
            logger.warning(
                f"Failed to re-import knowledge item {item.id} - Gemini unavailable or error occurred"
            )
    except ImportError:
        logger.debug("Gemini File Search service not available - skipping re-import")
    except Exception as e:
        logger.error(
            f"Error re-importing knowledge item {item_id} to File Search: {e}",
            exc_info=True,
        )
    finally:
        db.close()


# ========== Item Type Endpoints ==========


@router.get("/item-types", response_model=ItemTypeListResponse)
async def list_item_types(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all item types for the current user"""
    # Ensure default types exist on first access (guarded call)
    ensure_default_item_types(current_user.id, db)

    query = db.query(ItemType).filter(ItemType.userId == current_user.id)
    total = query.count()
    item_types = query.offset(offset).limit(limit).all()

    return ItemTypeListResponse(
        itemTypes=[ItemTypeResponse.model_validate(it) for it in item_types],
        total=total,
    )


@router.post("/item-types", response_model=ItemTypeResponse)
async def create_item_type(
    item_type_data: ItemTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new item type"""
    item_type = ItemType(
        id=generate_id(), userId=current_user.id, **item_type_data.model_dump()
    )

    db.add(item_type)
    db.commit()
    db.refresh(item_type)

    return ItemTypeResponse.model_validate(item_type)


@router.get("/item-types/{type_id}", response_model=ItemTypeResponse)
async def get_item_type(
    type_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific item type"""
    item_type = (
        db.query(ItemType)
        .filter(ItemType.id == type_id, ItemType.userId == current_user.id)
        .first()
    )

    if not item_type:
        raise HTTPException(status_code=404, detail="Item type not found")

    return ItemTypeResponse.model_validate(item_type)


@router.patch("/item-types/{type_id}", response_model=ItemTypeResponse)
async def update_item_type(
    type_id: str,
    item_type_update: ItemTypeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an item type"""
    item_type = (
        db.query(ItemType)
        .filter(ItemType.id == type_id, ItemType.userId == current_user.id)
        .first()
    )

    if not item_type:
        raise HTTPException(status_code=404, detail="Item type not found")

    update_data = item_type_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item_type, key, value)

    db.commit()
    db.refresh(item_type)

    return ItemTypeResponse.model_validate(item_type)


@router.delete("/item-types/{type_id}")
async def delete_item_type(
    type_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an item type (cascade deletes associated knowledge items)"""
    item_type = (
        db.query(ItemType)
        .filter(ItemType.id == type_id, ItemType.userId == current_user.id)
        .first()
    )

    if not item_type:
        raise HTTPException(status_code=404, detail="Item type not found")

    db.delete(item_type)
    db.commit()

    return {"success": True, "deletedId": type_id}


# ========== Knowledge Item Endpoints ==========


@router.get("/items", response_model=KnowledgeItemListResponse)
async def list_knowledge_items(
    typeId: Optional[str] = None,
    completed: Optional[bool] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all knowledge items for the current user, optionally filtered by type"""
    query = db.query(KnowledgeItem).filter(KnowledgeItem.userId == current_user.id)

    if typeId:
        query = query.filter(KnowledgeItem.typeId == typeId)
    if completed is not None:
        query = query.filter(KnowledgeItem.completed == completed)

    total = query.count()
    items = (
        query.order_by(KnowledgeItem.createdAt.desc()).offset(offset).limit(limit).all()
    )

    return KnowledgeItemListResponse(
        items=[KnowledgeItemResponse.model_validate(item) for item in items],
        total=total,
    )


@router.post("/items", response_model=KnowledgeItemResponse)
async def create_knowledge_item(
    item_data: KnowledgeItemCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new knowledge item"""
    # Verify the typeId belongs to the user
    item_type = (
        db.query(ItemType)
        .filter(ItemType.id == item_data.typeId, ItemType.userId == current_user.id)
        .first()
    )

    if not item_type:
        raise HTTPException(status_code=404, detail="Item type not found")

    knowledge_item = KnowledgeItem(
        id=generate_id(),
        userId=current_user.id,
        **item_data.model_dump(exclude={"content"}),
        content=item_data.content or "",
    )

    db.add(knowledge_item)
    db.commit()
    db.refresh(knowledge_item)

    # Schedule background import to File Search
    logger.debug(
        f"Scheduling File Search import for knowledge item {knowledge_item.id}"
    )
    background_tasks.add_task(
        import_knowledge_item_background, current_user.id, knowledge_item.id
    )

    # Index for semantic search (VD-340)
    background_tasks.add_task(
        _index_knowledge_item_background, current_user.id, knowledge_item.id
    )

    return KnowledgeItemResponse.model_validate(knowledge_item)


@router.get("/items/{item_id}", response_model=KnowledgeItemResponse)
async def get_knowledge_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific knowledge item"""
    knowledge_item = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == current_user.id)
        .first()
    )

    if not knowledge_item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    return KnowledgeItemResponse.model_validate(knowledge_item)


@router.patch("/items/{item_id}", response_model=KnowledgeItemResponse)
async def update_knowledge_item(
    item_id: str,
    item_update: KnowledgeItemUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a knowledge item"""
    knowledge_item = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == current_user.id)
        .first()
    )

    if not knowledge_item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    # If typeId is being updated, verify it belongs to the user
    update_data = item_update.model_dump(exclude_unset=True)
    if "typeId" in update_data:
        item_type = (
            db.query(ItemType)
            .filter(
                ItemType.id == update_data["typeId"], ItemType.userId == current_user.id
            )
            .first()
        )
        if not item_type:
            raise HTTPException(status_code=404, detail="Item type not found")

    # Track if content was updated (needs re-import)
    content_updated = "content" in update_data or "title" in update_data

    for key, value in update_data.items():
        if key == "content" and value is None:
            value = ""
        setattr(knowledge_item, key, value)

    db.commit()
    db.refresh(knowledge_item)

    # Re-import to File Search if content changed
    if content_updated:
        logger.debug(
            f"Scheduling File Search re-import for updated knowledge item {knowledge_item.id}"
        )
        background_tasks.add_task(
            update_knowledge_item_background, current_user.id, knowledge_item.id
        )

    # Re-index for semantic search (VD-340)
    background_tasks.add_task(
        _index_knowledge_item_background, current_user.id, knowledge_item.id
    )

    return KnowledgeItemResponse.model_validate(knowledge_item)


@router.delete("/items/{item_id}")
async def delete_knowledge_item(
    item_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a knowledge item"""
    knowledge_item = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == current_user.id)
        .first()
    )

    if not knowledge_item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    item_id_copy = knowledge_item.id  # Copy before deletion
    db.delete(knowledge_item)
    db.commit()

    # Remove from search index (VD-340)
    background_tasks.add_task(
        _delete_knowledge_item_index_background, current_user.id, item_id_copy
    )

    return {"success": True, "deletedId": item_id}


@router.post("/items/{item_id}/toggle", response_model=KnowledgeItemResponse)
async def toggle_knowledge_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle the completed status of a knowledge item"""
    knowledge_item = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.id == item_id, KnowledgeItem.userId == current_user.id)
        .first()
    )

    if not knowledge_item:
        raise HTTPException(status_code=404, detail="Knowledge item not found")

    knowledge_item.completed = not knowledge_item.completed

    db.commit()
    db.refresh(knowledge_item)

    return KnowledgeItemResponse.model_validate(knowledge_item)


@router.get("/search")
async def search_knowledge_items(
    query: str,
    typeId: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search knowledge items by title or content"""
    db_query = db.query(KnowledgeItem).filter(
        KnowledgeItem.userId == current_user.id,
        (KnowledgeItem.title.ilike(f"%{query}%"))
        | (KnowledgeItem.content.ilike(f"%{query}%")),
    )

    if typeId:
        db_query = db_query.filter(KnowledgeItem.typeId == typeId)

    total = db_query.count()
    items = db_query.offset(offset).limit(limit).all()

    return {
        "items": [KnowledgeItemResponse.model_validate(item) for item in items],
        "total": total,
        "query": query,
        "offset": offset,
        "limit": limit,
    }
