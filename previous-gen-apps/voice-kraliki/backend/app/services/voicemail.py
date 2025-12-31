"""Voicemail Service.

Handles voicemail messages, mailboxes, greetings, and notifications.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.voicemail import (
    GreetingCreate,
    NotificationChannel,
    Voicemail,
    VoicemailBox,
    VoicemailBoxCreate,
    VoicemailBoxUpdate,
    VoicemailCreate,
    VoicemailGreeting,
    VoicemailNotification,
    VoicemailStatus,
    VoicemailUpdate,
)

logger = logging.getLogger(__name__)


class VoicemailError(Exception):
    """Base exception for voicemail errors."""
    pass


class VoicemailService:
    """Service for managing voicemail."""

    def __init__(self, db: Session):
        self.db = db

    # ===== Voicemail Message Management =====

    def create_voicemail(self, voicemail_data: VoicemailCreate) -> Voicemail:
        """Create a new voicemail message."""
        # Verify mailbox exists
        mailbox = self.get_mailbox_by_agent(voicemail_data.agent_id)
        if not mailbox:
            # Auto-create mailbox if it doesn't exist
            mailbox = self.create_mailbox(VoicemailBoxCreate(
                agent_id=voicemail_data.agent_id,
                team_id=voicemail_data.team_id
            ))

        # Check mailbox capacity
        if mailbox.total_messages >= mailbox.max_messages:
            raise VoicemailError(f"Mailbox full (max: {mailbox.max_messages} messages)")

        # Calculate expiration
        expires_at = datetime.now(UTC) + timedelta(days=voicemail_data.retention_days)

        voicemail = Voicemail(
            agent_id=voicemail_data.agent_id,
            team_id=voicemail_data.team_id,
            call_sid=voicemail_data.call_sid,
            caller_phone=voicemail_data.caller_phone,
            caller_name=voicemail_data.caller_name,
            recording_url=voicemail_data.recording_url,
            recording_duration_seconds=voicemail_data.recording_duration_seconds,
            recording_format=voicemail_data.recording_format,
            storage_provider=voicemail_data.storage_provider,
            storage_key=voicemail_data.storage_key,
            priority=voicemail_data.priority,
            retention_days=voicemail_data.retention_days,
            expires_at=expires_at,
            status=VoicemailStatus.NEW.value
        )

        self.db.add(voicemail)

        # Update mailbox stats
        mailbox.total_messages += 1
        mailbox.unheard_messages += 1

        self.db.commit()
        self.db.refresh(voicemail)

        logger.info(f"Created voicemail for agent {voicemail_data.agent_id} from {voicemail_data.caller_phone}")

        # Send notifications
        if mailbox.notification_enabled:
            self._send_notifications(voicemail, mailbox)

        return voicemail

    def get_voicemail(self, voicemail_id: int) -> Voicemail | None:
        """Get a voicemail by ID."""
        return self.db.query(Voicemail).filter(
            Voicemail.id == voicemail_id,
            Voicemail.deleted_at == None
        ).first()

    def list_voicemails(
        self,
        agent_id: int,
        status: VoicemailStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Voicemail]:
        """List voicemails for an agent."""
        query = self.db.query(Voicemail).filter(
            Voicemail.agent_id == agent_id,
            Voicemail.deleted_at == None
        )

        if status:
            query = query.filter(Voicemail.status == status.value)

        return query.order_by(Voicemail.created_at.desc()).offset(skip).limit(limit).all()

    def update_voicemail(self, voicemail_id: int, voicemail_data: VoicemailUpdate) -> Voicemail | None:
        """Update a voicemail."""
        voicemail = self.get_voicemail(voicemail_id)
        if not voicemail:
            return None

        old_status = voicemail.status
        update_data = voicemail_data.model_dump(exclude_unset=True)

        # Convert status enum if provided
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            setattr(voicemail, field, value)

        voicemail.updated_at = datetime.now(UTC)

        # Update mailbox stats if status changed
        if voicemail_data.status and old_status != voicemail.status:
            mailbox = self.get_mailbox_by_agent(voicemail.agent_id)
            if mailbox:
                # Decrement unheard count if message was marked as heard/saved
                if old_status == VoicemailStatus.NEW.value and voicemail.status in [VoicemailStatus.HEARD.value, VoicemailStatus.SAVED.value]:
                    mailbox.unheard_messages = max(0, mailbox.unheard_messages - 1)

        self.db.commit()
        self.db.refresh(voicemail)

        logger.info(f"Updated voicemail {voicemail_id} (status: {old_status} -> {voicemail.status})")
        return voicemail

    def mark_as_heard(self, voicemail_id: int) -> Voicemail | None:
        """Mark a voicemail as heard."""
        voicemail = self.get_voicemail(voicemail_id)
        if not voicemail:
            return None

        if voicemail.status == VoicemailStatus.NEW.value:
            voicemail.status = VoicemailStatus.HEARD.value
            voicemail.first_heard_at = datetime.now(UTC)

            # Update mailbox stats
            mailbox = self.get_mailbox_by_agent(voicemail.agent_id)
            if mailbox:
                mailbox.unheard_messages = max(0, mailbox.unheard_messages - 1)

        voicemail.play_count += 1
        voicemail.last_heard_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(voicemail)

        logger.info(f"Marked voicemail {voicemail_id} as heard (play count: {voicemail.play_count})")
        return voicemail

    def delete_voicemail(self, voicemail_id: int, hard_delete: bool = False) -> bool:
        """Delete a voicemail."""
        voicemail = self.get_voicemail(voicemail_id)
        if not voicemail:
            return False

        if hard_delete:
            # Hard delete
            self.db.delete(voicemail)
            logger.info(f"Hard deleted voicemail {voicemail_id}")
        else:
            # Soft delete
            voicemail.status = VoicemailStatus.DELETED.value
            voicemail.deleted_at = datetime.now(UTC)
            logger.info(f"Soft deleted voicemail {voicemail_id}")

        # Update mailbox stats
        mailbox = self.get_mailbox_by_agent(voicemail.agent_id)
        if mailbox:
            mailbox.total_messages = max(0, mailbox.total_messages - 1)
            if voicemail.status == VoicemailStatus.NEW.value:
                mailbox.unheard_messages = max(0, mailbox.unheard_messages - 1)

        self.db.commit()
        return True

    def bulk_mark(self, voicemail_ids: list[int], status: VoicemailStatus, agent_id: int) -> int:
        """Bulk update voicemail status."""
        voicemails = self.db.query(Voicemail).filter(
            Voicemail.id.in_(voicemail_ids),
            Voicemail.agent_id == agent_id,
            Voicemail.deleted_at == None
        ).all()

        count = 0
        for voicemail in voicemails:
            voicemail.status = status.value
            voicemail.updated_at = datetime.now(UTC)
            count += 1

        self.db.commit()

        logger.info(f"Bulk updated {count} voicemails to status {status.value}")
        return count

    # ===== Mailbox Management =====

    def create_mailbox(self, mailbox_data: VoicemailBoxCreate) -> VoicemailBox:
        """Create a voicemail mailbox for an agent."""
        # Check if mailbox already exists
        existing = self.get_mailbox_by_agent(mailbox_data.agent_id)
        if existing:
            raise VoicemailError(f"Mailbox already exists for agent {mailbox_data.agent_id}")

        mailbox = VoicemailBox(
            agent_id=mailbox_data.agent_id,
            team_id=mailbox_data.team_id,
            is_enabled=mailbox_data.is_enabled,
            max_message_duration=mailbox_data.max_message_duration,
            max_messages=mailbox_data.max_messages,
            greeting_type=mailbox_data.greeting_type.value,
            notification_enabled=mailbox_data.notification_enabled,
            notification_channels=[ch.value for ch in mailbox_data.notification_channels],
            notification_email=mailbox_data.notification_email,
            notification_phone=mailbox_data.notification_phone,
            email_attachments=mailbox_data.email_attachments,
            email_transcription=mailbox_data.email_transcription
        )

        self.db.add(mailbox)
        self.db.commit()
        self.db.refresh(mailbox)

        logger.info(f"Created mailbox for agent {mailbox_data.agent_id}")
        return mailbox

    def get_mailbox(self, mailbox_id: int) -> VoicemailBox | None:
        """Get a mailbox by ID."""
        return self.db.query(VoicemailBox).filter(VoicemailBox.id == mailbox_id).first()

    def get_mailbox_by_agent(self, agent_id: int) -> VoicemailBox | None:
        """Get a mailbox by agent ID."""
        return self.db.query(VoicemailBox).filter(VoicemailBox.agent_id == agent_id).first()

    def update_mailbox(self, mailbox_id: int, mailbox_data: VoicemailBoxUpdate) -> VoicemailBox | None:
        """Update a mailbox."""
        mailbox = self.get_mailbox(mailbox_id)
        if not mailbox:
            return None

        update_data = mailbox_data.model_dump(exclude_unset=True)

        # Convert enum values
        if "greeting_type" in update_data and update_data["greeting_type"]:
            update_data["greeting_type"] = update_data["greeting_type"].value
        if "notification_channels" in update_data and update_data["notification_channels"]:
            update_data["notification_channels"] = [ch.value for ch in update_data["notification_channels"]]

        for field, value in update_data.items():
            setattr(mailbox, field, value)

        mailbox.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(mailbox)

        logger.info(f"Updated mailbox {mailbox_id}")
        return mailbox

    # ===== Greeting Management =====

    def create_greeting(self, greeting_data: GreetingCreate) -> VoicemailGreeting:
        """Create a voicemail greeting."""
        greeting = VoicemailGreeting(
            mailbox_id=greeting_data.mailbox_id,
            name=greeting_data.name,
            greeting_type=greeting_data.greeting_type.value,
            audio_url=greeting_data.audio_url,
            audio_duration_seconds=greeting_data.audio_duration_seconds,
            audio_format=greeting_data.audio_format,
            is_tts=greeting_data.is_tts,
            tts_text=greeting_data.tts_text,
            tts_voice=greeting_data.tts_voice,
            active_from=greeting_data.active_from,
            active_until=greeting_data.active_until
        )

        self.db.add(greeting)
        self.db.commit()
        self.db.refresh(greeting)

        logger.info(f"Created greeting for mailbox {greeting_data.mailbox_id}")
        return greeting

    def get_greeting(self, greeting_id: int) -> VoicemailGreeting | None:
        """Get a greeting by ID."""
        return self.db.query(VoicemailGreeting).filter(VoicemailGreeting.id == greeting_id).first()

    def list_greetings(self, mailbox_id: int) -> list[VoicemailGreeting]:
        """List all greetings for a mailbox."""
        return self.db.query(VoicemailGreeting).filter(
            VoicemailGreeting.mailbox_id == mailbox_id
        ).order_by(VoicemailGreeting.created_at.desc()).all()

    def set_active_greeting(self, mailbox_id: int, greeting_id: int) -> VoicemailBox | None:
        """Set the active greeting for a mailbox."""
        mailbox = self.get_mailbox(mailbox_id)
        greeting = self.get_greeting(greeting_id)

        if not mailbox or not greeting or greeting.mailbox_id != mailbox_id:
            return None

        # Deactivate all greetings
        self.db.query(VoicemailGreeting).filter(
            VoicemailGreeting.mailbox_id == mailbox_id
        ).update({"is_active": False})

        # Activate selected greeting
        greeting.is_active = True
        mailbox.current_greeting_id = greeting_id
        mailbox.greeting_type = greeting.greeting_type

        self.db.commit()
        self.db.refresh(mailbox)

        logger.info(f"Set active greeting {greeting_id} for mailbox {mailbox_id}")
        return mailbox

    # ===== Statistics & Analytics =====

    def get_voicemail_stats(self, agent_id: int) -> dict[str, Any]:
        """Get voicemail statistics for an agent."""
        voicemails = self.db.query(Voicemail).filter(
            Voicemail.agent_id == agent_id,
            Voicemail.deleted_at == None
        ).all()

        total = len(voicemails)
        new = sum(1 for v in voicemails if v.status == VoicemailStatus.NEW.value)
        heard = sum(1 for v in voicemails if v.status == VoicemailStatus.HEARD.value)
        saved = sum(1 for v in voicemails if v.status == VoicemailStatus.SAVED.value)
        archived = sum(1 for v in voicemails if v.status == VoicemailStatus.ARCHIVED.value)

        total_duration = sum(v.recording_duration_seconds for v in voicemails)
        avg_duration = total_duration / total if total > 0 else 0

        oldest = min(v.created_at for v in voicemails) if voicemails else None
        newest = max(v.created_at for v in voicemails) if voicemails else None

        return {
            "agent_id": agent_id,
            "total_messages": total,
            "new_messages": new,
            "heard_messages": heard,
            "saved_messages": saved,
            "archived_messages": archived,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": avg_duration,
            "oldest_message_date": oldest,
            "newest_message_date": newest
        }

    # ===== Retention & Cleanup =====

    def apply_retention_policy(self) -> int:
        """Apply retention policy and clean up expired voicemails."""
        now = datetime.now(UTC)

        # Find expired voicemails
        expired_voicemails = self.db.query(Voicemail).filter(
            Voicemail.expires_at <= now,
            Voicemail.auto_delete == True,
            Voicemail.status != VoicemailStatus.SAVED.value,  # Don't delete saved messages
            Voicemail.deleted_at == None
        ).all()

        count = 0
        for voicemail in expired_voicemails:
            voicemail.status = VoicemailStatus.DELETED.value
            voicemail.deleted_at = now

            # Update mailbox stats
            mailbox = self.get_mailbox_by_agent(voicemail.agent_id)
            if mailbox:
                mailbox.total_messages = max(0, mailbox.total_messages - 1)
                if voicemail.status == VoicemailStatus.NEW.value:
                    mailbox.unheard_messages = max(0, mailbox.unheard_messages - 1)

            count += 1

        self.db.commit()

        if count > 0:
            logger.info(f"Applied retention policy: deleted {count} expired voicemails")

        return count

    # ===== Notifications =====

    def _send_notifications(self, voicemail: Voicemail, mailbox: VoicemailBox):
        """Send notifications for new voicemail (placeholder)."""
        # In production, integrate with email/SMS/push notification services
        for channel in mailbox.notification_channels:
            notification = VoicemailNotification(
                voicemail_id=voicemail.id,
                agent_id=voicemail.agent_id,
                channel=channel,
                recipient=mailbox.notification_email if channel == NotificationChannel.EMAIL.value else mailbox.notification_phone,
                status="pending"
            )
            self.db.add(notification)

        self.db.commit()
        logger.info(f"Queued {len(mailbox.notification_channels)} notifications for voicemail {voicemail.id}")
