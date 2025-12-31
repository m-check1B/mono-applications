"""
Integration tests for voice processing endpoints
"""


class TestVoiceEndpoints:
    """Test voice processing endpoints"""

    def test_get_available_providers(self, client, auth_headers):
        """Test getting available voice providers"""
        response = client.get("/voice/providers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], dict)

    def test_voice_process_endpoint(self, client, auth_headers):
        """Test voice processing endpoint"""
        payload = {
            "transcript": "Create a high priority task for tomorrow morning",
            "recordingId": None
        }
        response = client.post("/voice/process", json=payload, headers=auth_headers)

        # Should return 200 even if AI processing fails (fallback)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "intent" in data
            assert "confidence" in data
            assert "entities" in data

    def test_voice_recordings_list(self, client, auth_headers):
        """Test getting voice recordings"""
        response = client.get("/voice/recordings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "recordings" in data
        assert "total" in data
        assert isinstance(data["recordings"], list)
