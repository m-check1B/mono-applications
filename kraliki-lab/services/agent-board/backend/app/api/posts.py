from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.post import Post, PostCreate, PostResponse
from ..services.board_manager import BoardManager
import os

router = APIRouter(prefix="/api/posts", tags=["posts"])

# Initialize board manager
BOARDS_PATH = os.getenv("BOARDS_PATH", "./boards")
board_manager = BoardManager(boards_path=BOARDS_PATH)

@router.post("/{board_id}", response_model=Post)
async def create_post(board_id: str, post_data: PostCreate):
    """Create a new post on a board"""
    try:
        return board_manager.create_post(board_id, post_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating post: {str(e)}")

@router.get("/{board_id}", response_model=PostResponse)
async def get_posts(
    board_id: str,
    content_type: Optional[str] = Query(None, description="Filter by content type (updates/journal)"),
    limit: int = Query(50, ge=1, le=200)
):
    """Get posts from a board"""
    try:
        posts = board_manager.get_posts(board_id, content_type=content_type, limit=limit)
        return PostResponse(
            posts=posts,
            count=len(posts),
            board_id=board_id,
            content_type=content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving posts: {str(e)}")

@router.get("/", response_model=PostResponse)
async def get_recent_posts(limit: int = Query(20, ge=1, le=100)):
    """Get recent posts from all boards"""
    try:
        posts = board_manager.get_recent_posts(limit=limit)
        return PostResponse(
            posts=posts,
            count=len(posts),
            board_id="all"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recent posts: {str(e)}")
