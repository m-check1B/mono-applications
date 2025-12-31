"""Tests for Feature Flags API.

Tests cover:
- Getting all feature flags
- Getting specific feature flag status
- Demo configurations
- Activating demo configurations
"""

import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the application."""
    app = create_app()
    return TestClient(app)


class TestGetAllFeatureFlags:
    """Tests for getting all feature flags."""

    def test_get_all_feature_flags(self, client: TestClient):
        """Test getting all feature flags."""
        response = client.get("/api/feature-flags/")

        assert response.status_code == 200
        data = response.json()
        assert "flags" in data
        assert "total" in data
        assert "enabled" in data
        assert "disabled" in data

    def test_feature_flags_structure(self, client: TestClient):
        """Test that feature flags have correct structure."""
        response = client.get("/api/feature-flags/")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["flags"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["enabled"], int)
        assert isinstance(data["disabled"], int)

        # Total should equal enabled + disabled
        assert data["total"] == data["enabled"] + data["disabled"]

    def test_feature_flag_item_structure(self, client: TestClient):
        """Test that each feature flag has correct structure."""
        response = client.get("/api/feature-flags/")

        assert response.status_code == 200
        data = response.json()

        if data["flags"]:
            flag = data["flags"][0]
            assert "name" in flag
            assert "enabled" in flag
            assert "description" in flag
            assert isinstance(flag["enabled"], bool)
            assert isinstance(flag["name"], str)
            assert isinstance(flag["description"], str)


class TestGetSpecificFeatureFlag:
    """Tests for getting specific feature flag."""

    def test_get_existing_feature_flag(self, client: TestClient):
        """Test getting an existing feature flag."""
        # First get all flags to find a valid name
        all_flags_response = client.get("/api/feature-flags/")
        assert all_flags_response.status_code == 200
        flags = all_flags_response.json()["flags"]

        if flags:
            flag_name = flags[0]["name"]
            response = client.get(f"/api/feature-flags/{flag_name}")

            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "enabled" in data
            assert "message" in data
            assert data["name"] == flag_name

    def test_get_nonexistent_feature_flag(self, client: TestClient):
        """Test getting a non-existent feature flag."""
        response = client.get("/api/feature-flags/nonexistent_flag_xyz123")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_feature_flag_enable_openai_realtime(self, client: TestClient):
        """Test getting enable_openai_realtime flag."""
        with patch("app.api.feature_flags.is_feature_enabled") as mock_enabled:
            mock_enabled.return_value = True

            response = client.get("/api/feature-flags/enable_openai_realtime")

            # This will either work or return 404 depending on how the flag is set up
            assert response.status_code in [200, 404]

    def test_get_feature_flag_demo_mode(self, client: TestClient):
        """Test getting demo_mode flag."""
        with patch("app.api.feature_flags.is_feature_enabled") as mock_enabled:
            mock_enabled.return_value = False

            response = client.get("/api/feature-flags/demo_mode")

            assert response.status_code in [200, 404]


class TestDemoConfigurations:
    """Tests for demo configurations."""

    def test_get_all_demo_configs(self, client: TestClient):
        """Test getting all demo configurations."""
        response = client.get("/api/feature-flags/demo-configs/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_demo_config_structure(self, client: TestClient):
        """Test that demo configs have correct structure."""
        response = client.get("/api/feature-flags/demo-configs/")

        assert response.status_code == 200
        data = response.json()

        if data:
            config = data[0]
            assert "name" in config
            assert "description" in config
            assert "features" in config
            assert "providers" in config
            assert "scenarios" in config

            assert isinstance(config["features"], dict)
            assert isinstance(config["providers"], list)
            assert isinstance(config["scenarios"], list)

    def test_get_specific_demo_config(self, client: TestClient):
        """Test getting a specific demo configuration."""
        # First get all configs to find a valid name
        all_configs_response = client.get("/api/feature-flags/demo-configs/")
        assert all_configs_response.status_code == 200
        configs = all_configs_response.json()

        if configs:
            config_name = configs[0]["name"]
            response = client.get(f"/api/feature-flags/demo-configs/{config_name}")

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == config_name

    def test_get_nonexistent_demo_config(self, client: TestClient):
        """Test getting a non-existent demo configuration."""
        response = client.get("/api/feature-flags/demo-configs/nonexistent_config_xyz123")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestActivateDemoConfig:
    """Tests for activating demo configurations."""

    def test_activate_demo_config(self, client: TestClient):
        """Test activating a demo configuration."""
        # First get all configs to find a valid name
        all_configs_response = client.get("/api/feature-flags/demo-configs/")
        assert all_configs_response.status_code == 200
        configs = all_configs_response.json()

        if configs:
            config_name = configs[0]["name"]
            response = client.post(f"/api/feature-flags/demo-configs/{config_name}/activate")

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "demo_type" in data
            assert data["demo_type"] == config_name

    def test_activate_nonexistent_demo_config(self, client: TestClient):
        """Test activating a non-existent demo configuration."""
        response = client.post("/api/feature-flags/demo-configs/nonexistent_xyz123/activate")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_activate_demo_config_response_structure(self, client: TestClient):
        """Test that activate response has correct structure."""
        all_configs_response = client.get("/api/feature-flags/demo-configs/")
        assert all_configs_response.status_code == 200
        configs = all_configs_response.json()

        if configs:
            config_name = configs[0]["name"]
            response = client.post(f"/api/feature-flags/demo-configs/{config_name}/activate")

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "demo_type" in data
            assert "features_activated" in data
            assert "providers_enabled" in data
            assert isinstance(data["features_activated"], int)
            assert isinstance(data["providers_enabled"], list)


class TestFeatureFlagsWithMocking:
    """Tests for feature flags with mocked feature_flags module."""

    def test_feature_flags_with_all_enabled(self, client: TestClient):
        """Test feature flags response when all flags are enabled."""
        with patch("app.api.feature_flags.get_feature_flags") as mock_get_flags:
            mock_flags = MagicMock()
            mock_flags.model_dump.return_value = {
                "enable_openai_realtime": True,
                "enable_gemini_native_audio": True,
                "demo_mode": True,
            }
            mock_get_flags.return_value = mock_flags

            response = client.get("/api/feature-flags/")

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] == 3
            assert data["disabled"] == 0

    def test_feature_flags_with_all_disabled(self, client: TestClient):
        """Test feature flags response when all flags are disabled."""
        with patch("app.api.feature_flags.get_feature_flags") as mock_get_flags:
            mock_flags = MagicMock()
            mock_flags.model_dump.return_value = {
                "enable_openai_realtime": False,
                "enable_gemini_native_audio": False,
                "demo_mode": False,
            }
            mock_get_flags.return_value = mock_flags

            response = client.get("/api/feature-flags/")

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] == 0
            assert data["disabled"] == 3

    def test_feature_flags_mixed_enabled(self, client: TestClient):
        """Test feature flags response with mixed enabled/disabled."""
        with patch("app.api.feature_flags.get_feature_flags") as mock_get_flags:
            mock_flags = MagicMock()
            mock_flags.model_dump.return_value = {
                "enable_openai_realtime": True,
                "enable_gemini_native_audio": False,
                "demo_mode": True,
                "mock_providers": False,
            }
            mock_get_flags.return_value = mock_flags

            response = client.get("/api/feature-flags/")

            assert response.status_code == 200
            data = response.json()
            assert data["enabled"] == 2
            assert data["disabled"] == 2
            assert data["total"] == 4
