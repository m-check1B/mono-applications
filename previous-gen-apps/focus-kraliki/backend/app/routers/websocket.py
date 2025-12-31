from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set, Optional
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from app.core.security import decode_token, get_current_user
from app.core.database import SessionLocal
from app.models.user import User, Role

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        # user_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new websocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a websocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.debug(f"Failed to send websocket message to user {user_id}: {e}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()


async def _authenticate_websocket(websocket: WebSocket) -> Optional[User]:
    """Validate JWT passed via query param or Authorization header."""
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return None

    try:
        payload = decode_token(token)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid authentication token")
        return None

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid authentication token")
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

    if not user:
        await websocket.close(code=1008, reason="User not found")
        return None

    return user


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time updates

    Message format:
    {
        "type": "task_update" | "notification" | "ping" | "chat_message",
        "data": {...},
        "timestamp": "ISO timestamp"
    }
    """
    current_user = await _authenticate_websocket(websocket)
    if not current_user:
        return
    if current_user.id != user_id:
        await websocket.close(code=1008, reason="Cannot subscribe to another user")
        return

    await manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif message_data.get("type") == "subscribe":
                # User subscribing to specific events
                await websocket.send_json({
                    "type": "subscribed",
                    "events": message_data.get("events", []),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Echo back for now (can be extended)
                await websocket.send_json({
                    "type": "echo",
                    "data": message_data,
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


@router.post("/ws/broadcast/{user_id}")
async def send_update_to_user(
    user_id: str,
    message: dict,
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint to send updates to a user's websocket connections
    This can be called from other parts of the application
    """
    if current_user.id != user_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to broadcast to this user")

    await manager.send_personal_message(message, user_id)
    return {"success": True, "user_id": user_id}


# Helper function to notify users of updates
async def notify_task_update(user_id: str, task_data: dict):
    """Notify user of task updates via WebSocket"""
    await manager.send_personal_message({
        "type": "task_update",
        "data": task_data,
        "timestamp": datetime.utcnow().isoformat()
    }, user_id)


async def notify_new_message(user_id: str, message_data: dict):
    """Notify user of new chat messages via WebSocket"""
    await manager.send_personal_message({
        "type": "chat_message",
        "data": message_data,
        "timestamp": datetime.utcnow().isoformat()
    }, user_id)

# ========== Event Bus Integration (Gap #7) ==========

from app.core.event_bus import get_event_bus

async def handle_backend_event(event: dict):
    """
    Forward backend events to WebSocket clients
    Part of Gap #7: Event bus notifications
    """
    user_id = event.get("user_id")
    if not user_id:
        return
    
    # Forward event to WebSocket client
    await manager.send_personal_message({
        "type": event.get("type", "notification"),
        "data": event.get("data"),
        "timestamp": event.get("timestamp")
    }, user_id)

# Subscribe to event types
event_bus = get_event_bus()
event_bus.subscribe("item_created", handle_backend_event)
event_bus.subscribe("item_updated", handle_backend_event)
event_bus.subscribe("item_deleted", handle_backend_event)
event_bus.subscribe("task_update", handle_backend_event)
event_bus.subscribe("task_created", handle_backend_event)
event_bus.subscribe("task_updated", handle_backend_event)
event_bus.subscribe("task_completed", handle_backend_event)
event_bus.subscribe("notification", handle_backend_event)

# Export event bus for use in other modules
__all__ = ["router", "manager", "notify_task_update", "notify_new_message", "event_bus"]
