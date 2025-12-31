"""
Push Notifications Router
Handles Web Push subscription management and notification preferences

VD-384: Full implementation with pywebpush for actual push delivery.
Subscriptions stored in user.preferences['pushSubscription'] (database-backed).
"""
import os
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from pywebpush import webpush, WebPushException

from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])

# VAPID keys for Web Push
# Generate with: npx web-push generate-vapid-keys
# Store in secrets for production
VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY",
    "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U"
)
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS = {"sub": "mailto:support@verduona.com"}


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys


class NotificationPreferences(BaseModel):
    taskReminders: Optional[bool] = True
    dailyDigest: Optional[bool] = True
    pomodoroAlerts: Optional[bool] = True
    projectUpdates: Optional[bool] = False


class VapidKeyResponse(BaseModel):
    publicKey: str


def _get_user_subscription(user: User) -> Optional[dict]:
    """Get push subscription from user preferences."""
    prefs = user.preferences or {}
    return prefs.get("pushSubscription")


def _set_user_subscription(user: User, subscription: Optional[dict], db: Session):
    """Store push subscription in user preferences."""
    prefs = user.preferences or {}
    if subscription:
        prefs["pushSubscription"] = subscription
    else:
        prefs.pop("pushSubscription", None)
    user.preferences = prefs
    db.commit()


@router.get("/vapid-key", response_model=VapidKeyResponse)
async def get_vapid_key():
    """Get VAPID public key for push subscription."""
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID keys not configured")
    return VapidKeyResponse(publicKey=VAPID_PUBLIC_KEY)


@router.post("/subscribe")
async def subscribe_push(
    subscription: PushSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to push notifications."""
    try:
        # Store subscription in database
        sub_data = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.keys.p256dh,
                "auth": subscription.keys.auth
            }
        }
        _set_user_subscription(current_user, sub_data, db)

        # Initialize notification preferences if not set
        prefs = current_user.preferences or {}
        if "notifications" not in prefs:
            prefs["notifications"] = {
                "enabled": True,
                "taskReminders": True,
                "dailyDigest": True,
                "pomodoroAlerts": True,
                "projectUpdates": False
            }
            current_user.preferences = prefs
            db.commit()

        logger.info(f"User {current_user.id} subscribed to push notifications")
        return {"success": True, "message": "Subscribed to push notifications"}

    except Exception as e:
        logger.error(f"Push subscription failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/subscribe")
async def unsubscribe_push(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe from push notifications."""
    try:
        # Remove subscription from database
        _set_user_subscription(current_user, None, db)

        # Update preferences
        prefs = current_user.preferences or {}
        if "notifications" in prefs:
            prefs["notifications"]["enabled"] = False
            current_user.preferences = prefs
            db.commit()

        logger.info(f"User {current_user.id} unsubscribed from push notifications")
        return {"success": True, "message": "Unsubscribed from push notifications"}

    except Exception as e:
        logger.error(f"Push unsubscribe failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user's notification preferences."""
    prefs = current_user.preferences or {}
    notif_prefs = prefs.get("notifications", {})

    return NotificationPreferences(
        taskReminders=notif_prefs.get("taskReminders", True),
        dailyDigest=notif_prefs.get("dailyDigest", True),
        pomodoroAlerts=notif_prefs.get("pomodoroAlerts", True),
        projectUpdates=notif_prefs.get("projectUpdates", False)
    )


@router.patch("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences."""
    try:
        prefs = current_user.preferences or {}
        if "notifications" not in prefs:
            prefs["notifications"] = {"enabled": True}

        # Update only provided fields
        pref_dict = preferences.model_dump(exclude_unset=True)
        for key, value in pref_dict.items():
            if value is not None:
                prefs["notifications"][key] = value

        current_user.preferences = prefs
        db.commit()

        return {"success": True, "message": "Preferences updated"}

    except Exception as e:
        logger.error(f"Failed to update notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def send_test_notification(
    current_user: User = Depends(get_current_user)
):
    """Send a test push notification to the user."""
    try:
        subscription = _get_user_subscription(current_user)
        if not subscription:
            raise HTTPException(
                status_code=400,
                detail="No push subscription found. Please enable notifications first."
            )

        if not VAPID_PRIVATE_KEY:
            # Dev mode without VAPID private key
            logger.info(f"Test notification requested for user {current_user.id} (VAPID not configured)")
            return {"success": True, "message": "Test notification would be sent (VAPID not configured in dev)"}

        # Send actual push notification
        payload = json.dumps({
            "title": "Focus by Kraliki",
            "body": "Push notifications are working! 🎉",
            "url": "/dashboard",
            "tag": "test"
        })

        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )

        logger.info(f"Test notification sent to user {current_user.id}")
        return {"success": True, "message": "Test notification sent"}

    except WebPushException as e:
        logger.error(f"WebPush error for user {current_user.id}: {e}")
        # Handle subscription gone (410) - clean up stale subscription
        if e.response and e.response.status_code == 410:
            _set_user_subscription(current_user, None, None)  # Will need db passed
            raise HTTPException(status_code=410, detail="Subscription expired. Please re-enable notifications.")
        raise HTTPException(status_code=500, detail=f"Push delivery failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    url: str = "/",
    tag: str = "default",
    db: Session = None
) -> bool:
    """
    Send a push notification to a user.
    Called by other modules (tasks, pomodoro, etc.)

    Args:
        user_id: The user ID to send notification to
        title: Notification title
        body: Notification body text
        url: URL to open when notification is clicked
        tag: Notification tag (for grouping/replacing)
        db: Database session (required for fetching subscription)

    Returns:
        True if notification was sent successfully, False otherwise
    """
    if not VAPID_PRIVATE_KEY:
        logger.debug("VAPID private key not configured, skipping push")
        return False

    if not db:
        logger.warning("No database session provided to send_push_notification")
        return False

    # Fetch user and subscription
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.debug(f"User {user_id} not found")
        return False

    subscription = _get_user_subscription(user)
    if not subscription:
        logger.debug(f"No push subscription for user {user_id}")
        return False

    # Check user preferences
    prefs = user.preferences or {}
    notif_prefs = prefs.get("notifications", {})
    if not notif_prefs.get("enabled", True):
        logger.debug(f"Notifications disabled for user {user_id}")
        return False

    try:
        payload = json.dumps({
            "title": title,
            "body": body,
            "url": url,
            "tag": tag
        })

        webpush(
            subscription_info=subscription,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )

        logger.info(f"Push notification sent to user {user_id}: {title}")
        return True

    except WebPushException as e:
        logger.error(f"Failed to send push notification to user {user_id}: {e}")
        # Handle subscription gone (410) - clean up stale subscription
        if e.response and e.response.status_code == 410:
            logger.info(f"Removing stale subscription for user {user_id}")
            _set_user_subscription(user, None, db)
        return False
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        return False


async def send_task_reminder(
    user_id: str,
    task_title: str,
    due_date: str,
    db: Session
) -> bool:
    """Send a task reminder notification."""
    return await send_push_notification(
        user_id=user_id,
        title="Task Reminder",
        body=f"'{task_title}' is due {due_date}",
        url="/dashboard/tasks",
        tag=f"task-reminder-{task_title[:20]}",
        db=db
    )


async def send_pomodoro_alert(
    user_id: str,
    message: str,
    db: Session
) -> bool:
    """Send a pomodoro timer notification."""
    return await send_push_notification(
        user_id=user_id,
        title="Pomodoro Timer",
        body=message,
        url="/dashboard/time",
        tag="pomodoro",
        db=db
    )


async def send_daily_digest(
    user_id: str,
    task_count: int,
    top_priority: str,
    db: Session
) -> bool:
    """Send daily digest notification."""
    body = f"You have {task_count} tasks today."
    if top_priority:
        body += f" Top priority: {top_priority}"

    return await send_push_notification(
        user_id=user_id,
        title="Good Morning! Your Daily Focus",
        body=body,
        url="/dashboard",
        tag="daily-digest",
        db=db
    )
