"""
Chat API endpoints for browser-based conversations
"""

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Import AI chat service
from app.auth.jwt_auth import get_current_user
from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    WRITE_OPERATION_RATE_LIMIT,
    limiter,
)
from app.models.user import User
from app.services.chat_ai_service import get_chat_service

# Context sharing imports
from app.services.context_sharing import (
    ChannelType,
    ContextEvent,
    ContextEventType,
    context_sharing_service,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.session_connections: dict[str, list[str]] = {}  # session_id -> [connection_ids]

    async def connect(self, websocket: WebSocket, connection_id: str, session_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket

        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)

    def disconnect(self, connection_id: str, session_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        if session_id in self.session_connections:
            if connection_id in self.session_connections[session_id]:
                self.session_connections[session_id].remove(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]

    async def send_to_session(self, session_id: str, message: dict):
        if session_id in self.session_connections:
            disconnected = []
            for connection_id in self.session_connections[session_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(json.dumps(message))
                    except Exception:
                        disconnected.append(connection_id)
                else:
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                self.disconnect(connection_id, session_id)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(connection_id)

        for connection_id in disconnected:
            # Find session_id and clean up
            for session_id, connections in self.session_connections.items():
                if connection_id in connections:
                    self.disconnect(connection_id, session_id)
                    break


manager = ConnectionManager()

# In-memory storage for demo purposes
# In production, use Redis or database
chat_sessions: dict[str, dict] = {}
chat_messages: dict[str, list[dict]] = {}


def _parse_timestamp(value: Any | None) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _calculate_unread_count(session_id: str, last_read_at: datetime | None) -> int:
    messages = chat_messages.get(session_id, [])
    if not last_read_at:
        return len(messages)
    unread_count = 0
    for msg in messages:
        msg_timestamp = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
        if msg_timestamp > last_read_at:
            unread_count += 1
    return unread_count


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    metadata: dict[str, Any] | None = None


class CreateSessionRequest(BaseModel):
    user_id: str
    company_id: str
    context: dict[str, Any] | None = None


class SendMessageRequest(BaseModel):
    session_id: str
    message: ChatMessage


class SessionUpdateRequest(BaseModel):
    session_id: str
    context: dict[str, Any]


@router.post("/sessions")
async def create_session(
    request: CreateSessionRequest, current_user: User = Depends(get_current_user)
):
    """Create a new chat session"""
    session_id = str(uuid.uuid4())

    session = {
        "id": session_id,
        "user_id": request.user_id,
        "company_id": request.company_id,
        "status": "active",
        "created_at": datetime.now(UTC),
        "last_activity": datetime.now(UTC),
        "context": request.context or {},
        "provider": "gemini",  # Default provider
        "customer_info": {},
    }

    chat_sessions[session_id] = session
    chat_messages[session_id] = []

    # Create shared context
    shared_context = context_sharing_service.create_shared_context(
        session_id=session_id,
        channel=ChannelType.BROWSER,
        channel_session_id=session_id,
        customer_info=request.context.get("customer_info") if request.context else None,
    )
    session["shared_context_id"] = shared_context.session_id
    session["last_read_at"] = datetime.now(UTC)

    return {
        "session_id": session_id,
        "status": "created",
        "created_at": session["created_at"].isoformat(),
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Get session details"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]
    messages = chat_messages.get(session_id, [])

    last_read_at = _parse_timestamp(session.get("last_read_at")) or session.get("created_at")
    session["unread_count"] = _calculate_unread_count(session_id, last_read_at)
    session["last_read_at"] = datetime.now(UTC)

    return {"session": session, "messages": messages, "message_count": len(messages)}


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List chat sessions"""
    sessions = list(chat_sessions.values())

    # Filter by status if provided
    if status:
        sessions = [s for s in sessions if s.get("status") == status]

    # Sort by last activity
    sessions.sort(key=lambda x: x.get("last_activity", datetime.min), reverse=True)

    # Apply pagination
    total = len(sessions)
    sessions = sessions[offset : offset + limit]

    # Add message counts and last message
    for session in sessions:
        session_id = session["id"]
        messages = chat_messages.get(session_id, [])
        session["message_count"] = len(messages)

        # Calculate unread messages (messages after last_read_at)
        last_read_at = _parse_timestamp(session.get("last_read_at")) or session.get("created_at")
        session["unread_count"] = _calculate_unread_count(session_id, last_read_at)

        if messages:
            session["last_message"] = messages[-1]["content"]
        else:
            session["last_message"] = ""

    return {"sessions": sessions, "total": total, "limit": limit, "offset": offset}


@router.post("/sessions/{session_id}/read")
async def mark_session_read(session_id: str, current_user: User = Depends(get_current_user)):
    """Mark a session as read for the current user."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.now(UTC)
    chat_sessions[session_id]["last_read_at"] = now
    chat_sessions[session_id]["last_activity"] = now

    return {
        "session_id": session_id,
        "last_read_at": now.isoformat(),
        "unread_count": _calculate_unread_count(session_id, now),
    }


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.post("/messages")
async def send_message(request: Request, message_data: SendMessageRequest):
    """Send a message to a chat session"""
    session_id = message_data.session_id

    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create message
    message = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "role": message_data.message.role,
        "content": message_data.message.content,
        "timestamp": datetime.now(UTC).isoformat(),
        "metadata": message_data.message.metadata or {},
    }

    # Store message
    if session_id not in chat_messages:
        chat_messages[session_id] = []
    chat_messages[session_id].append(message)

    # Update session activity
    now = datetime.now(UTC)
    chat_sessions[session_id]["last_activity"] = now
    chat_sessions[session_id]["last_read_at"] = now

    # Add context sharing event for message sent
    context_sharing_service.add_event(
        session_id,
        ContextEvent(
            event_type=ContextEventType.MESSAGE_SENT,
            channel=ChannelType.BROWSER,
            session_id=session_id,
            data={
                "role": message_data.message.role,
                "content": message_data.message.content,
                "metadata": message_data.message.metadata,
            },
        ),
    )

    # Broadcast to all connections in this session
    await manager.send_to_session(
        session_id,
        {
            "type": "message",
            "session_id": session_id,
            "role": message_data.message.role,
            "content": message_data.message.content,
            "metadata": message_data.message.metadata,
            "timestamp": message["timestamp"],
        },
    )

    # If it's a user message, generate AI response
    if message_data.message.role == MessageRole.USER:
        await asyncio.create_task(generate_ai_response(session_id, message_data.message.content))

    return {"message_id": message["id"], "timestamp": message["timestamp"], "status": "sent"}


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """Get messages for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = chat_messages.get(session_id, [])

    # Sort by timestamp (ascending)
    messages.sort(key=lambda x: x.get("timestamp", ""))

    # Apply pagination
    total = len(messages)
    messages = messages[offset : offset + limit]

    return {"messages": messages, "total": total, "limit": limit, "offset": offset}


@router.put("/sessions/{session_id}/context")
async def update_session_context(
    session_id: str, request: SessionUpdateRequest, current_user: User = Depends(get_current_user)
):
    """Update session context"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update context
    chat_sessions[session_id]["context"].update(request.context)
    chat_sessions[session_id]["last_activity"] = datetime.now(UTC)

    # Update context sharing service if customer info is updated
    if "customer_info" in request.context:
        context_sharing_service.update_customer_info(session_id, request.context["customer_info"])

    # Broadcast context update
    await manager.send_to_session(
        session_id,
        {
            "type": "session_update",
            "session_id": session_id,
            "context": chat_sessions[session_id]["context"],
        },
    )

    return {"status": "updated", "context": chat_sessions[session_id]["context"]}


@router.delete("/sessions/{session_id}")
async def end_session(session_id: str, current_user: User = Depends(get_current_user)):
    """End a chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_sessions[session_id]["status"] = "ended"
    chat_sessions[session_id]["ended_at"] = datetime.now(UTC)

    # Add context sharing session end event
    context_sharing_service.end_session(session_id)

    # Broadcast session end
    await manager.send_to_session(
        session_id,
        {
            "type": "session_ended",
            "session_id": session_id,
            "ended_at": chat_sessions[session_id]["ended_at"].isoformat(),
        },
    )

    return {"status": "ended", "ended_at": chat_sessions[session_id]["ended_at"].isoformat()}


# Context sharing endpoints
@router.post("/sessions/{session_id}/link-voice")
async def link_voice_session(
    session_id: str, voice_session_id: str, current_user: User = Depends(get_current_user)
):
    """Link a voice session to a browser chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Implement context sharing link
    context = context_sharing_service.link_channels(
        shared_session_id=session_id, channel=ChannelType.VOICE, channel_session_id=voice_session_id
    )

    if not context:
        raise HTTPException(status_code=400, detail="Failed to link sessions")

    return {"status": "linked", "chat_session_id": session_id, "voice_session_id": voice_session_id}


@router.get("/sessions/{session_id}/context")
async def get_shared_context(session_id: str, current_user: User = Depends(get_current_user)):
    """Get shared context for a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get context from context sharing service
    context = context_sharing_service.get_context(session_id)
    if not context:
        raise HTTPException(status_code=404, detail="Shared context not found")

    # Return context from sharing service
    messages = chat_messages.get(session_id, [])

    return {
        "session_id": session_id,
        "customer_info": context.customer_info,
        "conversation_summary": context.conversation_summary
        or [
            {
                "timestamp": msg["timestamp"],
                "channel": "browser",
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
            }
            for msg in messages[-20:]  # Last 20 messages
        ],
        "current_intent": context.get_current_intent(),
        "current_sentiment": context.get_current_sentiment(),
        "provider_history": context.provider_history,
        "workflows": context.workflows,
    }


@router.post("/sessions/{session_id}/context/customer-info")
async def update_customer_info(
    session_id: str, customer_info: dict[str, Any], current_user: User = Depends(get_current_user)
):
    """Update customer information in shared context"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update session customer info
    chat_sessions[session_id]["customer_info"].update(customer_info)
    chat_sessions[session_id]["last_activity"] = datetime.now(UTC)

    # Update context sharing service
    success = context_sharing_service.update_customer_info(session_id, customer_info)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update customer info")

    return {"status": "updated", "customer_info": chat_sessions[session_id]["customer_info"]}


@limiter.limit(API_RATE_LIMIT)
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    connection_id = str(uuid.uuid4())
    session_id = None

    try:
        # Wait for initial message with session info
        data = await websocket.receive_text()
        message = json.loads(data)

        if message.get("type") == "join":
            session_id = message.get("session_id")
            if not session_id:
                await websocket.close(code=4000, reason="Session ID required")
                return

            # Validate session exists
            if session_id not in chat_sessions:
                await websocket.close(code=4004, reason="Session not found")
                return

            # Add connection
            await manager.connect(websocket, connection_id, session_id)

            # Mark session as read
            now = datetime.now(UTC)
            chat_sessions[session_id]["last_read_at"] = now
            chat_sessions[session_id]["last_activity"] = now

            # Send confirmation
            await websocket.send_text(
                json.dumps(
                    {"type": "connected", "connection_id": connection_id, "session_id": session_id}
                )
            )

            # Send hydration data from context sharing
            hydration_data = context_sharing_service.get_hydration_data(session_id)
            if hydration_data:
                await websocket.send_text(
                    json.dumps(
                        {"type": "hydration", "session_id": session_id, "data": hydration_data}
                    )
                )

            # Send recent messages
            messages = chat_messages.get(session_id, [])
            for msg in messages[-10:]:  # Last 10 messages
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "message",
                            "session_id": session_id,
                            "role": msg["role"],
                            "content": msg["content"],
                            "metadata": msg.get("metadata", {}),
                            "timestamp": msg["timestamp"],
                        }
                    )
                )

        # Handle ongoing messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "message":
                # Handle message through regular API
                await send_message(
                    SendMessageRequest(
                        session_id=session_id or "",
                        message=ChatMessage(
                            role=message.get("role", "user"),
                            content=message.get("content", ""),
                            metadata=message.get("metadata"),
                        ),
                    )
                )
            elif message.get("type") == "typing":
                # Broadcast typing indicator
                if session_id:
                    await manager.send_to_session(
                        session_id,
                        {
                            "type": "typing",
                            "session_id": session_id,
                            "is_typing": message.get("is_typing", False),
                        },
                    )

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error("WebSocket error: %s", e)
    finally:
        if session_id:
            manager.disconnect(connection_id, session_id)


async def generate_ai_response(session_id: str | None, user_message: str):
    """Generate AI response for user message"""
    try:
        if not session_id:
            return

        chat_service = get_chat_service()

        # Get conversation history for context from shared context service if available
        # This allows incorporating history from other channels (e.g. voice)
        conversation_history = []
        context = context_sharing_service.get_context_by_channel(session_id)

        if context:
            shared_history = context.get_conversation_history()
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in shared_history[-15:]  # Use last 15 messages for more context
            ]
        elif session_id in chat_messages:
            # Fallback to local chat messages
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in chat_messages[session_id][-10:]
            ]

        # Add current user message if not already in history (it should be if it was added as an event)
        if not conversation_history or conversation_history[-1]["content"] != user_message:
            conversation_history.append({"role": "user", "content": user_message})

        # Get session for context
        session = chat_sessions.get(session_id, {})
        system_prompt = session.get(
            "system_prompt", "You are a helpful AI assistant for customer support."
        )

        # Add system prompt to history
        full_messages = [{"role": "system", "content": system_prompt}] + conversation_history

        # Generate AI response
        ai_result = await chat_service.generate_response(
            messages=full_messages,
            provider=session.get("provider"),
            temperature=0.7,
            max_tokens=500,
        )

        # Analyze intent and sentiment
        intent_sentiment = await chat_service.analyze_intent_and_sentiment(user_message)

        ai_response = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": "assistant",
            "content": ai_result["content"],
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": {
                "provider": ai_result.get("provider", "unknown"),
                "model": ai_result.get("model", "unknown"),
                "intent": intent_sentiment["intent"],
                "sentiment": intent_sentiment["sentiment"],
                "confidence": intent_sentiment["confidence"],
                "usage": ai_result.get("usage"),
            },
        }

        # Store AI response
        if session_id not in chat_messages:
            chat_messages[session_id] = []
        chat_messages[session_id].append(ai_response)

        # Update session activity
        if session_id in chat_sessions:
            chat_sessions[session_id]["last_activity"] = datetime.now(UTC)

        # Add context sharing event for AI response
        context_sharing_service.add_event(
            session_id,
            ContextEvent(
                event_type=ContextEventType.MESSAGE_SENT,
                channel=ChannelType.BROWSER,
                session_id=session_id,
                data={
                    "role": "assistant",
                    "content": ai_response["content"],
                    "metadata": ai_response["metadata"],
                },
            ),
        )

        # Add context sharing events for intent and sentiment
        context_sharing_service.add_event(
            session_id,
            ContextEvent(
                event_type=ContextEventType.INTENT_DETECTED,
                channel=ChannelType.BROWSER,
                session_id=session_id,
                data={
                    "intent": intent_sentiment["intent"],
                    "confidence": intent_sentiment["confidence"],
                    "provider": ai_result.get("provider"),
                },
            ),
        )
        context_sharing_service.add_event(
            session_id,
            ContextEvent(
                event_type=ContextEventType.SENTIMENT_ANALYZED,
                channel=ChannelType.BROWSER,
                session_id=session_id,
                data={
                    "sentiment": intent_sentiment["sentiment"],
                    "confidence": intent_sentiment["confidence"],
                },
            ),
        )

        # Broadcast AI response
        await manager.send_to_session(
            session_id,
            {
                "type": "message",
                "session_id": session_id,
                "role": "assistant",
                "content": ai_response["content"],
                "metadata": ai_response["metadata"],
                "timestamp": ai_response["timestamp"],
            },
        )

    except Exception as e:
        logger.error("Error generating AI response: %s", e)

        # Send error message
        if session_id:
            error_response = {
                "type": "error",
                "session_id": session_id,
                "error": "Failed to generate AI response",
            }
            await manager.send_to_session(session_id, error_response)
