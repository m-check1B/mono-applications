"""Tests for Alertmanager webhook endpoint.

Tests that alerts from Alertmanager are received and logged correctly.
"""

import pytest
from datetime import datetime

from app.api.alert_webhooks import (
    Alert,
    AlertLabel,
    AlertAnnotation,
    AlertmanagerPayload,
)


class TestAlertModels:
    """Test alert data models."""

    def test_alert_label_model(self):
        """Test AlertLabel model."""
        label = AlertLabel(
            alertname="HighErrorRate", severity="critical", component="backend", service="api"
        )
        assert label.alertname == "HighErrorRate"
        assert label.severity == "critical"
        assert label.component == "backend"
        assert label.service == "api"

    def test_alert_annotation_model(self):
        """Test AlertAnnotation model."""
        annotation = AlertAnnotation(
            summary="Backend API is experiencing high error rate",
            description="Error rate is 15%, threshold is 5%",
            runbook="https://docs.example.com/runbooks/high-error-rate",
        )
        assert annotation.summary == "Backend API is experiencing high error rate"
        assert annotation.description == "Error rate is 15%, threshold is 5%"
        assert annotation.runbook == "https://docs.example.com/runbooks/high-error-rate"

    def test_alert_model(self):
        """Test Alert model."""
        label = AlertLabel(alertname="BackendDown", severity="critical")
        annotation = AlertAnnotation(summary="Backend API is down")

        alert = Alert(
            status="firing",
            labels=label,
            annotations=annotation,
            startsAt=datetime.now(),
            fingerprint="abc123",
            generatorURL="http://prometheus:9090",
        )
        assert alert.status == "firing"
        assert alert.labels.alertname == "BackendDown"
        assert alert.annotations.summary == "Backend API is down"
        assert alert.fingerprint == "abc123"

    def test_alertmanager_payload_model(self):
        """Test AlertmanagerPayload model."""
        label = AlertLabel(alertname="TestAlert", severity="warning")
        annotation = AlertAnnotation(summary="Test summary")

        alert = Alert(
            status="firing",
            labels=label,
            annotations=annotation,
            startsAt=datetime.now(),
            fingerprint="test123",
        )

        payload = AlertmanagerPayload(
            receiver="web.hook",
            status="firing",
            alerts=[alert],
            groupLabels={"alertname": "TestAlert"},
            commonLabels={"severity": "warning"},
            commonAnnotations={"summary": "Test summary"},
            externalURL="http://alertmanager:9093",
            version="4",
            groupKey="test-group",
        )
        assert payload.receiver == "web.hook"
        assert payload.status == "firing"
        assert len(payload.alerts) == 1
        assert payload.alerts[0].labels.alertname == "TestAlert"


class TestAlertWebhookEndpoint:
    """Test alert webhook endpoint."""

    def test_receive_firing_alert(self, client):
        """Test receiving a firing alert from Alertmanager."""
        payload = AlertmanagerPayload(
            receiver="critical-alerts",
            status="firing",
            alerts=[
                {
                    "status": "firing",
                    "labels": {"alertname": "BackendDown", "severity": "critical"},
                    "annotations": {"summary": "Backend API is down"},
                    "startsAt": "2025-12-27T10:00:00Z",
                    "fingerprint": "abc123",
                }
            ],
            groupLabels={"alertname": "BackendDown"},
            commonLabels={"severity": "critical"},
            commonAnnotations={},
            externalURL="http://alertmanager:9093",
            version="4",
            groupKey="backend-down",
        )

        response = client.post("/webhooks/alerts", json=payload.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "accepted"
        assert data["alerts_received"] == 1

    def test_receive_resolved_alert(self, client):
        """Test receiving a resolved alert from Alertmanager."""
        payload = AlertmanagerPayload(
            receiver="critical-alerts",
            status="firing",
            alerts=[
                {
                    "status": "resolved",
                    "labels": {"alertname": "BackendDown", "severity": "critical"},
                    "annotations": {"summary": "Backend API is down"},
                    "startsAt": "2025-12-27T10:00:00Z",
                    "endsAt": "2025-12-27T10:05:00Z",
                    "fingerprint": "abc123",
                }
            ],
            groupLabels={"alertname": "BackendDown"},
            commonLabels={"severity": "critical"},
            commonAnnotations={},
            externalURL="http://alertmanager:9093",
            version="4",
            groupKey="backend-down",
        )

        response = client.post("/webhooks/alerts", json=payload.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "accepted"
        assert data["alerts_received"] == 1

    def test_receive_multiple_alerts(self, client):
        """Test receiving multiple alerts at once."""
        payload = AlertmanagerPayload(
            receiver="warning-alerts",
            status="firing",
            alerts=[
                {
                    "status": "firing",
                    "labels": {"alertname": "HighErrorRate", "severity": "warning"},
                    "annotations": {"summary": "High error rate detected"},
                    "startsAt": "2025-12-27T10:00:00Z",
                    "fingerprint": "error1",
                },
                {
                    "status": "firing",
                    "labels": {"alertname": "HighLatency", "severity": "warning"},
                    "annotations": {"summary": "High latency detected"},
                    "startsAt": "2025-12-27T10:00:00Z",
                    "fingerprint": "latency1",
                },
            ],
            groupLabels={"severity": "warning"},
            commonLabels={"environment": "production"},
            commonAnnotations={},
            externalURL="http://alertmanager:9093",
            version="4",
            groupKey="warning-alerts",
        )

        response = client.post("/webhooks/alerts", json=payload.model_dump())
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "accepted"
        assert data["alerts_received"] == 2

    def test_receive_alert_with_severity_levels(self, client):
        """Test receiving alerts with different severity levels."""
        for severity in ["critical", "warning", "info"]:
            payload = AlertmanagerPayload(
                receiver="web.hook",
                status="firing",
                alerts=[
                    {
                        "status": "firing",
                        "labels": {
                            "alertname": f"Test{severity.title()}Alert",
                            "severity": severity,
                        },
                        "annotations": {"summary": f"Test {severity} alert"},
                        "startsAt": "2025-12-27T10:00:00Z",
                        "fingerprint": f"test-{severity}",
                    }
                ],
                groupLabels={"alertname": f"Test{severity.title()}Alert"},
                commonLabels={"severity": severity},
                commonAnnotations={},
                externalURL="http://alertmanager:9093",
                version="4",
                groupKey=f"test-{severity}",
            )

            response = client.post("/webhooks/alerts", json=payload.model_dump())
            assert response.status_code == 200
            assert response.json()["alerts_received"] == 1


@pytest.fixture
def client():
    """Create a test client for Alertmanager webhook endpoint."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("FastAPI not available")
        return

    from app.api.alert_webhooks import router

    try:
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        with TestClient(app) as test_client:
            yield test_client
    except ImportError:
        pytest.skip("FastAPI not available")
