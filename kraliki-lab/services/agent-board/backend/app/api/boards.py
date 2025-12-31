from fastapi import APIRouter, HTTPException
from typing import List
from ..models.board import Board
from ..services.board_manager import BoardManager
import os

router = APIRouter(prefix="/api/boards", tags=["boards"])

# Initialize board manager
BOARDS_PATH = os.getenv("BOARDS_PATH", "./boards")
board_manager = BoardManager(boards_path=BOARDS_PATH)

@router.get("/", response_model=List[Board])
async def get_boards():
    """Get all boards with stats"""
    try:
        return board_manager.get_boards()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving boards: {str(e)}")

@router.get("/{board_id}", response_model=Board)
async def get_board(board_id: str):
    """Get a specific board"""
    try:
        board = board_manager.get_board(board_id)
        if not board:
            raise HTTPException(status_code=404, detail=f"Board not found: {board_id}")
        return board
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving board: {str(e)}")
