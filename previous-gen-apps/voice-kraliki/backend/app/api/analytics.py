"""Analytics API

REST API endpoints for analytics and metrics tracking:
- Call tracking (start, update, end)
- Analytics summaries and aggregations
- Agent and provider performance metrics
- Real-time metrics and active calls
"""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.middleware.rate_limit import API_RATE_LIMIT, WRITE_OPERATION_RATE_LIMIT, limiter
from app.services.analytics_service import (
    AnalyticsSummary,
    CallMetric,
    CallOutcome,
    get_analytics_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


# Request Models


class StartCallTrackingRequest(BaseModel):
    """Request to start tracking a call."""

    call_id: UUID
    session_id: UUID
    provider_id: str
    agent_id: str | None = None


class UpdateCallMetricRequest(BaseModel):
    """Request to update call metrics."""

    call_id: UUID
    # Quality metrics
    average_sentiment: float | None = None
    transcription_accuracy: float | None = None
    audio_quality_score: float | None = None
    # Interaction metrics
    agent_messages: int | None = None
    customer_messages: int | None = None
    ai_suggestions_used: int | None = None
    compliance_warnings: int | None = None
    # Metadata
    tags: list[str] | None = None
    notes: str | None = None


class EndCallTrackingRequest(BaseModel):
    """Request to end call tracking."""

    call_id: UUID
    outcome: CallOutcome


class GetAnalyticsSummaryRequest(BaseModel):
    """Request to get analytics summary."""

    start_time: datetime | None = None
    end_time: datetime | None = None


# Response Models


class CallTrackingResponse(BaseModel):
    """Response for call tracking operations."""

    status: str
    message: str
    call_metric: CallMetric | None = None


class AnalyticsSummaryResponse(BaseModel):
    """Response for analytics summary."""

    status: str
    summary: AnalyticsSummary


class CallMetricResponse(BaseModel):
    """Response for single call metric."""

    status: str
    metric: CallMetric | None = None


class ActiveCallsResponse(BaseModel):
    """Response for active calls list."""

    status: str
    active_calls: list[UUID]
    count: int


class CallCountsResponse(BaseModel):
    """Response for call counts."""

    status: str
    counts: dict[str, int]


# Endpoints


@router.post("/calls/start", response_model=CallTrackingResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def start_call_tracking(request: Request, request_body: StartCallTrackingRequest):
    """Start tracking a new call.

    Initializes metrics tracking for a call session, including:
    - Call timing and duration
    - Quality metrics
    - Interaction metrics
    - Agent and provider association

    Args:
        request: FastAPI request object
        request_body: Call tracking start request

    Returns:
        Initial call metric
    """
    try:
        service = get_analytics_service()
        metric = await service.start_call_tracking(
            call_id=request_body.call_id,
            session_id=request_body.session_id,
            provider_id=request_body.provider_id,
            agent_id=request_body.agent_id,
        )

        logger.info(f"Started call tracking: {request_body.call_id}")

        return CallTrackingResponse(
            status="success",
            message=f"Started tracking call {request_body.call_id}",
            call_metric=metric,
        )

    except Exception as e:
        logger.error(f"Failed to start call tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/calls/update", response_model=CallTrackingResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def update_call_metric(request: Request, request_body: UpdateCallMetricRequest):
    """Update metrics for an active call.

    Updates real-time metrics as the call progresses:
    - Quality scores (sentiment, transcription, audio)
    - Interaction counts (messages, suggestions)
    - Compliance warnings
    - Tags and notes

    Args:
        request: FastAPI request object
        request_body: Call metric update request

    Returns:
        Updated call metric
    """
    try:
        service = get_analytics_service()

        # Build updates dict from provided fields
        updates = {}
        for field, value in request_body.model_dump(exclude={"call_id"}, exclude_none=True).items():
            updates[field] = value

        metric = await service.update_call_metric(call_id=request_body.call_id, **updates)

        if not metric:
            raise HTTPException(
                status_code=404, detail=f"Call metric not found: {request_body.call_id}"
            )

        logger.info(f"Updated call metric: {request_body.call_id}")

        return CallTrackingResponse(
            status="success",
            message=f"Updated call metric {request_body.call_id}",
            call_metric=metric,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update call metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calls/end", response_model=CallTrackingResponse)
@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
async def end_call_tracking(request: Request, request_body: EndCallTrackingRequest):
    """End call tracking and finalize metrics.

    Completes call tracking with:
    - Final duration calculation
    - Outcome classification
    - Time series data update
    - Historical metrics storage

    Args:
        request: FastAPI request object
        request_body: Call tracking end request

    Returns:
        Final call metric
    """
    try:
        service = get_analytics_service()
        metric = await service.end_call_tracking(
            call_id=request_body.call_id, outcome=request_body.outcome
        )

        if not metric:
            raise HTTPException(
                status_code=404, detail=f"Call metric not found: {request_body.call_id}"
            )

        logger.info(
            f"Ended call tracking: {request_body.call_id} - Outcome: {request_body.outcome}"
        )

        return CallTrackingResponse(
            status="success",
            message=f"Ended tracking for call {request_body.call_id}",
            call_metric=metric,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end call tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=AnalyticsSummaryResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_analytics_summary(
    request: Request,
    start_time: datetime | None = Query(None, description="Start of period (ISO format)"),
    end_time: datetime | None = Query(None, description="End of period (ISO format)"),
):
    """Get aggregated analytics summary.

    Provides comprehensive analytics including:
    - Total calls and outcomes
    - Average call duration and success rate
    - Quality metrics (sentiment, audio, transcription)
    - Provider performance comparison
    - Agent performance metrics
    - Time-series data for visualization

    Args:
        start_time: Start of analysis period (default: 24 hours ago)
        end_time: End of analysis period (default: now)

    Returns:
        Comprehensive analytics summary
    """
    try:
        service = get_analytics_service()
        summary = await service.get_analytics_summary(start_time=start_time, end_time=end_time)

        logger.info(f"Retrieved analytics summary: {summary.total_calls} calls")

        return AnalyticsSummaryResponse(status="success", summary=summary)

    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/{call_id}", response_model=CallMetricResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_call_metric(request: Request, call_id: UUID):
    """Get metrics for a specific call.

    Retrieves detailed metrics for a single call:
    - Timing and duration
    - Quality scores
    - Interaction metrics
    - Outcome and notes

    Args:
        call_id: Call identifier

    Returns:
        Call metric if found
    """
    try:
        service = get_analytics_service()
        metric = service.get_call_metric(call_id)

        if not metric:
            raise HTTPException(status_code=404, detail=f"Call metric not found: {call_id}")

        return CallMetricResponse(status="success", metric=metric)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get call metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls", response_model=ActiveCallsResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_active_calls(request: Request):
    """Get list of currently active calls.

    Returns all calls that are currently in progress and being tracked.
    Useful for real-time monitoring dashboards.

    Returns:
        List of active call IDs
    """
    try:
        service = get_analytics_service()
        active_calls = service.get_active_calls()

        return ActiveCallsResponse(
            status="success", active_calls=active_calls, count=len(active_calls)
        )

    except Exception as e:
        logger.error(f"Failed to get active calls: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counts", response_model=CallCountsResponse)
@limiter.limit(API_RATE_LIMIT)
async def get_call_counts(request: Request):
    """Get call counts by status.

    Provides quick overview of:
    - Total tracked calls
    - Active calls
    - Completed calls
    - Failed calls

    Returns:
        Dictionary of call counts
    """
    try:
        service = get_analytics_service()
        counts = service.get_call_count()

        return CallCountsResponse(status="success", counts=counts)

    except Exception as e:
        logger.error(f"Failed to get call counts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
@limiter.limit(API_RATE_LIMIT)
async def get_agent_performance(
    request: Request,
    agent_id: str,
    start_time: datetime | None = Query(None, description="Start of period (ISO format)"),
    end_time: datetime | None = Query(None, description="End of period (ISO format)"),
):
    """Get performance metrics for a specific agent.

    Analyzes agent performance including:
    - Total calls handled
    - Success/failure rates
    - Average call duration
    - Customer sentiment scores
    - AI suggestions usage
    - Compliance warnings

    Args:
        agent_id: Agent identifier
        start_time: Start of analysis period (default: 24 hours ago)
        end_time: End of analysis period (default: now)

    Returns:
        Agent performance metrics
    """
    try:
        service = get_analytics_service()
        summary = await service.get_analytics_summary(start_time=start_time, end_time=end_time)

        if agent_id not in summary.agent_performance:
            raise HTTPException(status_code=404, detail=f"No metrics found for agent: {agent_id}")

        return {
            "status": "success",
            "agent_id": agent_id,
            "performance": summary.agent_performance[agent_id],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/{provider_id}")
@limiter.limit(API_RATE_LIMIT)
async def get_provider_performance(
    request: Request,
    provider_id: str,
    start_time: datetime | None = Query(None, description="Start of period (ISO format)"),
    end_time: datetime | None = Query(None, description="End of period (ISO format)"),
):
    """Get performance metrics for a specific provider.

    Analyzes provider performance including:
    - Total calls handled
    - Success/failure rates
    - Average latency
    - Audio quality scores
    - Uptime percentage
    - Error rates

    Args:
        provider_id: Provider identifier
        start_time: Start of analysis period (default: 24 hours ago)
        end_time: End of analysis period (default: now)

    Returns:
        Provider performance metrics
    """
    try:
        service = get_analytics_service()
        summary = await service.get_analytics_summary(start_time=start_time, end_time=end_time)

        if provider_id not in summary.provider_performance:
            raise HTTPException(
                status_code=404, detail=f"No metrics found for provider: {provider_id}"
            )

        return {
            "status": "success",
            "provider_id": provider_id,
            "performance": summary.provider_performance[provider_id],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provider performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/realtime")
@limiter.limit(API_RATE_LIMIT)
async def get_realtime_metrics(request: Request):
    """Get real-time metrics snapshot.

    Provides instant overview of current system state:
    - Active calls count
    - Recent call rate
    - Current average sentiment
    - Provider health status
    - Agent activity

    Returns:
        Real-time metrics snapshot
    """
    try:
        service = get_analytics_service()

        # Get current state
        active_calls = service.get_active_calls()
        counts = service.get_call_count()

        # Get recent summary (last hour)
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(hours=1)
        recent_summary = await service.get_analytics_summary(
            start_time=start_time, end_time=end_time
        )

        return {
            "status": "success",
            "timestamp": datetime.now(UTC).isoformat(),
            "active_calls": len(active_calls),
            "total_calls": counts["total"],
            "recent_calls_last_hour": recent_summary.total_calls,
            "recent_success_rate": recent_summary.success_rate,
            "recent_average_sentiment": recent_summary.average_sentiment,
            "recent_average_duration": recent_summary.average_call_duration,
        }

    except Exception as e:
        logger.error(f"Failed to get realtime metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
