"""Recording Management Service.

Handles call recording operations, storage, transcription, and retention.
"""

import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from botocore.exceptions import ClientError, NoCredentialsError
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.models.recording import (
    Recording,
    RecordingCreate,
    RecordingStatus,
    RecordingStorage,
    RecordingTranscript,
    RecordingUpdate,
    StorageProvider,
    TranscriptCreate,
    TranscriptionStatus,
    TranscriptUpdate,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class RecordingError(Exception):
    """Base exception for recording errors."""

    pass


class RecordingService:
    """Service for managing call recordings."""

    def __init__(self, db: Session):
        self.db = db

    # ===== Recording Management =====

    def create_recording(self, recording_data: RecordingCreate) -> Recording:
        """Create a new recording entry."""
        # Calculate expiration date
        expires_at = datetime.now(UTC) + timedelta(days=recording_data.retention_days)

        recording = Recording(
            call_sid=recording_data.call_sid,
            agent_id=recording_data.agent_id,
            team_id=recording_data.team_id,
            campaign_id=recording_data.campaign_id,
            caller_phone=recording_data.caller_phone,
            direction=recording_data.direction,
            started_at=recording_data.started_at or datetime.now(UTC),
            storage_provider=recording_data.storage_provider.value,
            storage_bucket=recording_data.storage_bucket,
            storage_key=recording_data.storage_key,
            file_format=recording_data.file_format,
            is_encrypted=recording_data.is_encrypted,
            retention_days=recording_data.retention_days,
            expires_at=expires_at,
            auto_delete=recording_data.auto_delete,
            status=RecordingStatus.RECORDING.value,
        )

        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)

        logger.info(f"Created recording: {recording.call_sid} (ID: {recording.id})")
        return recording

    def get_recording(self, recording_id: int) -> Recording | None:
        """Get a recording by ID."""
        return (
            self.db.query(Recording)
            .filter(Recording.id == recording_id, Recording.deleted_at is None)
            .first()
        )

    def get_recording_by_call_sid(self, call_sid: str) -> Recording | None:
        """Get a recording by call SID."""
        return (
            self.db.query(Recording)
            .filter(Recording.call_sid == call_sid, Recording.deleted_at is None)
            .first()
        )

    def list_recordings(
        self,
        agent_id: int | None = None,
        team_id: int | None = None,
        campaign_id: int | None = None,
        status: RecordingStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Recording]:
        """List recordings with optional filters."""
        query = self.db.query(Recording).filter(Recording.deleted_at is None)

        if agent_id:
            query = query.filter(Recording.agent_id == agent_id)
        if team_id:
            query = query.filter(Recording.team_id == team_id)
        if campaign_id:
            query = query.filter(Recording.campaign_id == campaign_id)
        if status:
            query = query.filter(Recording.status == status.value)
        if start_date:
            query = query.filter(Recording.started_at >= start_date)
        if end_date:
            query = query.filter(Recording.started_at <= end_date)

        return query.order_by(Recording.started_at.desc()).offset(skip).limit(limit).all()

    def update_recording(
        self, recording_id: int, recording_data: RecordingUpdate
    ) -> Recording | None:
        """Update a recording."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        update_data = recording_data.model_dump(exclude_unset=True)

        # Convert status enum if provided
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            setattr(recording, field, value)

        # Auto-complete if ended
        if recording_data.ended_at and recording.status == RecordingStatus.RECORDING.value:
            recording.status = RecordingStatus.COMPLETED.value

        recording.updated_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(recording)

        logger.info(f"Updated recording: {recording.call_sid} (ID: {recording.id})")
        return recording

    def complete_recording(
        self,
        recording_id: int,
        duration_seconds: int,
        file_size_bytes: int,
        checksum_md5: str | None = None,
    ) -> Recording | None:
        """Mark a recording as completed."""
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        recording.status = RecordingStatus.COMPLETED.value
        recording.ended_at = datetime.now(UTC)
        recording.duration_seconds = duration_seconds
        recording.file_size_bytes = file_size_bytes
        recording.checksum_md5 = checksum_md5

        self.db.commit()
        self.db.refresh(recording)

        logger.info(
            f"Completed recording: {recording.call_sid} (ID: {recording.id}, duration: {duration_seconds}s)"
        )
        return recording

    def delete_recording(self, recording_id: int, hard_delete: bool = False) -> bool:
        """Delete a recording (soft delete by default)."""
        recording = self.get_recording(recording_id)
        if not recording:
            return False

        if hard_delete:
            # Hard delete - remove from database
            self.db.delete(recording)
            logger.info(f"Hard deleted recording: {recording.call_sid} (ID: {recording.id})")
        else:
            # Soft delete - mark as deleted
            recording.status = RecordingStatus.DELETED.value
            recording.deleted_at = datetime.now(UTC)
            logger.info(f"Soft deleted recording: {recording.call_sid} (ID: {recording.id})")

        self.db.commit()
        return True

    def generate_download_url(
        self, recording_id: int, expires_in_seconds: int = 3600
    ) -> tuple[str, datetime] | None:
        """
        Generate a signed download URL for a recording.

        Integrates with cloud storage providers (S3, Azure, GCS) to generate
        presigned URLs with expiration.
        """
        recording = self.get_recording(recording_id)
        if not recording:
            return None

        if recording.status != RecordingStatus.COMPLETED.value:
            raise RecordingError("Recording is not ready for download")

        # Generate expiration time
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)

        # Generate signed URL based on storage provider
        if recording.storage_provider == StorageProvider.S3.value:
            try:
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region,
                )
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": recording.storage_bucket, "Key": recording.storage_key},
                    ExpiresIn=expires_in_seconds,
                )
                logger.info(f"Generated S3 presigned URL for recording {recording.id}")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to generate S3 presigned URL: {e}")
                # Fallback to public URL if presigned URL generation fails
                url = f"https://s3.amazonaws.com/{recording.storage_bucket}/{recording.storage_key}"
        elif recording.storage_provider == StorageProvider.MINIO.value:
            try:
                # MinIO uses boto3 with endpoint_url
                endpoint_url = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")

                # Check for per-team config
                storage_config = self.get_default_storage(recording.team_id)
                aws_access_key_id = settings.aws_access_key_id
                aws_secret_access_key = settings.aws_secret_access_key

                if storage_config and storage_config.provider == StorageProvider.MINIO.value:
                    endpoint_url = storage_config.config.get("endpoint_url", endpoint_url)
                    aws_access_key_id = storage_config.config.get("access_key_id", aws_access_key_id)
                    aws_secret_access_key = storage_config.config.get("secret_key", aws_secret_access_key)

                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=settings.aws_region,
                    endpoint_url=endpoint_url,
                )
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": recording.storage_bucket, "Key": recording.storage_key},
                    ExpiresIn=expires_in_seconds,
                )
                logger.info(f"Generated MinIO presigned URL for recording {recording.id}")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to generate MinIO presigned URL: {e}")
                url = f"{endpoint_url}/{recording.storage_bucket}/{recording.storage_key}"
        elif recording.storage_provider == StorageProvider.GCS.value:
            try:
                # GCS can use boto3 with its S3-compatible API
                endpoint_url = "https://storage.googleapis.com"
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region,
                    endpoint_url=endpoint_url,
                )
                url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": recording.storage_bucket, "Key": recording.storage_key},
                    ExpiresIn=expires_in_seconds,
                )
                logger.info(f"Generated GCS presigned URL for recording {recording.id}")
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to generate GCS presigned URL: {e}")
                url = f"https://storage.googleapis.com/{recording.storage_bucket}/{recording.storage_key}"
        elif recording.storage_provider == StorageProvider.AZURE.value:
            try:
                if settings.azure_storage_connection_string:
                    blob_service_client = BlobServiceClient.from_connection_string(
                        settings.azure_storage_connection_string
                    )
                elif settings.azure_storage_account_name and settings.azure_storage_account_key:
                    blob_service_client = BlobServiceClient(
                        account_url=f"https://{settings.azure_storage_account_name}.blob.core.windows.net",
                        credential=settings.azure_storage_account_key,
                    )
                else:
                    logger.warning("Azure credentials not configured, using public URL")
                    raise ValueError("Azure credentials not configured")

                blob_client = blob_service_client.get_blob_client(
                    container=recording.storage_bucket,
                    blob=recording.storage_key,
                )

                sas_token = generate_blob_sas(
                    account_name=settings.azure_storage_account_name,
                    container_name=recording.storage_bucket,
                    blob_name=recording.storage_key,
                    account_key=settings.azure_storage_account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=expires_at,
                )

                url = f"{blob_client.url}?{sas_token}"
                logger.info(f"Generated Azure presigned URL for recording {recording.id}")
            except (AzureError, ValueError) as e:
                logger.error(f"Failed to generate Azure presigned URL: {e}")
                url = f"https://{recording.storage_bucket}.blob.core.windows.net/{recording.storage_key}"
        else:
            # Local storage - direct path
            url = f"/api/recordings/{recording.id}/download"
            logger.info(f"Generated local download URL for recording {recording.id}")

        # Cache the URL
        recording.download_url = url
        recording.download_url_expires_at = expires_at
        self.db.commit()

        logger.info(f"Generated download URL for recording {recording.id} (expires: {expires_at})")
        return url, expires_at

    # ===== Transcription Management =====

    def create_transcript(self, transcript_data: TranscriptCreate) -> RecordingTranscript:
        """Create a transcription request."""
        # Verify recording exists
        recording = self.get_recording(transcript_data.recording_id)
        if not recording:
            raise RecordingError(f"Recording {transcript_data.recording_id} not found")

        transcript = RecordingTranscript(
            recording_id=transcript_data.recording_id,
            provider=transcript_data.provider,
            language=transcript_data.language,
            status=TranscriptionStatus.PENDING.value,
        )

        self.db.add(transcript)
        self.db.commit()
        self.db.refresh(transcript)

        logger.info(f"Created transcript request for recording {transcript_data.recording_id}")
        return transcript

    def get_transcript(self, transcript_id: int) -> RecordingTranscript | None:
        """Get a transcript by ID."""
        return (
            self.db.query(RecordingTranscript)
            .filter(RecordingTranscript.id == transcript_id)
            .first()
        )

    def get_recording_transcript(self, recording_id: int) -> RecordingTranscript | None:
        """Get the transcript for a recording."""
        return (
            self.db.query(RecordingTranscript)
            .filter(
                RecordingTranscript.recording_id == recording_id,
                RecordingTranscript.status == TranscriptionStatus.COMPLETED.value,
            )
            .first()
        )

    def update_transcript(
        self, transcript_id: int, transcript_data: TranscriptUpdate
    ) -> RecordingTranscript | None:
        """Update a transcript."""
        transcript = self.get_transcript(transcript_id)
        if not transcript:
            return None

        update_data = transcript_data.model_dump(exclude_unset=True)

        # Convert status enum if provided
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            setattr(transcript, field, value)

        # Auto-complete if text provided
        if transcript_data.text and transcript.status == TranscriptionStatus.PENDING.value:
            transcript.status = TranscriptionStatus.COMPLETED.value
            transcript.completed_at = datetime.now(UTC)

        # Update searchable text
        if transcript_data.text:
            transcript.searchable_text = transcript_data.text.lower()

        self.db.commit()
        self.db.refresh(transcript)

        logger.info(f"Updated transcript {transcript.id} for recording {transcript.recording_id}")
        return transcript

    def search_transcripts(
        self, search_query: str, agent_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[RecordingTranscript]:
        """Search transcripts by text content."""
        query = (
            self.db.query(RecordingTranscript)
            .join(Recording)
            .filter(
                RecordingTranscript.searchable_text.contains(search_query.lower()),
                RecordingTranscript.status == TranscriptionStatus.COMPLETED.value,
                Recording.deleted_at is None,
            )
        )

        if agent_id:
            query = query.filter(Recording.agent_id == agent_id)

        return query.order_by(Recording.started_at.desc()).offset(skip).limit(limit).all()

    # ===== Storage Management =====

    def create_storage_config(self, config_data) -> RecordingStorage:
        """Create storage provider configuration."""
        storage = RecordingStorage(
            team_id=config_data.team_id,
            provider=config_data.provider.value,
            name=config_data.name,
            description=config_data.description,
            is_active=config_data.is_active,
            is_default=config_data.is_default,
            config=config_data.config,
            encryption_enabled=config_data.encryption_enabled,
            default_retention_days=config_data.default_retention_days,
        )

        self.db.add(storage)
        self.db.commit()
        self.db.refresh(storage)

        logger.info(f"Created storage config: {storage.name} (provider: {storage.provider})")
        return storage

    def get_storage_config(self, storage_id: int) -> RecordingStorage | None:
        """Get storage configuration by ID."""
        return self.db.query(RecordingStorage).filter(RecordingStorage.id == storage_id).first()

    def get_default_storage(self, team_id: int | None = None) -> RecordingStorage | None:
        """Get default storage configuration."""
        query = self.db.query(RecordingStorage).filter(
            RecordingStorage.is_default, RecordingStorage.is_active
        )

        if team_id:
            query = query.filter(
                or_(RecordingStorage.team_id == team_id, RecordingStorage.team_id is None)
            )

        return query.first()

    # ===== Retention & Cleanup =====

    def apply_retention_policy(self) -> int:
        """Apply retention policy and clean up expired recordings."""
        now = datetime.now(UTC)

        # Find expired recordings with auto-delete enabled
        expired_recordings = (
            self.db.query(Recording)
            .filter(
                Recording.expires_at <= now,
                Recording.auto_delete,
                Recording.status != RecordingStatus.DELETED.value,
                Recording.deleted_at is None,
            )
            .all()
        )

        count = 0
        for recording in expired_recordings:
            recording.status = RecordingStatus.DELETED.value
            recording.deleted_at = now
            count += 1

        self.db.commit()

        if count > 0:
            logger.info(f"Applied retention policy: marked {count} recordings for deletion")

        return count

    # ===== Analytics =====

    def get_recording_stats(
        self,
        agent_id: int | None = None,
        team_id: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Get recording statistics."""
        query = self.db.query(Recording).filter(Recording.deleted_at is None)

        if agent_id:
            query = query.filter(Recording.agent_id == agent_id)
        if team_id:
            query = query.filter(Recording.team_id == team_id)
        if start_date:
            query = query.filter(Recording.started_at >= start_date)
        if end_date:
            query = query.filter(Recording.started_at <= end_date)

        recordings = query.all()

        total_recordings = len(recordings)
        total_duration = sum(r.duration_seconds for r in recordings if r.duration_seconds)
        total_size = sum(r.file_size_bytes for r in recordings if r.file_size_bytes)

        completed = sum(1 for r in recordings if r.status == RecordingStatus.COMPLETED.value)
        transcribed = sum(1 for r in recordings if r.has_transcription)

        return {
            "total_recordings": total_recordings,
            "completed_recordings": completed,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": total_duration / total_recordings
            if total_recordings > 0
            else 0,
            "total_storage_bytes": total_size,
            "transcribed_count": transcribed,
            "transcription_rate": (transcribed / total_recordings * 100)
            if total_recordings > 0
            else 0,
        }
