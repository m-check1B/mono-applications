"""Sentiment analysis router - FastAPI endpoints for sentiment analysis"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User
from app.models.call import Call
from app.models.sentiment import (
    SentimentAnalysis, RealTimeSentiment, SentimentAlert,
    SentimentType, EmotionType, TrendType
)
from app.schemas.sentiment import (
    AnalyzeSentimentRequest, BatchAnalyzeSentimentRequest,
    SentimentResult, SentimentHistoryResponse, RealTimeSentimentResponse,
    SentimentAnalyticsResponse, SentimentAlertsResponse, ServiceHealth,
    EmotionResult, TriggerResult, SentimentDistribution, TrendDistribution,
    TopEmotion, DailyAnalytics, SentimentAnalyticsSummary,
    RealTimeSentimentSnapshot
)
from app.services.sentiment_service import get_sentiment_service

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])
logger = get_logger(__name__)


@router.post("/analyze", response_model=dict, status_code=status.HTTP_200_OK)
async def analyze_sentiment(
    request: AnalyzeSentimentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment of text using AI

    **Protected**: Requires authentication
    """
    try:
        # Verify call access
        stmt = select(Call).where(
            Call.id == request.call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or access denied"
            )

        # Analyze sentiment
        sentiment_service = get_sentiment_service()
        analysis = await sentiment_service.analyze_sentiment(
            db,
            request.text,
            request.call_id,
            request.session_id,
            request.transcript_id,
            request.context
        )

        return {
            "success": True,
            "data": {
                "id": analysis.id,
                "overall": analysis.overall.value,
                "confidence": analysis.confidence,
                "intensity": analysis.intensity,
                "trend": analysis.trend.value if analysis.trend else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze sentiment"
        )


@router.post("/analyze/batch", response_model=dict, status_code=status.HTTP_200_OK)
async def batch_analyze_sentiment(
    request: BatchAnalyzeSentimentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Batch analyze multiple texts

    **Protected**: Requires authentication
    """
    try:
        # Verify all calls belong to user's organization
        call_ids = [a.call_id for a in request.analyses]
        stmt = select(Call).where(
            Call.id.in_(call_ids),
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        calls = result.scalars().all()

        if len(calls) != len(set(call_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more calls not found or access denied"
            )

        # Batch analyze
        sentiment_service = get_sentiment_service()
        results = await sentiment_service.batch_analyze_sentiment(
            db,
            [a.dict() for a in request.analyses]
        )

        return {
            "success": True,
            "data": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform batch sentiment analysis"
        )


@router.get("/history/{call_id}", response_model=SentimentHistoryResponse)
async def get_sentiment_history(
    call_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment analysis history for a call

    **Protected**: Requires authentication
    """
    try:
        # Verify call access
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or access denied"
            )

        sentiment_service = get_sentiment_service()
        history_data = await sentiment_service.get_sentiment_history(db, call_id, limit, offset)

        # Convert to response format
        history_items = []
        for analysis in history_data["history"]:
            emotions = [
                EmotionResult(
                    emotion=e.emotion,
                    score=e.score,
                    confidence=e.confidence
                )
                for e in analysis.emotions
            ]

            triggers = [
                TriggerResult(
                    keyword=t.keyword,
                    context=t.context,
                    impact_score=t.impact_score
                )
                for t in analysis.triggers
            ]

            history_items.append(SentimentResult(
                id=analysis.id,
                call_id=analysis.call_id,
                session_id=analysis.session_id,
                transcript_id=analysis.transcript_id,
                overall=analysis.overall,
                confidence=analysis.confidence,
                intensity=analysis.intensity,
                trend=analysis.trend,
                emotions=emotions,
                triggers=triggers,
                timestamp=analysis.timestamp,
                metadata=analysis.metadata_payload
            ))

        return SentimentHistoryResponse(
            history=history_items,
            total=history_data["total"],
            has_more=history_data["has_more"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sentiment history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sentiment history"
        )


@router.get("/realtime/{session_id}", response_model=dict)
async def get_real_time_sentiment(
    session_id: str,
    include_history: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time sentiment data for active session

    **Protected**: Requires authentication
    """
    try:
        stmt = select(RealTimeSentiment).where(RealTimeSentiment.session_id == session_id)
        result = await db.execute(stmt)
        rt_sentiment = result.scalar_one_or_none()

        if not rt_sentiment:
            return {
                "success": False,
                "message": "No real-time sentiment data found for this session"
            }

        # Build response
        history = []
        if include_history and rt_sentiment.sentiment_history:
            history = [
                RealTimeSentimentSnapshot(
                    timestamp=datetime.fromisoformat(h["timestamp"]),
                    sentiment=SentimentType(h["sentiment"]),
                    confidence=h["confidence"],
                    intensity=h["intensity"]
                )
                for h in rt_sentiment.sentiment_history
            ]

        response_data = RealTimeSentimentResponse(
            session_id=rt_sentiment.session_id,
            call_id=rt_sentiment.call_id,
            current_sentiment=rt_sentiment.current_sentiment,
            current_confidence=rt_sentiment.current_confidence,
            current_intensity=rt_sentiment.current_intensity,
            trend=rt_sentiment.trend,
            is_active=rt_sentiment.is_active,
            started_at=rt_sentiment.started_at,
            last_updated=rt_sentiment.last_updated,
            sentiment_history=history,
            alerts=rt_sentiment.alerts or []
        )

        return {
            "success": True,
            "data": response_data.dict()
        }

    except Exception as e:
        logger.error(f"Error getting real-time sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve real-time sentiment data"
        )


@router.get("/analytics", response_model=dict)
async def get_sentiment_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    call_ids: Optional[List[str]] = Query(None),
    agent_id: Optional[str] = None,
    sentiment_type: Optional[SentimentType] = None,
    emotion_type: Optional[EmotionType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment analytics and insights

    **Protected**: Requires authentication
    """
    try:
        is_supervisor = "supervisor" in (current_user.roles or [])

        # Default date range: last 30 days
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=30))

        # Build query
        from sqlalchemy.orm import selectinload

        stmt = (
            select(SentimentAnalysis)
            .join(SentimentAnalysis.call)
            .where(Call.organization_id == current_user.organization_id)
            .where(SentimentAnalysis.timestamp >= start_date)
            .where(SentimentAnalysis.timestamp <= end_date)
            .options(
                selectinload(SentimentAnalysis.emotions),
                selectinload(SentimentAnalysis.triggers),
                selectinload(SentimentAnalysis.call)
            )
        )

        # Apply filters
        if call_ids:
            stmt = stmt.where(SentimentAnalysis.call_id.in_(call_ids))

        if sentiment_type:
            stmt = stmt.where(SentimentAnalysis.overall == sentiment_type)

        if not is_supervisor:
            stmt = stmt.where(Call.agent_id == current_user.id)
        elif agent_id:
            stmt = stmt.where(Call.agent_id == agent_id)

        result = await db.execute(stmt)
        analyses = result.scalars().all()

        # Calculate analytics
        total = len(analyses)

        if total == 0:
            return {
                "success": True,
                "data": {
                    "summary": {
                        "total_analyses": 0,
                        "avg_confidence": 0,
                        "avg_intensity": 0,
                        "date_range": {"startDate": start_date, "endDate": end_date}
                    },
                    "sentiment_distribution": {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0},
                    "trend_distribution": {"IMPROVING": 0, "DECLINING": 0, "STABLE": 0},
                    "top_emotions": [],
                    "daily_analytics": []
                }
            }

        # Sentiment distribution
        sentiment_dist = SentimentDistribution(
            POSITIVE=sum(1 for a in analyses if a.overall == SentimentType.POSITIVE),
            NEUTRAL=sum(1 for a in analyses if a.overall == SentimentType.NEUTRAL),
            NEGATIVE=sum(1 for a in analyses if a.overall == SentimentType.NEGATIVE)
        )

        # Averages
        avg_confidence = sum(a.confidence for a in analyses) / total
        avg_intensity = sum(a.intensity for a in analyses) / total

        # Trend distribution
        trend_dist = TrendDistribution(
            IMPROVING=sum(1 for a in analyses if a.trend == TrendType.IMPROVING),
            DECLINING=sum(1 for a in analyses if a.trend == TrendType.DECLINING),
            STABLE=sum(1 for a in analyses if a.trend == TrendType.STABLE or a.trend is None)
        )

        # Top emotions
        emotion_counts = {}
        for analysis in analyses:
            for emotion in analysis.emotions:
                key = emotion.emotion.value
                emotion_counts[key] = emotion_counts.get(key, 0) + 1

        top_emotions = [
            TopEmotion(emotion=emotion, count=count)
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Daily analytics
        daily_data = {}
        for analysis in analyses:
            date_key = analysis.timestamp.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "total": 0,
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "confidence_sum": 0
                }

            daily_data[date_key]["total"] += 1
            daily_data[date_key]["confidence_sum"] += analysis.confidence

            if analysis.overall == SentimentType.POSITIVE:
                daily_data[date_key]["positive"] += 1
            elif analysis.overall == SentimentType.NEUTRAL:
                daily_data[date_key]["neutral"] += 1
            else:
                daily_data[date_key]["negative"] += 1

        daily_analytics = [
            DailyAnalytics(
                date=data["date"],
                total=data["total"],
                positive=data["positive"],
                neutral=data["neutral"],
                negative=data["negative"],
                avg_confidence=data["confidence_sum"] / data["total"]
            )
            for data in sorted(daily_data.values(), key=lambda x: x["date"])
        ]

        response = SentimentAnalyticsResponse(
            summary=SentimentAnalyticsSummary(
                total_analyses=total,
                avg_confidence=round(avg_confidence, 2),
                avg_intensity=round(avg_intensity, 2),
                date_range={"startDate": start_date, "endDate": end_date}
            ),
            sentiment_distribution=sentiment_dist,
            trend_distribution=trend_dist,
            top_emotions=top_emotions,
            daily_analytics=daily_analytics
        )

        return {
            "success": True,
            "data": response.dict()
        }

    except Exception as e:
        logger.error(f"Error getting sentiment analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sentiment analytics"
        )


@router.post("/calls/{call_id}/summary", response_model=dict)
async def generate_call_summary(
    call_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate sentiment summary for a call

    **Protected**: Requires authentication
    """
    try:
        # Verify call access
        stmt = select(Call).where(
            Call.id == call_id,
            Call.organization_id == current_user.organization_id
        )
        result = await db.execute(stmt)
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found or access denied"
            )

        sentiment_service = get_sentiment_service()
        summary = await sentiment_service.generate_call_summary(db, call_id)

        return {
            "success": True,
            "data": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating sentiment summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate sentiment summary"
        )


@router.get("/alerts", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_sentiment_alerts(
    severity: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    alert_type: Optional[str] = Query(None, regex="^(escalation|satisfaction|frustration|confusion)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sentiment alerts for active sessions

    **Protected**: Requires supervisor role
    """
    try:
        # Get active real-time sessions
        from sqlalchemy.orm import selectinload

        stmt = (
            select(RealTimeSentiment)
            .where(RealTimeSentiment.is_active == True)
            .join(RealTimeSentiment.call)
            .where(Call.organization_id == current_user.organization_id)
            .options(selectinload(RealTimeSentiment.call))
        )

        result = await db.execute(stmt)
        active_sessions = result.scalars().all()

        # Extract and filter alerts
        all_alerts = []
        for session in active_sessions:
            session_alerts = session.alerts or []
            for alert in session_alerts:
                all_alerts.append({
                    **alert,
                    "sessionId": session.session_id,
                    "callId": session.call_id
                })

        # Apply filters
        if severity:
            all_alerts = [a for a in all_alerts if a.get("severity") == severity]

        if alert_type:
            all_alerts = [a for a in all_alerts if a.get("type") == alert_type]

        # Sort by timestamp and limit
        all_alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        all_alerts = all_alerts[:limit]

        return {
            "success": True,
            "data": {
                "alerts": all_alerts,
                "total": len(all_alerts),
                "active_sessions_count": len(active_sessions)
            }
        }

    except Exception as e:
        logger.error(f"Error getting sentiment alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sentiment alerts"
        )


@router.get("/health", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_service_health():
    """
    Get sentiment service health status

    **Protected**: Requires supervisor role
    """
    try:
        sentiment_service = get_sentiment_service()
        health = sentiment_service.get_health_status()

        return {
            "success": True,
            "data": health
        }

    except Exception as e:
        logger.error(f"Error getting service health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve service health"
        )


@router.post("/cleanup", response_model=dict, dependencies=[Depends(require_supervisor)])
async def cleanup_sentiment_data(
    max_age_hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Clean up old sentiment data

    **Protected**: Requires supervisor role
    """
    try:
        sentiment_service = get_sentiment_service()
        max_age_ms = max_age_hours * 60 * 60 * 1000

        deleted_count = await sentiment_service.cleanup(db, max_age_ms)

        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} sentiment records older than {max_age_hours} hours"
        }

    except Exception as e:
        logger.error(f"Error cleaning up sentiment data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup sentiment data"
        )
