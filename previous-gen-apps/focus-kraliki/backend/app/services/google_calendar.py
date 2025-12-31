"""
Google Calendar Sync Service
Bidirectional sync between Focus by Kraliki events and Google Calendar
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid
import logging

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Service for syncing events with Google Calendar.

    Features:
    - Two-way sync: Focus by Kraliki ↔ Google Calendar
    - Create events in Google Calendar
    - Fetch events from Google Calendar
    - Update existing events
    - Delete events
    - Sync task deadlines to calendar
    """

    def __init__(self, oauth_token: str, refresh_token: str = None):
        """
        Initialize Google Calendar service.

        Args:
            oauth_token: Google OAuth access token
            refresh_token: Google OAuth refresh token (for token renewal)
        """
        from app.core.config import settings

        creds = Credentials(
            token=oauth_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET
        )
        self.service = build('calendar', 'v3', credentials=creds)

    async def sync_events(
        self,
        user_id: str,
        calendar_id: str = 'primary',
        time_min: datetime = None,
        time_max: datetime = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch events from Google Calendar.

        Args:
            user_id: User ID for database storage
            calendar_id: Google Calendar ID (default: 'primary')
            time_min: Minimum event start time (default: now)
            time_max: Maximum event end time (default: 30 days from now)
            max_results: Maximum number of events to fetch

        Returns:
            List of event dictionaries ready for database insertion
        """
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = datetime.utcnow() + timedelta(days=30)

        try:
            # Fetch events from Google Calendar
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            google_events = events_result.get('items', [])

            # Convert to Focus by Kraliki event format
            focus_events = []
            for gevent in google_events:
                focus_event = self._google_to_focus_event(gevent, user_id, calendar_id)
                focus_events.append(focus_event)

            return focus_events

        except HttpError as error:
            logger.error(f"Google Calendar API error: {error}")
            raise

    def _google_to_focus_event(
        self,
        google_event: Dict[str, Any],
        user_id: str,
        calendar_id: str
    ) -> Dict[str, Any]:
        """
        Convert Google Calendar event to Focus by Kraliki event format.

        Args:
            google_event: Google Calendar API event object
            user_id: User ID
            calendar_id: Google Calendar ID

        Returns:
            Dictionary matching Focus by Kraliki Event model
        """
        # Extract start/end times
        start = google_event['start'].get('dateTime', google_event['start'].get('date'))
        end = google_event['end'].get('dateTime', google_event['end'].get('date'))
        all_day = 'date' in google_event['start']

        # Parse datetime strings
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))

        # Extract attendees
        attendees = [
            attendee.get('email')
            for attendee in google_event.get('attendees', [])
        ]

        return {
            'id': str(uuid.uuid4()),  # Generate new Focus by Kraliki ID
            'user_id': user_id,
            'title': google_event.get('summary', 'Untitled Event'),
            'description': google_event.get('description', ''),
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'google_event_id': google_event['id'],
            'google_calendar_id': calendar_id,
            'location': google_event.get('location'),
            'attendees': attendees if attendees else None,
            'color': google_event.get('colorId'),
        }

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: str = None,
        location: str = None,
        attendees: List[str] = None,
        calendar_id: str = 'primary'
    ) -> str:
        """
        Create event in Google Calendar.

        Args:
            title: Event title
            start_time: Event start datetime
            end_time: Event end datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Google Calendar ID

        Returns:
            Google Calendar event ID
        """
        event = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            return created_event['id']

        except HttpError as error:
            logger.error(f"Error creating Google Calendar event: {error}")
            raise

    async def update_event(
        self,
        google_event_id: str,
        title: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        description: str = None,
        location: str = None,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Update existing Google Calendar event.

        Args:
            google_event_id: Google Calendar event ID
            title: Updated title
            start_time: Updated start time
            end_time: Updated end time
            description: Updated description
            location: Updated location
            calendar_id: Google Calendar ID

        Returns:
            True if successful
        """
        try:
            # Fetch current event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=google_event_id
            ).execute()

            # Update fields
            if title:
                event['summary'] = title
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }

            # Update event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=google_event_id,
                body=event
            ).execute()

            return True

        except HttpError as error:
            logger.error(f"Error updating Google Calendar event: {error}")
            return False

    async def delete_event(
        self,
        google_event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Delete event from Google Calendar.

        Args:
            google_event_id: Google Calendar event ID
            calendar_id: Google Calendar ID

        Returns:
            True if successful
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=google_event_id
            ).execute()

            return True

        except HttpError as error:
            logger.error(f"Error deleting Google Calendar event: {error}")
            return False

    async def sync_task_deadline(
        self,
        task_id: str,
        task_title: str,
        due_date: datetime,
        duration_minutes: int = 60,
        description: str = None,
        calendar_id: str = 'primary'
    ) -> str:
        """
        Create Google Calendar event from task deadline.

        Args:
            task_id: Task ID (stored in event description)
            task_title: Task title
            due_date: Task due date
            duration_minutes: Estimated task duration
            description: Task description
            calendar_id: Google Calendar ID

        Returns:
            Google Calendar event ID
        """
        end_time = due_date + timedelta(minutes=duration_minutes)

        event_description = f"Task: {task_title}"
        if description:
            event_description += f"\n\n{description}"
        event_description += f"\n\nTask ID: {task_id}"

        return await self.create_event(
            title=f"📋 {task_title}",
            start_time=due_date,
            end_time=end_time,
            description=event_description,
            calendar_id=calendar_id
        )
