"""
Speak by Kraliki - Insights Router
Dashboard analytics and reporting

RBAC enforced:
- owner, hr_director: View all insights across departments
- manager: View insights only for their department
"""

from uuid import UUID
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rbac import Permission, require_permission, can_view_all_departments
from app.models.conversation import Conversation
from app.models.survey import Survey
from app.models.alert import Alert
from app.models.action import Action
from app.models.department import Department
from app.models.employee import Employee
from app.services.analysis import AnalysisService
from app.schemas.insights import (
    InsightsOverview,
    DepartmentInsights,
    TrendData,
    TrendDataPoint,
    SentimentGauge,
    ParticipationRate,
    TopicCount,
    QuoteDisplay,
)

router = APIRouter(prefix="/speak/insights", tags=["insights"])
analysis_service = AnalysisService()


@router.get("/overview", response_model=InsightsOverview)
async def get_overview(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user: dict = Depends(require_permission(Permission.INSIGHTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get insights overview.

    RBAC: Managers only see insights for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role", "")
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)
    prev_period_start = period_start - timedelta(days=period_days)

    # Build base query
    base_query = (
        select(Conversation)
        .join(Survey)
        .where(Survey.company_id == company_id)
    )

    # Apply department scoping for managers
    if not can_view_all_departments(user_role):
        user_dept_id = current_user.get("department_id")
        if user_dept_id:
            base_query = base_query.join(Employee).where(Employee.department_id == UUID(user_dept_id))
        else:
            # Manager without department sees nothing
            base_query = base_query.where(False)

    # Get conversations for current period
    conv_result = await db.execute(
        base_query
        .where(Conversation.completed_at >= period_start)
        .where(Conversation.completed_at <= period_end)
    )
    conversations = conv_result.scalars().all()

    # Get conversations for previous period (for comparison)
    prev_conv_result = await db.execute(
        select(Conversation)
        .join(Survey)
        .where(Survey.company_id == company_id)
        .where(Conversation.completed_at >= prev_period_start)
        .where(Conversation.completed_at < period_start)
    )
    prev_conversations = prev_conv_result.scalars().all()

    # Calculate sentiment
    sentiments = [float(c.sentiment_score) for c in conversations if c.sentiment_score]
    prev_sentiments = [float(c.sentiment_score) for c in prev_conversations if c.sentiment_score]

    current_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    prev_sentiment = sum(prev_sentiments) / len(prev_sentiments) if prev_sentiments else None

    # Calculate participation
    total_invited = await db.scalar(
        select(func.count(Conversation.id))
        .join(Survey)
        .where(Survey.company_id == company_id)
        .where(Conversation.invited_at >= period_start)
    ) or 0

    total_completed = len([c for c in conversations if c.status == "completed"])

    prev_invited = await db.scalar(
        select(func.count(Conversation.id))
        .join(Survey)
        .where(Survey.company_id == company_id)
        .where(Conversation.invited_at >= prev_period_start)
        .where(Conversation.invited_at < period_start)
    ) or 0

    prev_completed = len([c for c in prev_conversations if c.status == "completed"])

    current_participation = total_completed / total_invited if total_invited else 0.0
    prev_participation = prev_completed / prev_invited if prev_invited else None

    # Extract topics
    topic_counts = {}
    for conv in conversations:
        if conv.topics:
            for topic in conv.topics:
                if topic not in topic_counts:
                    topic_counts[topic] = {"count": 0, "sentiments": []}
                topic_counts[topic]["count"] += 1
                if conv.sentiment_score:
                    topic_counts[topic]["sentiments"].append(float(conv.sentiment_score))

    top_topics = [
        TopicCount(
            topic=topic,
            count=data["count"],
            sentiment=sum(data["sentiments"]) / len(data["sentiments"]) if data["sentiments"] else 0.0
        )
        for topic, data in sorted(topic_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    ]

    # Get alert and action counts
    active_alerts = await db.scalar(
        select(func.count(Alert.id))
        .where(Alert.company_id == company_id)
        .where(Alert.is_resolved == False)
    ) or 0

    pending_actions = await db.scalar(
        select(func.count(Action.id))
        .where(Action.company_id == company_id)
        .where(Action.status.in_(["new", "heard", "in_progress"]))
    ) or 0

    return InsightsOverview(
        company_id=company_id,
        period_start=period_start,
        period_end=period_end,
        sentiment=SentimentGauge(
            current=current_sentiment,
            previous=prev_sentiment,
            change=current_sentiment - prev_sentiment if prev_sentiment else None,
            trend="up" if prev_sentiment and current_sentiment > prev_sentiment else "down" if prev_sentiment and current_sentiment < prev_sentiment else "stable"
        ),
        participation=ParticipationRate(
            current=current_participation,
            previous=prev_participation,
            change=current_participation - prev_participation if prev_participation else None,
            total_invited=total_invited,
            total_completed=total_completed
        ),
        top_topics=top_topics,
        active_alerts_count=active_alerts,
        pending_actions_count=pending_actions,
    )


@router.get("/departments", response_model=list[DepartmentInsights])
async def get_department_insights(
    period_days: int = Query(default=30, ge=7, le=365),
    current_user: dict = Depends(require_permission(Permission.INSIGHTS_VIEW_ALL)),
    db: AsyncSession = Depends(get_db)
):
    """Get per-department breakdown.

    RBAC: Only owner and hr_director can view all department insights.
    """
    company_id = UUID(current_user["company_id"])
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)

    # Get departments
    dept_result = await db.execute(
        select(Department).where(Department.company_id == company_id)
    )
    departments = dept_result.scalars().all()

    insights = []
    for dept in departments:
        # Get conversations for department
        from app.models.employee import Employee
        conv_result = await db.execute(
            select(Conversation)
            .join(Employee)
            .join(Survey)
            .where(Survey.company_id == company_id)
            .where(Employee.department_id == dept.id)
            .where(Conversation.completed_at >= period_start)
        )
        conversations = conv_result.scalars().all()

        # Calculate metrics
        sentiments = [float(c.sentiment_score) for c in conversations if c.sentiment_score]
        current_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        total_completed = len([c for c in conversations if c.status == "completed"])

        # Employee count
        emp_count = await db.scalar(
            select(func.count(Employee.id))
            .where(Employee.department_id == dept.id)
            .where(Employee.is_active == True)
        ) or 0

        # Topics
        topic_counts = {}
        for conv in conversations:
            if conv.topics:
                for topic in conv.topics:
                    if topic not in topic_counts:
                        topic_counts[topic] = {"count": 0, "sentiments": []}
                    topic_counts[topic]["count"] += 1
                    if conv.sentiment_score:
                        topic_counts[topic]["sentiments"].append(float(conv.sentiment_score))

        top_topics = [
            TopicCount(
                topic=topic,
                count=data["count"],
                sentiment=sum(data["sentiments"]) / len(data["sentiments"]) if data["sentiments"] else 0.0
            )
            for topic, data in sorted(topic_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        ]

        # Alert count
        alerts_count = await db.scalar(
            select(func.count(Alert.id))
            .where(Alert.department_id == dept.id)
            .where(Alert.is_resolved == False)
        ) or 0

        insights.append(DepartmentInsights(
            department_id=dept.id,
            department_name=dept.name,
            employee_count=emp_count,
            sentiment=SentimentGauge(
                current=current_sentiment,
                previous=None,
                change=None,
                trend="stable"
            ),
            participation=ParticipationRate(
                current=total_completed / emp_count if emp_count else 0.0,
                previous=None,
                change=None,
                total_invited=emp_count,
                total_completed=total_completed
            ),
            top_topics=top_topics,
            alerts_count=alerts_count,
        ))

    return insights


@router.get("/trends", response_model=TrendData)
async def get_trends(
    metric: str = Query(default="sentiment", pattern="^(sentiment|participation)$"),
    period: str = Query(default="month", pattern="^(week|month|quarter)$"),
    current_user: dict = Depends(require_permission(Permission.INSIGHTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get trend data over time.

    RBAC: Managers only see trends for their department.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role", "")

    # Determine period
    if period == "week":
        days = 7
        bucket_size = 1  # Daily
    elif period == "month":
        days = 30
        bucket_size = 7  # Weekly
    else:  # quarter
        days = 90
        bucket_size = 14  # Bi-weekly

    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Build query with department scoping
    query = (
        select(Conversation)
        .join(Survey)
        .where(Survey.company_id == company_id)
        .where(Conversation.completed_at >= period_start)
    )

    # Apply department scoping for managers
    if not can_view_all_departments(user_role):
        user_dept_id = current_user.get("department_id")
        if user_dept_id:
            query = query.join(Employee).where(Employee.department_id == UUID(user_dept_id))
        else:
            # Manager without department sees empty trends
            return TrendData(metric=metric, period=period, data=[])

    query = query.order_by(Conversation.completed_at)
    conv_result = await db.execute(query)
    conversations = conv_result.scalars().all()

    # Group by time buckets
    data_points = []
    current_bucket_start = period_start

    while current_bucket_start < period_end:
        bucket_end = current_bucket_start + timedelta(days=bucket_size)
        bucket_convs = [
            c for c in conversations
            if c.completed_at and current_bucket_start <= c.completed_at < bucket_end
        ]

        if metric == "sentiment":
            sentiments = [float(c.sentiment_score) for c in bucket_convs if c.sentiment_score]
            value = sum(sentiments) / len(sentiments) if sentiments else 0.0
        else:  # participation
            value = len([c for c in bucket_convs if c.status == "completed"])

        data_points.append(TrendDataPoint(
            date=current_bucket_start,
            value=value,
            count=len(bucket_convs)
        ))

        current_bucket_start = bucket_end

    return TrendData(
        metric=metric,
        period=period,
        data=data_points
    )


@router.get("/quotes", response_model=list[QuoteDisplay])
async def get_quotes(
    limit: int = Query(default=10, ge=1, le=50),
    sentiment: str | None = Query(default=None, pattern="^(positive|negative|neutral)$"),
    current_user: dict = Depends(require_permission(Permission.INSIGHTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get anonymous quotes for display.

    RBAC: Managers only see quotes from their department's employees.
    """
    company_id = UUID(current_user["company_id"])
    user_role = current_user.get("role", "")

    query = (
        select(Conversation)
        .join(Survey)
        .where(Survey.company_id == company_id)
        .where(Conversation.status == "completed")
        .where(Conversation.transcript != None)
    )

    # Apply department scoping for managers
    if not can_view_all_departments(user_role):
        user_dept_id = current_user.get("department_id")
        if user_dept_id:
            query = query.join(Employee).where(Employee.department_id == UUID(user_dept_id))
        else:
            # Manager without department sees nothing
            return []

    query = query.order_by(Conversation.completed_at.desc())

    if sentiment == "positive":
        query = query.where(Conversation.sentiment_score > 0.2)
    elif sentiment == "negative":
        query = query.where(Conversation.sentiment_score < -0.2)
    elif sentiment == "neutral":
        query = query.where(Conversation.sentiment_score.between(-0.2, 0.2))

    result = await db.execute(query.limit(limit * 2))  # Get extra to filter
    conversations = result.scalars().all()

    quotes = []
    for conv in conversations:
        if not conv.transcript:
            continue

        # Extract meaningful user quotes
        user_turns = [
            t for t in conv.transcript
            if t.get("role") == "user" and
            not t.get("redacted") and
            len(t.get("content", "")) > 30
        ]

        if user_turns:
            # Pick a representative quote
            quote_turn = max(user_turns, key=lambda t: len(t.get("content", "")))

            # Get department name
            from app.models.employee import Employee
            emp_result = await db.execute(
                select(Employee).where(Employee.id == conv.employee_id)
            )
            emp = emp_result.scalar_one_or_none()

            dept_name = None
            if emp and emp.department_id:
                dept_result = await db.execute(
                    select(Department).where(Department.id == emp.department_id)
                )
                dept = dept_result.scalar_one_or_none()
                dept_name = dept.name if dept else None

            quotes.append(QuoteDisplay(
                id=conv.id,
                content=quote_turn["content"][:300] + ("..." if len(quote_turn["content"]) > 300 else ""),
                sentiment=float(conv.sentiment_score) if conv.sentiment_score else 0.0,
                topic=conv.topics[0] if conv.topics else None,
                department_name=dept_name,
                created_at=conv.completed_at or conv.created_at,
                anonymous_id=conv.anonymous_id or "ANON"
            ))

        if len(quotes) >= limit:
            break

    return quotes
