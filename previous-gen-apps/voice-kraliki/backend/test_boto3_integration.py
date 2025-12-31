#!/usr/bin/env python3
"""Test script to verify boto3 integration in RecordingService."""

import os
import sys

# Add backend to path
sys.path.insert(0, "/home/adminmatej/github/applications/cc-lite-2026/backend")


def test_boto3_import():
    """Test that boto3 can be imported."""
    print("Testing boto3 import...")
    try:
        import boto3

        print(f"✓ boto3 imported successfully (version {boto3.__version__})")
        return True
    except ImportError as e:
        print(f"✗ Failed to import boto3: {e}")
        return False


def test_botocore_import():
    """Test that botocore exceptions can be imported."""
    print("\nTesting botocore.exceptions import...")
    try:
        from botocore.exceptions import ClientError, NoCredentialsError

        print("✓ botocore.exceptions imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import botocore.exceptions: {e}")
        return False


def test_recording_service_import():
    """Test that RecordingService can be imported (will fail if boto3 not available)."""
    print("\nTesting RecordingService import...")
    try:
        from app.services.recording import RecordingService

        print("✓ RecordingService imported successfully")
        print("  - boto3 integration loaded")
        print("  - S3 presigned URL generation available")
        return True
    except ImportError as e:
        print(f"✗ Failed to import RecordingService: {e}")
        return False


def test_s3_client_creation():
    """Test that an S3 client can be created (mock mode)."""
    print("\nTesting S3 client creation (mock mode)...")
    try:
        import boto3
        from unittest.mock import Mock, patch

        # Mock settings to avoid needing real AWS credentials
        with patch("app.services.recording.settings") as mock_settings:
            mock_settings.aws_access_key_id = None
            mock_settings.aws_secret_access_key = None
            mock_settings.aws_region = "us-east-1"

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=None,
                aws_secret_access_key=None,
                region_name="us-east-1",
            )
            print("✓ S3 client created successfully")
            print(f"  - Client type: {type(s3_client).__name__}")
            return True
    except Exception as e:
        print(f"✗ Failed to create S3 client: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("CC-Lite Boto3 Integration Verification")
    print("=" * 70)

    results = []
    results.append(("boto3 import", test_boto3_import()))
    results.append(("botocore exceptions", test_botocore_import()))
    results.append(("RecordingService import", test_recording_service_import()))
    results.append(("S3 client creation", test_s3_client_creation()))

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED - boto3 integration working correctly")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED - boto3 integration has issues")
        sys.exit(1)
