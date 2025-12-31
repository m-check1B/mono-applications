"""
Google Calendar Two-Way Sync Router
Addresses CR-002 from BACKLOG.md (P0: Critical for all user segments)

Features:
- OAuth 2.0 authentication with Google Calendar
- Two-way sync: Tasks <-> Calendar Events
- Automatic sync on schedule
- Manual sync triggers
- Webhook support for real-time updates
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    BackgroundTasks,
    Header,
    Request,
)
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import httpx
import logging

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.core.config import settings
from app.core.webhook_security import google_webhook_verifier
from app.middleware.rate_limit import limiter
from app.core.conflict_resolution import (
    ConflictResolver,
    ConflictResolutionPolicy,
    ConflictType,
    SyncConflict,
)
from app.models.user import User
from app.models.task import Task, Project, TaskStatus
from app.models.event import Event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calendar-sync", tags=["calendar-integration"])


class CalendarOAuthRequest(BaseModel):
    """Request to initiate Google Calendar OAuth"""

    redirect_uri: str = Field(..., description="OAuth redirect URI")


class CalendarOAuthResponse(BaseModel):
    """OAuth URL response"""

    auth_url: str
    state: str


class CalendarTokenExchange(BaseModel):
    """Exchange authorization code for tokens"""

    code: str
    redirect_uri: str


class CalendarTokenResponse(BaseModel):
    """OAuth token response"""

    access_token: str
    refresh_token: Optional[str]
    expires_in: int
    token_type: str


class CalendarSyncError(BaseModel):
    """Calendar sync error details"""

    code: str
    message: str
    timestamp: datetime
    recoverable: bool = True


class CalendarSyncStatus(BaseModel):
    """Calendar sync status"""

    enabled: bool
    connected: bool
    last_sync: Optional[datetime]
    sync_direction: str  # "one-way", "two-way"
    calendars: List[dict]
    last_error: Optional[CalendarSyncError] = None


class CalendarSyncRequest(BaseModel):
    """Manual sync request"""

    direction: Optional[str] = Field(
        "both", description="Sync direction: 'to_calendar', 'from_calendar', or 'both'"
    )
    start_date: Optional[str] = Field(
        None, description="Sync from this date (ISO format)"
    )
    end_date: Optional[str] = Field(
        None, description="Sync until this date (ISO format)"
    )


# In-memory storage for OAuth states (replace with Redis in production)
_oauth_states = {}


@router.post("/oauth/init", response_model=CalendarOAuthResponse)
@limiter.limit("5/minute")  # Rate limit OAuth init - sensitive operation
async def init_calendar_oauth(
    http_request: Request,
    request: CalendarOAuthRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initialize Google Calendar OAuth flow.

    Returns an authorization URL that the user should visit to grant permissions.
    Required scopes: calendar.events.readonly, calendar.events
    """
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    # Generate state for CSRF protection
    import secrets

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {"user_id": current_user.id, "timestamp": datetime.utcnow()}

    # Build OAuth URL with calendar scopes
    scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]
    scope_string = " ".join(scopes)

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_OAUTH_CLIENT_ID}&"
        f"redirect_uri={request.redirect_uri}&"
        f"response_type=code&"
        f"scope={scope_string}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={state}"
    )

    return CalendarOAuthResponse(auth_url=auth_url, state=state)


@router.post("/oauth/exchange", response_model=CalendarTokenResponse)
@limiter.limit("5/minute")  # Rate limit OAuth exchange - sensitive operation
async def exchange_calendar_token(
    http_request: Request,
    request: CalendarTokenExchange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Exchange authorization code for access and refresh tokens.

    Store tokens securely in user preferences for future sync operations.
    """
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": request.code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": request.redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=400, detail="Failed to exchange authorization code"
            )

        token_data = response.json()

    # Store tokens in user preferences (encrypted in production!)
    prefs = current_user.preferences or {}
    prefs["calendar_sync"] = {
        "enabled": True,
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "expires_at": (
            datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        ).isoformat(),
        "sync_direction": "two-way",
        "last_sync": None,
    }
    current_user.preferences = prefs
    db.commit()

    return CalendarTokenResponse(
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        expires_in=token_data["expires_in"],
        token_type=token_data.get("token_type", "Bearer"),
    )


@router.get("/status", response_model=CalendarSyncStatus)
async def get_calendar_sync_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current calendar sync status for the user.

    Shows:
    - Whether sync is enabled and connected
    - Last sync timestamp
    - Sync direction (one-way vs two-way)
    - Available calendars
    """
    prefs = current_user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})

    enabled = calendar_sync.get("enabled", False)
    connected = enabled and "access_token" in calendar_sync

    # Parse last sync
    last_sync = None
    if calendar_sync.get("last_sync"):
        try:
            last_sync = datetime.fromisoformat(calendar_sync["last_sync"])
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse last_sync timestamp: {e}")

    # Get calendars list (if connected)
    calendars = []
    current_error = None

    if connected:
        # Fetch calendar list from Google Calendar API
        access_token = calendar_sync.get("access_token")
        if access_token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://www.googleapis.com/calendar/v3/users/me/calendarList",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )

                    if response.status_code == 200:
                        calendar_data = response.json()
                        for cal in calendar_data.get("items", []):
                            calendars.append(
                                {
                                    "id": cal.get("id"),
                                    "name": cal.get("summary", "Unnamed Calendar"),
                                    "color": cal.get("backgroundColor", "#3B82F6"),
                                    "primary": cal.get("primary", False),
                                }
                            )
                    elif response.status_code == 401:
                        # Token expired or invalid
                        logger.error(
                            f"Calendar API auth failed (401): token may be expired"
                        )
                        current_error = CalendarSyncError(
                            code="auth_expired",
                            message="Google Calendar authorization expired. Please reconnect your calendar.",
                            timestamp=datetime.utcnow(),
                            recoverable=True,
                        )
                    elif response.status_code == 403:
                        # Permission denied
                        logger.error(
                            f"Calendar API permission denied (403): {response.text}"
                        )
                        current_error = CalendarSyncError(
                            code="permission_denied",
                            message="Access to Google Calendar was denied. Please reconnect with required permissions.",
                            timestamp=datetime.utcnow(),
                            recoverable=True,
                        )
                    else:
                        # Other API error
                        logger.error(
                            f"Calendar API error ({response.status_code}): {response.text}"
                        )
                        current_error = CalendarSyncError(
                            code="api_error",
                            message=f"Google Calendar API returned error {response.status_code}",
                            timestamp=datetime.utcnow(),
                            recoverable=True,
                        )
            except httpx.TimeoutException as e:
                logger.error(f"Calendar API timeout: {e}")
                current_error = CalendarSyncError(
                    code="timeout",
                    message="Google Calendar API timed out. Please try again later.",
                    timestamp=datetime.utcnow(),
                    recoverable=True,
                )
            except httpx.ConnectError as e:
                logger.error(f"Calendar API connection error: {e}")
                current_error = CalendarSyncError(
                    code="connection_error",
                    message="Could not connect to Google Calendar. Please check your network connection.",
                    timestamp=datetime.utcnow(),
                    recoverable=True,
                )
            except Exception as e:
                logger.error(
                    f"Unexpected error fetching calendar list: {type(e).__name__}: {e}"
                )
                current_error = CalendarSyncError(
                    code="unexpected_error",
                    message=f"An unexpected error occurred: {type(e).__name__}",
                    timestamp=datetime.utcnow(),
                    recoverable=False,
                )

    # Also check for stored errors from background sync
    last_error = current_error
    if not last_error and calendar_sync.get("last_error"):
        stored_error = calendar_sync["last_error"]
        try:
            last_error = CalendarSyncError(
                code=stored_error.get("code", "unknown"),
                message=stored_error.get("message", "Unknown error"),
                timestamp=datetime.fromisoformat(stored_error["timestamp"])
                if stored_error.get("timestamp")
                else datetime.utcnow(),
                recoverable=stored_error.get("recoverable", True),
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse stored error: {e}")

    return CalendarSyncStatus(
        enabled=enabled,
        connected=connected,
        last_sync=last_sync,
        sync_direction=calendar_sync.get("sync_direction", "two-way"),
        calendars=calendars,
        last_error=last_error,
    )


@router.post("/sync")
@limiter.limit("5/minute")  # Rate limit sync - makes external API calls
async def sync_calendar(
    http_request: Request,
    request: CalendarSyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually trigger calendar sync.

    Sync directions:
    - 'to_calendar': Push Focus tasks to Google Calendar
    - 'from_calendar': Pull Google Calendar events to Focus tasks
    - 'both': Two-way sync (default)

    Background task performs the actual sync to avoid blocking.

    Prerequisites:
    1. Google OAuth must be configured on the server (GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET)
    2. User must complete OAuth flow via POST /calendar-sync/oauth/init and /oauth/exchange
    3. Calendar sync must be enabled in user preferences
    """
    # Check if Google OAuth is configured on the server
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "google_oauth_not_configured",
                "message": "Google OAuth is not configured on this server. Please contact your administrator.",
                "hint": "Server needs GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables.",
            },
        )

    prefs = current_user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})

    # Check if calendar sync is enabled
    if not calendar_sync.get("enabled"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "calendar_sync_disabled",
                "message": "Calendar sync is disabled in your settings.",
                "hint": "Complete OAuth flow via POST /calendar-sync/oauth/init to connect your calendar.",
            },
        )

    # Check if user has connected their calendar (has access token)
    if not calendar_sync.get("access_token"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "calendar_not_connected",
                "message": "Your Google Calendar is not connected.",
                "hint": "Complete OAuth flow: 1) POST /calendar-sync/oauth/init, 2) Authorize in browser, 3) POST /calendar-sync/oauth/exchange with the code.",
            },
        )

    # Parse date range
    start_date = (
        datetime.fromisoformat(request.start_date)
        if request.start_date
        else datetime.now() - timedelta(days=7)
    )
    end_date = (
        datetime.fromisoformat(request.end_date)
        if request.end_date
        else datetime.now() + timedelta(days=30)
    )

    # Queue background sync
    background_tasks.add_task(
        perform_calendar_sync,
        user_id=current_user.id,
        access_token=calendar_sync["access_token"],
        direction=request.direction,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "success": True,
        "message": "Calendar sync started in background",
        "direction": request.direction,
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
    }


@router.post("/disconnect")
async def disconnect_calendar(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Disconnect Google Calendar integration.

    Removes stored tokens and disables sync.
    """
    prefs = current_user.preferences or {}
    if "calendar_sync" in prefs:
        prefs["calendar_sync"] = {"enabled": False}
        current_user.preferences = prefs
        db.commit()

    return {"success": True, "message": "Calendar disconnected successfully"}


@router.delete("/error")
async def clear_calendar_error(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Clear the last calendar sync error.

    Call this after the user has acknowledged/seen the error.
    """
    prefs = current_user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})

    if "last_error" in calendar_sync:
        del calendar_sync["last_error"]
        prefs["calendar_sync"] = calendar_sync
        current_user.preferences = prefs
        db.commit()
        return {"success": True, "message": "Calendar sync error cleared"}

    return {"success": True, "message": "No error to clear"}


@router.post("/webhook")
@limiter.limit("100/minute")  # Rate limit webhook - allow Google's burst but prevent abuse
async def calendar_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    x_goog_resource_id: Optional[str] = Header(None),
    x_goog_resource_state: Optional[str] = Header(None),
    x_goog_channel_id: Optional[str] = Header(None),
    x_goog_channel_expiration: Optional[str] = Header(None),
    x_goog_channel_token: Optional[str] = Header(None),
    x_goog_message_number: Optional[str] = Header(None),
):
    """
    Webhook endpoint for Google Calendar push notifications.

    Google Calendar sends push notifications via webhooks when calendar events change.
    This enables real-time two-way sync without polling.

    Setup process:
    1. Register this webhook URL with Google Cloud Console
    2. Call Google Calendar API to watch calendar changes
    3. Google sends notifications to this endpoint when events change

    Security:
    - Verifies X-Goog-Channel-* headers
    - Validates channel ID and expiration
    - Optional token-based authentication

    Push notification states:
    - sync: Initial sync notification (can be ignored)
    - exists: Resource change notification (trigger sync)
    - not_exists: Resource deleted (cleanup)
    """
    # Verify Google Calendar webhook headers
    try:
        webhook_data = google_webhook_verifier.verify_google_calendar_webhook(
            x_goog_resource_id=x_goog_resource_id,
            x_goog_resource_state=x_goog_resource_state,
            x_goog_channel_id=x_goog_channel_id,
            x_goog_channel_expiration=x_goog_channel_expiration,
            x_goog_channel_token=x_goog_channel_token,
            x_goog_message_number=x_goog_message_number,
        )
    except HTTPException as e:
        logger.error(f"Google Calendar webhook verification failed: {e.detail}")
        raise

    channel_id = webhook_data["channel_id"]
    resource_state = webhook_data["resource_state"]
    resource_id = webhook_data["resource_id"]

    logger.info(
        f"Google Calendar webhook: channel={channel_id}, state={resource_state}, resource={resource_id}"
    )

    # Find user associated with this channel
    # Channel ID format: "user_{user_id}_calendar_{calendar_id}"
    user_id = None
    if channel_id.startswith("user_"):
        parts = channel_id.split("_")
        if len(parts) >= 2:
            user_id = parts[1]

    if not user_id:
        logger.warning(f"Could not extract user_id from channel_id: {channel_id}")
        # Still return 200 to acknowledge receipt
        return {"success": True, "message": "Webhook received but user not found"}

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User not found for calendar webhook: {user_id}")
        return {"success": True, "message": "Webhook received but user not found"}

    # Check if user has calendar sync enabled
    prefs = user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})

    if not calendar_sync.get("enabled"):
        logger.info(f"Calendar sync not enabled for user {user_id}, ignoring webhook")
        return {"success": True, "message": "Calendar sync not enabled"}

    # Store webhook delivery metadata
    webhook_deliveries = calendar_sync.get("webhook_deliveries", [])
    webhook_deliveries.append(
        {
            "channel_id": channel_id,
            "resource_state": resource_state,
            "resource_id": resource_id,
            "message_number": webhook_data.get("message_number"),
            "received_at": datetime.utcnow().isoformat(),
        }
    )

    # Keep only last 50 deliveries
    calendar_sync["webhook_deliveries"] = webhook_deliveries[-50:]

    # Update last webhook time
    calendar_sync["last_webhook"] = datetime.utcnow().isoformat()

    # Update channel expiration if provided
    if x_goog_channel_expiration:
        calendar_sync["channel_expiration"] = x_goog_channel_expiration

    prefs["calendar_sync"] = calendar_sync
    user.preferences = prefs
    db.commit()

    # Handle different resource states
    if resource_state == "sync":
        # Initial sync notification - acknowledge but don't sync
        logger.info(f"Calendar webhook sync state for user {user_id} - acknowledging")
        return {"success": True, "message": "Sync notification acknowledged"}

    elif resource_state == "exists":
        # Resource changed - trigger background sync
        logger.info(
            f"Calendar webhook change detected for user {user_id} - queueing sync"
        )

        # Queue background sync job
        background_tasks.add_task(
            perform_calendar_sync,
            user_id=user_id,
            access_token=calendar_sync.get("access_token"),
            direction="from_calendar",  # Only sync from calendar (webhook triggered by calendar change)
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now() + timedelta(days=30),
        )

        return {
            "success": True,
            "message": "Calendar change detected, sync queued",
            "channel_id": channel_id,
            "resource_state": resource_state,
        }

    elif resource_state == "not_exists":
        # Resource deleted - log but don't fail
        logger.info(f"Calendar webhook resource deleted for user {user_id}")
        return {"success": True, "message": "Resource deleted notification received"}

    else:
        logger.warning(f"Unknown calendar webhook resource_state: {resource_state}")
        return {"success": True, "message": f"Unknown resource state: {resource_state}"}


# Background sync implementation
async def perform_calendar_sync(
    user_id: str,
    access_token: str,
    direction: str,
    start_date: datetime,
    end_date: datetime,
):
    """
    Perform actual calendar sync in background.

    This function:
    1. Fetches Google Calendar events
    2. Compares with Focus tasks/events
    3. Creates/updates entries in both systems
    4. Handles conflicts using last-modified timestamps
    5. Stores any errors in user preferences for UI visibility
    """
    from app.core.database import SessionLocal

    db = SessionLocal()

    def store_sync_error(error_code: str, error_message: str, recoverable: bool = True):
        """Store sync error in user preferences for UI visibility."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                prefs = user.preferences or {}
                if "calendar_sync" not in prefs:
                    prefs["calendar_sync"] = {}
                prefs["calendar_sync"]["last_error"] = {
                    "code": error_code,
                    "message": error_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "recoverable": recoverable,
                }
                user.preferences = prefs
                db.commit()
        except Exception as store_err:
            logger.error(f"Failed to store sync error for user {user_id}: {store_err}")

    def clear_sync_error():
        """Clear any previous sync error on successful sync."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                prefs = user.preferences or {}
                if "calendar_sync" in prefs and "last_error" in prefs["calendar_sync"]:
                    del prefs["calendar_sync"]["last_error"]
                    user.preferences = prefs
                    db.commit()
        except Exception as clear_err:
            logger.warning(
                f"Failed to clear sync error for user {user_id}: {clear_err}"
            )

    try:
        logger.info(
            f"Starting calendar sync for user {user_id}, direction: {direction}"
        )

        # Fetch user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for calendar sync")
            return

        # Sync from calendar to Focus
        if direction in ["from_calendar", "both"]:
            await sync_from_calendar(db, user, access_token, start_date, end_date)

        # Sync from Focus to calendar
        if direction in ["to_calendar", "both"]:
            await sync_to_calendar(db, user, access_token, start_date, end_date)

        # Update last sync timestamp and clear any previous errors
        prefs = user.preferences or {}
        if "calendar_sync" in prefs:
            prefs["calendar_sync"]["last_sync"] = datetime.utcnow().isoformat()
            # Clear previous error on success
            if "last_error" in prefs["calendar_sync"]:
                del prefs["calendar_sync"]["last_error"]
            user.preferences = prefs
            db.commit()

        logger.info(f"Calendar sync completed for user {user_id}")

    except httpx.TimeoutException as e:
        error_msg = (
            "Calendar sync timed out. Google Calendar API is slow or unreachable."
        )
        logger.error(f"Calendar sync timeout for user {user_id}: {e}")
        store_sync_error("sync_timeout", error_msg, recoverable=True)
        db.rollback()

    except httpx.ConnectError as e:
        error_msg = "Could not connect to Google Calendar. Please check your network connection."
        logger.error(f"Calendar sync connection error for user {user_id}: {e}")
        store_sync_error("sync_connection_error", error_msg, recoverable=True)
        db.rollback()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            error_msg = (
                "Google Calendar authorization expired. Please reconnect your calendar."
            )
            logger.error(f"Calendar sync auth error for user {user_id}: {e}")
            store_sync_error("sync_auth_expired", error_msg, recoverable=True)
        elif e.response.status_code == 403:
            error_msg = "Access to Google Calendar was denied. Please reconnect with required permissions."
            logger.error(f"Calendar sync permission error for user {user_id}: {e}")
            store_sync_error("sync_permission_denied", error_msg, recoverable=True)
        elif e.response.status_code == 429:
            error_msg = (
                "Too many requests to Google Calendar. Sync will retry automatically."
            )
            logger.warning(f"Calendar sync rate limited for user {user_id}: {e}")
            store_sync_error("sync_rate_limited", error_msg, recoverable=True)
        else:
            error_msg = f"Google Calendar API error ({e.response.status_code}). Please try again later."
            logger.error(f"Calendar sync HTTP error for user {user_id}: {e}")
            store_sync_error("sync_api_error", error_msg, recoverable=True)
        db.rollback()

    except Exception as e:
        error_msg = f"Unexpected sync error: {type(e).__name__}. Please contact support if this persists."
        logger.error(
            f"Calendar sync failed for user {user_id}: {type(e).__name__}: {e}",
            exc_info=True,
        )
        store_sync_error("sync_unexpected_error", error_msg, recoverable=False)
        db.rollback()

    finally:
        db.close()


async def sync_from_calendar(
    db: Session, user: User, access_token: str, start_date: datetime, end_date: datetime
):
    """
    Sync events from Google Calendar to Focus with advanced conflict handling.

    Creates or updates tasks for calendar events, detecting and resolving conflicts.
    """
    # Get conflict resolution policy from user preferences
    prefs = user.preferences or {}
    calendar_sync = prefs.get("calendar_sync", {})
    policy_str = calendar_sync.get("conflict_resolution_policy", "last_modified_wins")

    try:
        policy = ConflictResolutionPolicy(policy_str)
    except ValueError as e:
        logger.warning(
            f"Invalid conflict resolution policy '{policy_str}': {e}, using default LAST_MODIFIED_WINS"
        )
        policy = ConflictResolutionPolicy.LAST_MODIFIED_WINS

    # Get last sync time for conflict detection
    last_sync_time = None
    if calendar_sync.get("last_sync"):
        try:
            last_sync_time = datetime.fromisoformat(calendar_sync["last_sync"])
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse last_sync timestamp: {e}")

    # Initialize conflict resolver
    resolver = ConflictResolver(policy=policy)

    # Fetch calendar events from Google
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "timeMin": start_date.isoformat() + "Z",
                "timeMax": end_date.isoformat() + "Z",
                "singleEvents": True,
                "orderBy": "startTime",
            },
        )

        if response.status_code != 200:
            logger.error(f"Failed to fetch calendar events: {response.text}")
            # Raise as HTTPStatusError so it's caught by the parent handler
            response.raise_for_status()

        events_data = response.json()

    conflicts_detected = []
    events_synced = 0
    events_skipped = []

    # Process each calendar event
    for event_data in events_data.get("items", []):
        event_id = event_data.get("id")
        title = event_data.get("summary", "Untitled Event")
        description = event_data.get("description", "")

        # Parse start/end times
        start = event_data.get("start", {})
        start_time = start.get("dateTime") or start.get("date")

        # Skip events without valid start time
        if not start_time:
            logger.warning(f"Skipping event {event_id} ({title}): missing start time")
            events_skipped.append({"id": event_id, "title": title, "reason": "missing_start_time"})
            continue

        # Check if event already exists in Focus
        existing = (
            db.query(Event)
            .filter(Event.user_id == user.id, Event.google_event_id == event_id)
            .first()
        )

        if existing:
            # Event exists - check for conflicts
            focus_item = {
                "id": existing.id,
                "title": existing.title,
                "description": existing.description,
                "dueDate": existing.start_time,
                "endDate": existing.end_time,
                "updatedAt": existing.updated_at
                if hasattr(existing, "updated_at")
                else existing.created_at,
            }

            conflict = resolver.detect_conflicts(
                focus_item=focus_item,
                calendar_item=event_data,
                last_sync_time=last_sync_time,
            )

            if conflict:
                # Conflict detected - resolve it
                winning_side, resolved_data = resolver.resolve_conflict(conflict)

                if winning_side == "manual":
                    # Store for UI review
                    conflicts_detected.append(resolved_data)
                    logger.info(
                        f"Conflict detected for event {event_id}, pending manual resolution"
                    )
                elif winning_side == "calendar":
                    # Update Focus event with calendar data
                    existing.title = title
                    existing.description = description
                    if start_time:
                        existing.start_time = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                    end = event_data.get("end", {})
                    end_time = end.get("dateTime") or end.get("date")
                    if end_time:
                        existing.end_time = datetime.fromisoformat(
                            end_time.replace("Z", "+00:00")
                        )
                    logger.info(
                        f"Conflict resolved: calendar wins for event {event_id}"
                    )
                elif winning_side == "focus":
                    # Keep Focus data, don't update
                    logger.info(f"Conflict resolved: focus wins for event {event_id}")
                elif winning_side == "merged":
                    # Apply merged data
                    if "title" in resolved_data:
                        existing.title = resolved_data["title"]
                    if "description" in resolved_data:
                        existing.description = resolved_data["description"]
                    if "dueDate" in resolved_data:
                        existing.start_time = resolved_data["dueDate"]
                    if "endDate" in resolved_data:
                        existing.end_time = resolved_data["endDate"]
                    logger.info(f"Conflict resolved: merged for event {event_id}")
            else:
                # No conflict - update normally
                existing.title = title
                existing.description = description
                if start_time:
                    existing.start_time = datetime.fromisoformat(
                        start_time.replace("Z", "+00:00")
                    )
                end = event_data.get("end", {})
                end_time = end.get("dateTime") or end.get("date")
                if end_time:
                    existing.end_time = datetime.fromisoformat(
                        end_time.replace("Z", "+00:00")
                    )

            events_synced += 1

        else:
            # Create new event in Focus
            end = event_data.get("end", {})
            end_time = end.get("dateTime") or end.get("date")

            try:
                parsed_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                parsed_end = (
                    datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    if end_time
                    else parsed_start
                )
            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Skipping event {event_id} ({title}): invalid date format - {e}"
                )
                events_skipped.append({
                    "id": event_id,
                    "title": title,
                    "reason": "invalid_date_format",
                    "error": str(e),
                })
                continue

            new_event = Event(
                id=generate_id(),
                user_id=user.id,
                title=title,
                description=description,
                start_time=parsed_start,
                end_time=parsed_end,
                google_event_id=event_id,
                created_at=datetime.utcnow(),
            )
            db.add(new_event)
            events_synced += 1

    # Store skipped events in user preferences for UI visibility
    if events_skipped:
        calendar_sync["last_sync_skipped"] = events_skipped
        logger.info(f"Skipped {len(events_skipped)} events due to validation errors")

    # Store conflicts in user preferences for UI review
    if conflicts_detected:
        calendar_sync["pending_conflicts"] = conflicts_detected
        prefs["calendar_sync"] = calendar_sync
        user.preferences = prefs

    db.commit()
    logger.info(
        f"Synced {events_synced} events from calendar, "
        f"{len(conflicts_detected)} conflicts pending, "
        f"{len(events_skipped)} events skipped"
    )


async def sync_to_calendar(
    db: Session, user: User, access_token: str, start_date: datetime, end_date: datetime
):
    """
    Sync Focus tasks/events to Google Calendar.

    Creates calendar events for tasks with due dates that don't exist yet.
    """
    # Fetch tasks with due dates
    tasks = (
        db.query(Task)
        .filter(
            Task.userId == user.id,
            Task.dueDate.isnot(None),
            Task.dueDate >= start_date,
            Task.dueDate <= end_date,
            Task.status != TaskStatus.COMPLETED,
        )
        .all()
    )

    tasks_failed = []

    async with httpx.AsyncClient() as client:
        for task in tasks:
            # Check if task already synced to calendar
            if task.google_calendar_id:
                continue

            # Create calendar event
            event_data = {
                "summary": task.title,
                "description": task.description or "",
                "start": {"dateTime": task.dueDate.isoformat(), "timeZone": "UTC"},
                "end": {
                    "dateTime": (task.dueDate + timedelta(hours=1)).isoformat(),
                    "timeZone": "UTC",
                },
            }

            response = await client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=event_data,
            )

            if response.status_code in (200, 201):
                created_event = response.json()
                task.google_calendar_id = created_event["id"]
                logger.info(f"Created calendar event for task {task.id}")
            elif response.status_code in (401, 403):
                # Auth error - propagate to parent handler
                logger.error(
                    f"Calendar API auth error for task {task.id}: {response.status_code}"
                )
                response.raise_for_status()
            else:
                # Track non-fatal errors for UI visibility
                error_info = {
                    "task_id": task.id,
                    "task_title": task.title,
                    "status_code": response.status_code,
                    "error": response.text[:200] if response.text else "Unknown error",
                }
                tasks_failed.append(error_info)
                logger.warning(
                    f"Failed to create calendar event for task {task.id}: "
                    f"{response.status_code} - {response.text}"
                )

    # Store failed tasks in user preferences for UI visibility
    if tasks_failed:
        prefs = user.preferences or {}
        calendar_sync = prefs.get("calendar_sync", {})
        calendar_sync["last_sync_failed_tasks"] = tasks_failed
        prefs["calendar_sync"] = calendar_sync
        user.preferences = prefs
        logger.info(f"{len(tasks_failed)} tasks failed to sync to calendar")

    tasks_synced = len([t for t in tasks if t.google_calendar_id])
    db.commit()
    logger.info(
        f"Synced {tasks_synced} of {len(tasks)} tasks to calendar, "
        f"{len(tasks_failed)} tasks failed"
    )
