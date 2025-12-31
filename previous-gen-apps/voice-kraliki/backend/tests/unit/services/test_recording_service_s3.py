"""Tests for Recording Service with boto3 S3 presigned URL integration."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.models.recording import (
    Recording,
    RecordingStatus,
    StorageProvider,
    RecordingCreate,
    RecordingUpdate,
)
from app.services.recording import RecordingService, RecordingError


class TestRecordingServiceS3PresignedURL:
    """Test S3 presigned URL generation in RecordingService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def recording_service(self, mock_db):
        """Create RecordingService instance with mock DB."""
        return RecordingService(mock_db)

    @pytest.fixture
    def sample_recording(self):
        """Create sample recording object as mock."""
        recording = Mock(spec=Recording)
        recording.id = 1
        recording.call_sid = "CA123456789"
        recording.status = RecordingStatus.COMPLETED.value
        recording.storage_provider = StorageProvider.S3.value
        recording.storage_bucket = "test-bucket"
        recording.storage_key = "recordings/test.wav"
        recording.download_url = None
        recording.download_url_expires_at = None
        return recording

    def test_generate_s3_presigned_url_success(self, recording_service, sample_recording, mock_db):
        """Test successful S3 presigned URL generation."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        expected_url = "https://test-bucket.s3.amazonaws.com/recordings/test.wav?AWSAccessKeyId=xxx&Expires=yyy&Signature=zzz"

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = expected_url
            mock_boto3_client.return_value = mock_s3

            url, expires_at = recording_service.generate_download_url(1, expires_in_seconds=3600)

            assert url == expected_url
            assert isinstance(expires_at, datetime)
            assert (expires_at - datetime.now(timezone.utc)).total_seconds() > 3500

            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={
                    "Bucket": sample_recording.storage_bucket,
                    "Key": sample_recording.storage_key,
                },
                ExpiresIn=3600,
            )

            mock_boto3_client.assert_called_once_with(
                "s3", aws_access_key_id=None, aws_secret_access_key=None, region_name="us-east-1"
            )

    def test_generate_s3_presigned_url_with_credentials(
        self, recording_service, sample_recording, mock_db
    ):
        """Test S3 presigned URL generation with explicit credentials."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        expected_url = "https://test-bucket.s3.amazonaws.com/recordings/test.wav?AWSAccessKeyId=xxx&Expires=yyy&Signature=zzz"

        with (
            patch("app.services.recording.boto3.client") as mock_boto3_client,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.aws_access_key_id = "test_access_key"
            mock_settings.aws_secret_access_key = "test_secret_key"
            mock_settings.aws_region = "us-west-2"

            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = expected_url
            mock_boto3_client.return_value = mock_s3

            url, _ = recording_service.generate_download_url(1)

            mock_boto3_client.assert_called_once_with(
                "s3",
                aws_access_key_id="test_access_key",
                aws_secret_access_key="test_secret_key",
                region_name="us-west-2",
            )

    def test_generate_s3_presigned_url_aws_error_fallback(
        self, recording_service, sample_recording, mock_db
    ):
        """Test fallback to public URL when AWS credentials are invalid."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        from botocore.exceptions import NoCredentialsError

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.side_effect = NoCredentialsError()
            mock_boto3_client.return_value = mock_s3

            url, expires_at = recording_service.generate_download_url(1)

            expected_url = f"https://s3.amazonaws.com/{sample_recording.storage_bucket}/{sample_recording.storage_key}"
            assert url == expected_url
            assert isinstance(expires_at, datetime)

    def test_generate_s3_presigned_url_client_error_fallback(
        self, recording_service, sample_recording, mock_db
    ):
        """Test fallback to public URL when AWS client error occurs."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        from botocore.exceptions import ClientError

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.side_effect = ClientError(
                {"Error": {"Code": "AccessDenied"}}, "GeneratePresignedUrl"
            )
            mock_boto3_client.return_value = mock_s3

            url, expires_at = recording_service.generate_download_url(1)

            expected_url = f"https://s3.amazonaws.com/{sample_recording.storage_bucket}/{sample_recording.storage_key}"
            assert url == expected_url

    def test_generate_url_azure_storage_fallback(
        self, recording_service, sample_recording, mock_db
    ):
        """Test Azure storage fallback to public URL when credentials not configured."""
        sample_recording.storage_provider = StorageProvider.AZURE.value
        sample_recording.storage_bucket = "testaccount"
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        with patch("app.services.recording.settings") as mock_settings:
            mock_settings.azure_storage_connection_string = None
            mock_settings.azure_storage_account_name = None
            mock_settings.azure_storage_account_key = None

            url, expires_at = recording_service.generate_download_url(1)

            expected_url = f"https://{sample_recording.storage_bucket}.blob.core.windows.net/{sample_recording.storage_key}"
            assert url == expected_url
            assert isinstance(expires_at, datetime)

    def test_generate_url_local_storage(self, recording_service, sample_recording, mock_db):
        """Test URL generation for local storage."""
        sample_recording.storage_provider = "local"
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        url, expires_at = recording_service.generate_download_url(1)

        expected_url = f"/api/recordings/{sample_recording.id}/download"
        assert url == expected_url
        assert isinstance(expires_at, datetime)

    def test_generate_url_recording_not_found(self, recording_service, mock_db):
        """Test URL generation when recording does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = recording_service.generate_download_url(999)
        assert result is None

    def test_generate_url_recording_not_completed(
        self, recording_service, sample_recording, mock_db
    ):
        """Test URL generation when recording is not completed."""
        sample_recording.status = RecordingStatus.RECORDING.value
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording

        with pytest.raises(RecordingError, match="Recording is not ready for download"):
            recording_service.generate_download_url(1)

    def test_generate_url_caches_in_recording(self, recording_service, sample_recording, mock_db):
        """Test that generated URL is cached in the recording object."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        expected_url = "https://test-bucket.s3.amazonaws.com/recordings/test.wav?AWSAccessKeyId=xxx&Expires=yyy&Signature=zzz"

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = expected_url
            mock_boto3_client.return_value = mock_s3

            url, expires_at = recording_service.generate_download_url(1)

            assert sample_recording.download_url == url
            assert sample_recording.download_url_expires_at == expires_at
            mock_db.commit.assert_called_once()

    def test_generate_url_custom_expiration(self, recording_service, sample_recording, mock_db):
        """Test URL generation with custom expiration time."""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        custom_expiration_seconds = 7200

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = "https://example.com/presigned"
            mock_boto3_client.return_value = mock_s3

            _, expires_at = recording_service.generate_download_url(
                1, expires_in_seconds=custom_expiration_seconds
            )

            mock_s3.generate_presigned_url.assert_called_once_with(
                "get_object",
                Params={
                    "Bucket": sample_recording.storage_bucket,
                    "Key": sample_recording.storage_key,
                },
                ExpiresIn=custom_expiration_seconds,
            )

    def test_generate_url_minio_storage(self, recording_service, sample_recording, mock_db):
        """Test URL generation for MinIO storage."""
        sample_recording.storage_provider = StorageProvider.MINIO.value
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        expected_url = "http://localhost:9000/test-bucket/recordings/test.wav?signature=xxx"

        with (
            patch("app.services.recording.boto3.client") as mock_boto3_client,
            patch("app.services.recording.os.getenv") as mock_getenv,
        ):
            mock_getenv.return_value = "http://localhost:9000"
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = expected_url
            mock_boto3_client.return_value = mock_s3

            url, _ = recording_service.generate_download_url(1)

            assert url == expected_url
            mock_boto3_client.assert_called_once_with(
                "s3",
                aws_access_key_id=None,
                aws_secret_access_key=None,
                region_name="us-east-1",
                endpoint_url="http://localhost:9000",
            )

    def test_generate_url_gcs_storage(self, recording_service, sample_recording, mock_db):
        """Test URL generation for GCS storage via boto3."""
        sample_recording.storage_provider = StorageProvider.GCS.value
        mock_db.query.return_value.filter.return_value.first.return_value = sample_recording
        mock_db.commit = Mock()

        expected_url = "https://storage.googleapis.com/test-bucket/recordings/test.wav?signature=xxx"

        with patch("app.services.recording.boto3.client") as mock_boto3_client:
            mock_s3 = MagicMock()
            mock_s3.generate_presigned_url.return_value = expected_url
            mock_boto3_client.return_value = mock_s3

            url, _ = recording_service.generate_download_url(1)

            assert url == expected_url
            mock_boto3_client.assert_called_once_with(
                "s3",
                aws_access_key_id=None,
                aws_secret_access_key=None,
                region_name="us-east-1",
                endpoint_url="https://storage.googleapis.com",
            )
