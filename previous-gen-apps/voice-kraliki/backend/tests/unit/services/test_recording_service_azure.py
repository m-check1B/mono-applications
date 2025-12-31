"""Tests for Recording Service with Azure Storage SDK integration."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.models.recording import (
    Recording,
    RecordingStatus,
    StorageProvider,
)
from app.services.recording import RecordingService, RecordingError


class TestRecordingServiceAzurePresignedURL:
    """Test Azure presigned URL generation in RecordingService."""

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
    def azure_recording(self):
        """Create sample Azure recording object as mock."""
        recording = Mock(spec=Recording)
        recording.id = 1
        recording.call_sid = "CA987654321"
        recording.status = RecordingStatus.COMPLETED.value
        recording.storage_provider = StorageProvider.AZURE.value
        recording.storage_bucket = "testcontainer"
        recording.storage_key = "recordings/test.wav"
        recording.download_url = None
        recording.download_url_expires_at = None
        return recording

    def test_generate_azure_presigned_url_with_connection_string(
        self, recording_service, azure_recording, mock_db
    ):
        """Test successful Azure presigned URL generation using connection string."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        expected_sas_token = "sv=2023-01-03&ss=b&srt=sco&sp=r&se=2025-12-25T16:00:00Z&st=2025-12-24T15:00:00Z&spr=https&sig=xxx"
        expected_url = f"https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav?{expected_sas_token}"

        with (
            patch("app.services.recording.BlobServiceClient") as mock_blob_service_client,
            patch("app.services.recording.generate_blob_sas") as mock_generate_blob_sas,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.azure_storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
            mock_settings.azure_storage_account_name = "testaccount"
            mock_settings.azure_storage_account_key = "testkey"

            mock_blob_client = MagicMock()
            mock_blob_client.url = (
                "https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav"
            )
            mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client
            mock_generate_blob_sas.return_value = expected_sas_token

            url, expires_at = recording_service.generate_download_url(1, expires_in_seconds=3600)

            assert url == expected_url
            assert isinstance(expires_at, datetime)
            assert (expires_at - datetime.now(timezone.utc)).total_seconds() > 3500

            mock_blob_service_client.from_connection_string.assert_called_once_with(
                "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
            )

            mock_generate_blob_sas.assert_called_once()
            call_kwargs = mock_generate_blob_sas.call_args[1]
            assert call_kwargs["account_name"] == "testaccount"
            assert call_kwargs["container_name"] == "testcontainer"
            assert call_kwargs["blob_name"] == "recordings/test.wav"
            assert call_kwargs["account_key"] == "testkey"

    def test_generate_azure_presigned_url_with_account_key(
        self, recording_service, azure_recording, mock_db
    ):
        """Test Azure presigned URL generation using account name and key."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        expected_sas_token = "sv=2023-01-03&ss=b&srt=sco&sp=r&se=2025-12-25T16:00:00Z&st=2025-12-24T15:00:00Z&spr=https&sig=yyy"
        expected_url = f"https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav?{expected_sas_token}"

        with (
            patch("app.services.recording.BlobServiceClient") as mock_blob_service_client,
            patch("app.services.recording.generate_blob_sas") as mock_generate_blob_sas,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.azure_storage_connection_string = None
            mock_settings.azure_storage_account_name = "testaccount"
            mock_settings.azure_storage_account_key = "testkey"

            mock_blob_client = MagicMock()
            mock_blob_client.url = (
                "https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav"
            )
            mock_blob_service_client.return_value.get_blob_client.return_value = mock_blob_client
            mock_generate_blob_sas.return_value = expected_sas_token

            url, expires_at = recording_service.generate_download_url(1)

            assert url == expected_url

            mock_blob_service_client.assert_called_once_with(
                account_url="https://testaccount.blob.core.windows.net",
                credential="testkey",
            )

    def test_generate_azure_presigned_url_no_credentials_fallback(
        self, recording_service, azure_recording, mock_db
    ):
        """Test fallback to public URL when Azure credentials are not configured."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        with patch("app.services.recording.settings") as mock_settings:
            mock_settings.azure_storage_connection_string = None
            mock_settings.azure_storage_account_name = None
            mock_settings.azure_storage_account_key = None

            url, expires_at = recording_service.generate_download_url(1)

            expected_url = f"https://testcontainer.blob.core.windows.net/recordings/test.wav"
            assert url == expected_url
            assert isinstance(expires_at, datetime)

    def test_generate_azure_presigned_url_azure_error_fallback(
        self, recording_service, azure_recording, mock_db
    ):
        """Test fallback to public URL when Azure client error occurs."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        from azure.core.exceptions import AzureError

        with (
            patch("app.services.recording.BlobServiceClient") as mock_blob_service_client,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.azure_storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
            mock_settings.azure_storage_account_name = "testaccount"
            mock_settings.azure_storage_account_key = "testkey"

            mock_blob_service_client.from_connection_string.side_effect = AzureError(
                "Invalid credentials"
            )

            url, expires_at = recording_service.generate_download_url(1)

            expected_url = f"https://testcontainer.blob.core.windows.net/recordings/test.wav"
            assert url == expected_url

    def test_generate_azure_presigned_url_custom_expiration(
        self, recording_service, azure_recording, mock_db
    ):
        """Test Azure presigned URL generation with custom expiration time."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        custom_expiration_seconds = 7200
        custom_expiry = datetime.now(timezone.utc) + timedelta(seconds=custom_expiration_seconds)

        with (
            patch("app.services.recording.BlobServiceClient") as mock_blob_service_client,
            patch("app.services.recording.generate_blob_sas") as mock_generate_blob_sas,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.azure_storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
            mock_settings.azure_storage_account_name = "testaccount"
            mock_settings.azure_storage_account_key = "testkey"

            mock_blob_client = MagicMock()
            mock_blob_client.url = (
                "https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav"
            )
            mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client
            mock_generate_blob_sas.return_value = "sv=test"

            _, expires_at = recording_service.generate_download_url(
                1, expires_in_seconds=custom_expiration_seconds
            )

            call_kwargs = mock_generate_blob_sas.call_args[1]
            assert call_kwargs["expiry"] == expires_at
            assert (expires_at - datetime.now(timezone.utc)).total_seconds() > 7000

    def test_generate_azure_presigned_url_caches_in_recording(
        self, recording_service, azure_recording, mock_db
    ):
        """Test that generated Azure URL is cached in the recording object."""
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording
        mock_db.commit = Mock()

        expected_sas_token = "sv=2023-01-03&ss=b&srt=sco&sp=r&se=2025-12-25T16:00:00Z&st=2025-12-24T15:00:00Z&spr=https&sig=zzz"

        with (
            patch("app.services.recording.BlobServiceClient") as mock_blob_service_client,
            patch("app.services.recording.generate_blob_sas") as mock_generate_blob_sas,
            patch("app.services.recording.settings") as mock_settings,
        ):
            mock_settings.azure_storage_connection_string = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=testkey;EndpointSuffix=core.windows.net"
            mock_settings.azure_storage_account_name = "testaccount"
            mock_settings.azure_storage_account_key = "testkey"

            mock_blob_client = MagicMock()
            mock_blob_client.url = (
                "https://testaccount.blob.core.windows.net/testcontainer/recordings/test.wav"
            )
            mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client
            mock_generate_blob_sas.return_value = expected_sas_token

            url, expires_at = recording_service.generate_download_url(1)

            assert azure_recording.download_url == url
            assert azure_recording.download_url_expires_at == expires_at
            mock_db.commit.assert_called_once()

    def test_generate_azure_url_recording_not_found(self, recording_service, mock_db):
        """Test Azure URL generation when recording does not exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = recording_service.generate_download_url(999)
        assert result is None

    def test_generate_azure_url_recording_not_completed(
        self, recording_service, azure_recording, mock_db
    ):
        """Test Azure URL generation when recording is not completed."""
        azure_recording.status = RecordingStatus.RECORDING.value
        mock_db.query.return_value.filter.return_value.first.return_value = azure_recording

        with pytest.raises(RecordingError, match="Recording is not ready for download"):
            recording_service.generate_download_url(1)
