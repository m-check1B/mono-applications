"""Sentiment analysis service - AI-powered sentiment detection"""
import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
import anthropic
from app.core.logger import get_logger
from app.models.sentiment import (
    SentimentAnalysis, SentimentEmotion, SentimentTrigger,
    RealTimeSentiment, SentimentAlert, SentimentType, EmotionType, TrendType
)
from app.schemas.sentiment import SentimentContext

logger = get_logger(__name__)


class SentimentAnalysisService:
    """Service for AI-powered sentiment analysis"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.cache: Dict[str, Any] = {}  # Simple in-memory cache
        self.metrics = {
            "total_analyses": 0,
            "total_response_time_ms": 0,
            "errors": 0,
            "active_sessions": 0
        }

    async def analyze_sentiment(
        self,
        db,
        text: str,
        call_id: str,
        session_id: Optional[str] = None,
        transcript_id: Optional[str] = None,
        context: Optional[SentimentContext] = None
    ) -> SentimentAnalysis:
        """
        Analyze sentiment of text using Claude AI

        Args:
            db: Database session
            text: Text to analyze
            call_id: Associated call ID
            session_id: Optional session ID
            transcript_id: Optional transcript ID
            context: Optional conversation context

        Returns:
            SentimentAnalysis object
        """
        start_time = datetime.utcnow()

        try:
            # Build context-aware prompt
            context_str = self._build_context_string(context) if context else ""

            prompt = f"""Analyze the sentiment of the following text from a call center conversation.
{context_str}

Text to analyze:
"{text}"

Provide a JSON response with:
1. overall: POSITIVE, NEUTRAL, or NEGATIVE
2. confidence: 0.0 to 1.0
3. intensity: 0.0 to 1.0
4. trend: IMPROVING, DECLINING, or STABLE (based on context if available)
5. emotions: array of {{emotion: string, score: float, confidence: float}} for detected emotions (JOY, SADNESS, ANGER, FEAR, SURPRISE, DISGUST, TRUST, ANTICIPATION, FRUSTRATION, SATISFACTION, CONFUSION, EXCITEMENT)
6. triggers: array of {{keyword: string, context: string, impact_score: float}} for keywords that influenced sentiment
7. reasoning: brief explanation

Return ONLY valid JSON, no other text."""

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            import json
            response_text = message.content[0].text
            result = json.loads(response_text)

            # Create sentiment analysis record
            analysis_id = str(uuid4())
            analysis = SentimentAnalysis(
                id=analysis_id,
                call_id=call_id,
                session_id=session_id,
                transcript_id=transcript_id,
                overall=SentimentType[result["overall"]],
                confidence=float(result["confidence"]),
                intensity=float(result["intensity"]),
                trend=TrendType[result.get("trend", "STABLE")] if result.get("trend") else None,
                conversation_phase=context.conversation_phase if context else None,
                customer_type=context.customer_type if context else None,
                call_reason=context.call_reason if context else None,
                urgency=context.urgency if context else None,
                text_analyzed=text[:1000],  # Store first 1000 chars
                timestamp=datetime.utcnow(),
                metadata_payload={"reasoning": result.get("reasoning", "")}
            )

            db.add(analysis)

            # Add emotions
            for emotion_data in result.get("emotions", []):
                try:
                    emotion = SentimentEmotion(
                        id=str(uuid4()),
                        analysis_id=analysis_id,
                        emotion=EmotionType[emotion_data["emotion"]],
                        score=float(emotion_data["score"]),
                        confidence=float(emotion_data["confidence"])
                    )
                    db.add(emotion)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Invalid emotion data: {e}")

            # Add triggers
            for trigger_data in result.get("triggers", []):
                trigger = SentimentTrigger(
                    id=str(uuid4()),
                    analysis_id=analysis_id,
                    keyword=trigger_data["keyword"],
                    context=trigger_data.get("context"),
                    impact_score=float(trigger_data.get("impact_score", 0.5))
                )
                db.add(trigger)

            await db.commit()
            await db.refresh(analysis)

            # Update metrics
            elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics["total_analyses"] += 1
            self.metrics["total_response_time_ms"] += elapsed

            logger.info(f"Sentiment analysis completed for call {call_id}: {result['overall']} ({elapsed:.0f}ms)")

            return analysis

        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Error analyzing sentiment: {e}")
            await db.rollback()
            raise

    async def batch_analyze_sentiment(
        self,
        db,
        analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch analyze multiple texts

        Args:
            db: Database session
            analyses: List of analysis requests

        Returns:
            Dictionary with successful and failed counts
        """
        tasks = []
        for analysis_data in analyses:
            task = self.analyze_sentiment(
                db,
                analysis_data["text"],
                analysis_data["call_id"],
                analysis_data.get("session_id"),
                analysis_data.get("transcript_id"),
                analysis_data.get("context")
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]

        return {
            "successful": successful,
            "failed": len(failed),
            "total": len(analyses)
        }

    async def get_sentiment_history(self, db, call_id: str, limit: int = 50, offset: int = 0):
        """Get sentiment analysis history for a call"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = (
            select(SentimentAnalysis)
            .where(SentimentAnalysis.call_id == call_id)
            .options(
                selectinload(SentimentAnalysis.emotions),
                selectinload(SentimentAnalysis.triggers)
            )
            .order_by(SentimentAnalysis.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(stmt)
        analyses = result.scalars().all()

        # Get total count
        count_stmt = select(SentimentAnalysis).where(SentimentAnalysis.call_id == call_id)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())

        return {
            "history": analyses,
            "total": total,
            "has_more": offset + limit < total
        }

    async def update_real_time_sentiment(
        self,
        db,
        session_id: str,
        call_id: str,
        sentiment: SentimentType,
        confidence: float,
        intensity: float
    ):
        """Update or create real-time sentiment tracking"""
        from sqlalchemy import select

        # Check if session exists
        stmt = select(RealTimeSentiment).where(RealTimeSentiment.session_id == session_id)
        result = await db.execute(stmt)
        rt_sentiment = result.scalar_one_or_none()

        if not rt_sentiment:
            # Create new
            rt_sentiment = RealTimeSentiment(
                id=str(uuid4()),
                session_id=session_id,
                call_id=call_id,
                current_sentiment=sentiment,
                current_confidence=confidence,
                current_intensity=intensity,
                trend=TrendType.STABLE,
                is_active=True,
                started_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                sentiment_history=[],
                alerts=[]
            )
            db.add(rt_sentiment)
            self.metrics["active_sessions"] += 1
        else:
            # Update existing
            # Determine trend
            if sentiment.value > rt_sentiment.current_sentiment.value:
                trend = TrendType.IMPROVING
            elif sentiment.value < rt_sentiment.current_sentiment.value:
                trend = TrendType.DECLINING
            else:
                trend = TrendType.STABLE

            # Add to history
            history = rt_sentiment.sentiment_history or []
            history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "sentiment": sentiment.value,
                "confidence": confidence,
                "intensity": intensity
            })

            rt_sentiment.current_sentiment = sentiment
            rt_sentiment.current_confidence = confidence
            rt_sentiment.current_intensity = intensity
            rt_sentiment.trend = trend
            rt_sentiment.last_updated = datetime.utcnow()
            rt_sentiment.sentiment_history = history

            # Check for alerts
            await self._check_and_create_alerts(db, rt_sentiment)

        await db.commit()
        return rt_sentiment

    async def _check_and_create_alerts(self, db, rt_sentiment: RealTimeSentiment):
        """Check sentiment and create alerts if needed"""
        alerts = rt_sentiment.alerts or []

        # Check for negative sentiment with high confidence
        if (rt_sentiment.current_sentiment == SentimentType.NEGATIVE and
            rt_sentiment.current_confidence > 0.8):
            alert = {
                "id": str(uuid4()),
                "type": "escalation",
                "severity": "high",
                "message": "High confidence negative sentiment detected",
                "timestamp": datetime.utcnow().isoformat()
            }
            alerts.append(alert)

            # Create persistent alert
            db_alert = SentimentAlert(
                id=alert["id"],
                session_id=rt_sentiment.session_id,
                call_id=rt_sentiment.call_id,
                alert_type=alert["type"],
                severity=alert["severity"],
                message=alert["message"],
                triggered_at=datetime.utcnow()
            )
            db.add(db_alert)

        # Check for declining trend
        if rt_sentiment.trend == TrendType.DECLINING and rt_sentiment.current_intensity > 0.7:
            alert = {
                "id": str(uuid4()),
                "type": "satisfaction",
                "severity": "medium",
                "message": "Customer satisfaction declining",
                "timestamp": datetime.utcnow().isoformat()
            }
            alerts.append(alert)

        rt_sentiment.alerts = alerts

    async def generate_call_summary(self, db, call_id: str) -> Dict[str, Any]:
        """Generate sentiment summary for entire call"""
        from sqlalchemy import select, func

        # Get all analyses for call
        stmt = (
            select(SentimentAnalysis)
            .where(SentimentAnalysis.call_id == call_id)
            .order_by(SentimentAnalysis.timestamp.asc())
        )
        result = await db.execute(stmt)
        analyses = result.scalars().all()

        if not analyses:
            return {"error": "No sentiment data found"}

        # Calculate summary stats
        total = len(analyses)
        positive = sum(1 for a in analyses if a.overall == SentimentType.POSITIVE)
        neutral = sum(1 for a in analyses if a.overall == SentimentType.NEUTRAL)
        negative = sum(1 for a in analyses if a.overall == SentimentType.NEGATIVE)

        avg_confidence = sum(a.confidence for a in analyses) / total
        avg_intensity = sum(a.intensity for a in analyses) / total

        # Overall trend
        if len(analyses) >= 2:
            first_half = analyses[:len(analyses)//2]
            second_half = analyses[len(analyses)//2:]
            first_avg = sum(self._sentiment_to_score(a.overall) for a in first_half) / len(first_half)
            second_avg = sum(self._sentiment_to_score(a.overall) for a in second_half) / len(second_half)

            if second_avg > first_avg:
                overall_trend = "IMPROVING"
            elif second_avg < first_avg:
                overall_trend = "DECLINING"
            else:
                overall_trend = "STABLE"
        else:
            overall_trend = "STABLE"

        return {
            "call_id": call_id,
            "total_analyses": total,
            "sentiment_distribution": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative
            },
            "averages": {
                "confidence": round(avg_confidence, 3),
                "intensity": round(avg_intensity, 3)
            },
            "overall_trend": overall_trend,
            "timeline": [
                {
                    "timestamp": a.timestamp.isoformat(),
                    "sentiment": a.overall.value,
                    "confidence": a.confidence,
                    "intensity": a.intensity
                }
                for a in analyses
            ]
        }

    def _sentiment_to_score(self, sentiment: SentimentType) -> float:
        """Convert sentiment to numeric score"""
        if sentiment == SentimentType.POSITIVE:
            return 1.0
        elif sentiment == SentimentType.NEUTRAL:
            return 0.5
        else:
            return 0.0

    def _build_context_string(self, context: SentimentContext) -> str:
        """Build context string for AI prompt"""
        parts = []
        if context.conversation_phase:
            parts.append(f"Conversation phase: {context.conversation_phase.value}")
        if context.customer_type:
            parts.append(f"Customer type: {context.customer_type.value}")
        if context.call_reason:
            parts.append(f"Call reason: {context.call_reason}")
        if context.urgency:
            parts.append(f"Urgency: {context.urgency.value}")

        return "\n".join(parts) if parts else ""

    def get_health_status(self) -> Dict[str, Any]:
        """Get service health metrics"""
        avg_response_time = (
            self.metrics["total_response_time_ms"] / self.metrics["total_analyses"]
            if self.metrics["total_analyses"] > 0
            else 0
        )

        error_rate = (
            self.metrics["errors"] / self.metrics["total_analyses"]
            if self.metrics["total_analyses"] > 0
            else 0
        )

        return {
            "status": "healthy" if error_rate < 0.1 else "degraded",
            "active_sessions": self.metrics["active_sessions"],
            "total_analyses_today": self.metrics["total_analyses"],
            "average_response_time_ms": round(avg_response_time, 2),
            "error_rate": round(error_rate, 3)
        }

    async def cleanup(self, db, max_age_ms: int):
        """Clean up old sentiment data"""
        from sqlalchemy import delete

        cutoff_time = datetime.utcnow() - timedelta(milliseconds=max_age_ms)

        # Delete old real-time sentiment sessions
        stmt = (
            delete(RealTimeSentiment)
            .where(RealTimeSentiment.is_active == False)
            .where(RealTimeSentiment.last_updated < cutoff_time)
        )

        result = await db.execute(stmt)
        await db.commit()

        logger.info(f"Cleaned up {result.rowcount} old sentiment sessions")
        return result.rowcount


# Singleton instance
_sentiment_service = None


def get_sentiment_service() -> SentimentAnalysisService:
    """Get singleton sentiment service instance"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentAnalysisService()
    return _sentiment_service
