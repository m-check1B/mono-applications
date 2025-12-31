"""
Event Publishing Integration Examples for Voice by Kraliki

Events to publish:
1. call.started - When call begins
2. call.ended - When call completes (Planning module can create follow-up task)
3. call.transcribed - Real-time transcript available
4. campaign.completed - Campaign finished (trigger workflow)
5. sentiment.analyzed - Negative sentiment detected (alert)
"""

from fastapi import APIRouter, Depends
from app.core.events import event_publisher
from app.core.security import get_current_user

router = APIRouter()

# Example 1: Call started event
@router.post("/calls/{call_id}/start")
async def start_call(call_id: str, current_user = Depends(get_current_user)):
    """
    Start a call and publish event

    Platform Integration:
    - Tracking module records call start time
    - Analytics module starts real-time metrics
    """
    # ... existing call start logic ...

    # Publish event for other modules
    await event_publisher.publish_call_started(
        call_id=call_id,
        from_number="+15551234567",
        to_number="+15559876543",
        campaign_id="campaign-123",
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"status": "started", "event_published": True}

# Example 2: Call ended event
@router.post("/calls/{call_id}/end")
async def end_call(call_id: str, current_user = Depends(get_current_user)):
    """
    End a call and publish event

    Platform Integration:
    - Planning module (Focus-Lite) creates follow-up task if callback requested
    - Analytics updates completion metrics
    - CRM module updates customer interaction history
    """
    # ... existing call end logic ...

    # Publish event for other modules
    await event_publisher.publish_call_ended(
        call_id=call_id,
        duration=320,  # seconds
        outcome="callback_requested",
        transcript="Customer wants callback tomorrow at 2pm",
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"status": "ended", "event_published": True}

# Example 3: Campaign completed event
@router.post("/campaigns/{campaign_id}/complete")
async def complete_campaign(campaign_id: str, current_user = Depends(get_current_user)):
    """
    Complete campaign and publish event

    Platform Integration:
    - Agents module (CLI-Toris) suggests workflow optimizations
    - Reporting module generates campaign analytics
    - Workflow module triggers next campaign in sequence
    """
    # ... existing campaign logic ...

    await event_publisher.publish_campaign_completed(
        campaign_id=campaign_id,
        total_calls=150,
        successful_calls=120,
        failed_calls=30,
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"status": "completed", "event_published": True}

# Example 4: Real-time transcription event
@router.post("/calls/{call_id}/transcribe")
async def transcribe_call(call_id: str, current_user = Depends(get_current_user)):
    """
    Publish real-time transcription

    Platform Integration:
    - AI assistant provides real-time suggestions to agent
    - Compliance module monitors for restricted keywords
    - Training module identifies coaching opportunities
    """
    # ... transcription logic ...

    transcript_chunk = "Customer mentioned they received defective product"

    await event_publisher.publish_call_transcribed(
        call_id=call_id,
        transcript=transcript_chunk,
        language="en-US",
        confidence=0.95,
        organization_id=current_user.get("org_id")
    )

    return {"transcription_published": True}

# Example 5: Negative sentiment alert
@router.post("/calls/{call_id}/analyze")
async def analyze_sentiment(call_id: str, current_user = Depends(get_current_user)):
    """
    Analyze sentiment and alert on negative

    Platform Integration:
    - Notification module sends alert to supervisor
    - Escalation module suggests supervisor intervention
    - Quality module flags call for review
    """
    # ... sentiment analysis logic ...

    sentiment_score = -0.7  # Negative

    if sentiment_score < -0.5:
        await event_publisher.publish_sentiment_analyzed(
            call_id=call_id,
            sentiment="negative",
            score=sentiment_score,
            keywords=["frustrated", "angry", "disappointed"],
            organization_id=current_user.get("org_id")
        )

    return {"sentiment_score": sentiment_score, "alert_sent": True}

# Example 6: Batch event publishing for campaign analytics
@router.post("/campaigns/{campaign_id}/analytics")
async def publish_campaign_analytics(campaign_id: str, current_user = Depends(get_current_user)):
    """
    Publish multiple events for comprehensive campaign analytics

    This demonstrates publishing multiple related events in sequence
    for complex workflows that span multiple platform modules
    """
    # Campaign completion event
    await event_publisher.publish_campaign_completed(
        campaign_id=campaign_id,
        total_calls=200,
        successful_calls=150,
        failed_calls=50,
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    # Overall sentiment summary event
    await event_publisher.publish(
        event_type="campaign.sentiment.summary",
        data={
            "campaign_id": campaign_id,
            "positive_calls": 120,
            "neutral_calls": 50,
            "negative_calls": 30,
            "average_score": 0.35
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    # Quality metrics event
    await event_publisher.publish(
        event_type="campaign.quality.metrics",
        data={
            "campaign_id": campaign_id,
            "average_handle_time": 245,  # seconds
            "first_call_resolution": 0.75,
            "customer_satisfaction": 4.2  # out of 5
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {"analytics_events_published": 3}

# Example 7: Using events for cross-module workflows
@router.post("/workflows/callback-requested")
async def handle_callback_workflow(current_user = Depends(get_current_user)):
    """
    Demonstrate cross-module workflow triggered by events

    Workflow:
    1. Call ends with "callback_requested" outcome
    2. Event published to platform bus
    3. Planning module (Focus-Lite) receives event
    4. Automatically creates task: "Call back customer X"
    5. Task assigned to same agent
    6. Reminder sent at scheduled time

    This shows how Voice by Kraliki events enable automation across modules
    without tight coupling
    """
    call_id = "call-789"
    customer_name = "John Smith"
    callback_time = "2025-10-06T14:00:00Z"

    await event_publisher.publish(
        event_type="call.callback.requested",
        data={
            "call_id": call_id,
            "customer_name": customer_name,
            "requested_time": callback_time,
            "priority": "high",
            "notes": "Customer wants to discuss refund options"
        },
        organization_id=current_user.get("org_id"),
        user_id=current_user.get("sub")
    )

    return {
        "workflow_initiated": True,
        "expected_actions": [
            "Task created in Planning module",
            "Reminder scheduled",
            "Agent notified"
        ]
    }
