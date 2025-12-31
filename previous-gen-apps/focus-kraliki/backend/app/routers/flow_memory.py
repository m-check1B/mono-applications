"""
Flow Memory API Endpoints
Provides conversational memory and context management
"""

from fastapi import APIRouter, Depends, HTTPException
import redis.asyncio as aioredis
from typing import Optional

from app.core.security import get_current_user
from app.models.user import User
from app.services.flow_memory import FlowMemoryService
from app.schemas.flow_memory import (
    InteractionCreate,
    StoreResponse,
    MemoryRetrievalRequest,
    MemoryResponse,
    SessionResponse,
    ContextSummaryCreate,
    ContextSummaryResponse,
    MemoryStatsResponse,
    ClearMemoryResponse,
    BulkInteractionCreate,
    InteractionResponse,
    MemoryPatterns
)
from app.core.config import settings

router = APIRouter(prefix="/flow-memory", tags=["flow-memory"])

# Redis client instance
_redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client


async def close_redis_client() -> None:
    """Close the shared Redis client to avoid leaking connections."""
    global _redis_client
    if _redis_client is None:
        return
    await _redis_client.close()
    if hasattr(_redis_client, "connection_pool"):
        await _redis_client.connection_pool.disconnect()
    _redis_client = None


async def get_flow_memory_service(
    redis_client: aioredis.Redis = Depends(get_redis_client)
) -> FlowMemoryService:
    """Dependency to get Flow Memory Service"""
    return FlowMemoryService(redis_client)


@router.post("/interactions", response_model=StoreResponse)
async def store_interaction(
    interaction: InteractionCreate,
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Store a new interaction in user's conversational memory

    This endpoint saves user messages and AI responses for context continuity.
    Automatically extracts patterns and maintains rolling window of interactions.
    """
    try:
        interaction_dict = {
            "user_message": interaction.user_message,
            "ai_response": interaction.ai_response,
            "context": interaction.context,
            "metadata": interaction.metadata
        }

        success = await flow_service.store_interaction(
            user_id=current_user.id,
            interaction=interaction_dict,
            session_id=interaction.session_id
        )

        return StoreResponse(
            success=success,
            message="Interaction stored successfully",
            interactions_stored=1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store interaction: {str(e)}")


@router.post("/interactions/bulk", response_model=StoreResponse)
async def store_bulk_interactions(
    bulk_request: BulkInteractionCreate,
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Store multiple interactions at once

    Useful for importing conversation history or batch updates.
    """
    try:
        stored_count = 0
        for interaction in bulk_request.interactions:
            interaction_dict = {
                "user_message": interaction.user_message,
                "ai_response": interaction.ai_response,
                "context": interaction.context,
                "metadata": interaction.metadata
            }

            success = await flow_service.store_interaction(
                user_id=current_user.id,
                interaction=interaction_dict,
                session_id=interaction.session_id
            )

            if success:
                stored_count += 1

        return StoreResponse(
            success=True,
            message=f"Stored {stored_count} interactions",
            interactions_stored=stored_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store interactions: {str(e)}")


@router.post("/retrieve", response_model=MemoryResponse)
async def retrieve_memory(
    retrieval_request: MemoryRetrievalRequest,
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Retrieve user's conversational memory

    Supports semantic filtering via query parameter and returns:
    - Recent interactions
    - Extracted patterns
    - Context summary
    """
    try:
        memory_data = await flow_service.retrieve_context(
            user_id=current_user.id,
            query=retrieval_request.query,
            limit=retrieval_request.limit
        )

        # Convert to response format
        interactions = [
            InteractionResponse(**interaction)
            for interaction in memory_data.get("interactions", [])
        ]

        patterns = MemoryPatterns(**memory_data.get("patterns", {}))

        return MemoryResponse(
            interactions=interactions,
            patterns=patterns,
            insights=memory_data.get("insights", []),
            context_summary=memory_data.get("context_summary"),
            total_count=len(interactions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {str(e)}")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Retrieve a specific session's data

    Sessions are temporary (24h TTL) conversation threads.
    """
    try:
        session_data = await flow_service.get_session(current_user.id, session_id)

        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        interactions = [
            InteractionResponse(**interaction)
            for interaction in session_data.get("interactions", [])
        ]

        return SessionResponse(
            session_id=session_data["session_id"],
            started_at=session_data["started_at"],
            last_activity=session_data["last_activity"],
            interactions=interactions,
            interaction_count=len(interactions)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@router.post("/context/compress", response_model=ContextSummaryResponse)
async def compress_context(
    summary_request: ContextSummaryCreate,
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Store a compressed summary of user's context

    Used to maintain long-term context without storing all interactions.
    Typically generated by AI from recent conversation history.
    """
    try:
        success = await flow_service.compress_and_store_context(
            user_id=current_user.id,
            summary=summary_request.summary
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store context")

        from datetime import datetime
        return ContextSummaryResponse(
            summary=summary_request.summary,
            created_at=datetime.utcnow().isoformat(),
            version=1
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compress context: {str(e)}")


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Get statistics about user's memory

    Returns metrics like total interactions, top topics, and patterns detected.
    """
    try:
        stats = await flow_service.get_memory_stats(current_user.id)
        return MemoryStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/clear", response_model=ClearMemoryResponse)
async def clear_memory(
    current_user: User = Depends(get_current_user),
    flow_service: FlowMemoryService = Depends(get_flow_memory_service)
):
    """
    Clear all memory for the current user

    WARNING: This permanently deletes all interactions, patterns, and context.
    This action cannot be undone.
    """
    try:
        success = await flow_service.clear_memory(current_user.id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear memory")

        return ClearMemoryResponse(
            success=True,
            message="All memory cleared successfully",
            cleared_items={
                "interactions": "all",
                "patterns": "all",
                "sessions": "all",
                "context": "cleared"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check(
    redis_client: aioredis.Redis = Depends(get_redis_client)
):
    """Check Redis connection health"""
    try:
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": "disconnected", "error": str(e)}
