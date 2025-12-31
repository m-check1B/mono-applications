"""
Unit tests for Exports Router
Tests invoice generation and billable hours export functionality
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task, TaskStatus, Project
from app.models.time_entry import TimeEntry
from app.routers.exports import InvoiceExportRequest, BillableHoursSummary
from app.core.security_v2 import generate_id


class TestInvoiceExportRequest:
    """Test the InvoiceExportRequest schema"""

    def test_valid_request(self):
        """Valid request with all fields"""
        request = InvoiceExportRequest(
            start_date="2025-11-01",
            end_date="2025-11-30",
            project_id="proj-123",
            client_name="Acme Corp",
            invoice_number="INV-2025-001",
            hourly_rate=75.00,
            format="csv",
            include_non_billable=False
        )
        assert request.start_date == "2025-11-01"
        assert request.end_date == "2025-11-30"
        assert request.hourly_rate == 75.00
        assert request.format == "csv"

    def test_minimal_request(self):
        """Request with only required fields"""
        request = InvoiceExportRequest(
            start_date="2025-11-01",
            end_date="2025-11-30"
        )
        assert request.project_id is None
        assert request.client_name is None
        assert request.invoice_number is None
        assert request.hourly_rate is None
        assert request.format == "csv"  # default
        assert request.include_non_billable is False  # default

    def test_json_format(self):
        """Request for JSON format"""
        request = InvoiceExportRequest(
            start_date="2025-11-01",
            end_date="2025-11-30",
            format="json"
        )
        assert request.format == "json"

    def test_pdf_format(self):
        """Request for PDF format"""
        request = InvoiceExportRequest(
            start_date="2025-11-01",
            end_date="2025-11-30",
            format="pdf"
        )
        assert request.format == "pdf"


class TestBillableHoursSummary:
    """Test the BillableHoursSummary schema"""

    def test_summary_creation(self):
        """Create summary with valid data"""
        summary = BillableHoursSummary(
            total_hours=40.0,
            billable_hours=35.0,
            non_billable_hours=5.0,
            total_amount=2625.00,
            currency="USD",
            projects=[
                {"id": "proj-1", "name": "Project A", "hours": 20.0},
                {"id": "proj-2", "name": "Project B", "hours": 15.0}
            ],
            date_range={"start": "2025-11-01", "end": "2025-11-30"}
        )
        assert summary.total_hours == 40.0
        assert summary.billable_hours == 35.0
        assert summary.total_amount == 2625.00
        assert len(summary.projects) == 2

    def test_summary_default_currency(self):
        """Default currency is USD"""
        summary = BillableHoursSummary(
            total_hours=10.0,
            billable_hours=10.0,
            non_billable_hours=0.0,
            total_amount=750.00,
            projects=[],
            date_range={"start": "2025-11-01", "end": "2025-11-07"}
        )
        assert summary.currency == "USD"


class TestGenerateInvoiceEndpoint:
    """Test the invoice generation endpoint"""

    def test_generate_invoice_csv(self, client, test_user, auth_headers, db):
        """Generate CSV invoice with billable time entries"""
        # Create a task and time entries
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Test Task",
            status=TaskStatus.IN_PROGRESS,
            priority=3
        )
        db.add(task)

        # Create billable time entry
        now = datetime.utcnow()
        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            task_id=task.id,
            start_time=now - timedelta(hours=2),
            end_time=now - timedelta(hours=1),
            duration_seconds=3600,
            billable=True,
            hourly_rate=7500  # $75.00 in cents
        )
        db.add(entry)
        db.commit()

        # Generate invoice
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "format": "csv"
            },
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_generate_invoice_json(self, client, test_user, auth_headers, db):
        """Generate JSON invoice"""
        # Create task and time entry
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="JSON Test Task",
            status=TaskStatus.COMPLETED,
            priority=4
        )
        db.add(task)

        now = datetime.utcnow()
        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            task_id=task.id,
            start_time=now - timedelta(hours=3),
            end_time=now - timedelta(hours=1),
            duration_seconds=7200,
            billable=True,
            hourly_rate=10000
        )
        db.add(entry)
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "format": "json",
                "client_name": "Test Client"
            },
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_generate_invoice_invalid_date(self, client, auth_headers):
        """Invalid date format returns 400"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "invalid-date",
                "end_date": "2025-11-30"
            },
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    def test_generate_invoice_no_entries(self, client, auth_headers):
        """No time entries returns 404"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",
                "format": "json"
            },
            headers=auth_headers
        )

        # Endpoint returns 404 when no billable hours found
        assert response.status_code == 404
        assert "No billable hours found" in response.json()["detail"]

    def test_generate_invoice_with_hourly_rate_override(self, client, test_user, auth_headers, db):
        """Override hourly rate in request"""
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Rate Override Task",
            status=TaskStatus.IN_PROGRESS,
            priority=3
        )
        db.add(task)

        now = datetime.utcnow()
        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            task_id=task.id,
            start_time=now - timedelta(hours=1),
            end_time=now,
            duration_seconds=3600,
            billable=True,
            hourly_rate=5000  # Original rate
        )
        db.add(entry)
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "hourly_rate": 100.00,  # Override to $100/hr
                "format": "json"
            },
            headers=auth_headers
        )

        assert response.status_code == 200


class TestBillableSummaryEndpoint:
    """Test billable hours summary endpoint"""

    def test_get_billable_summary(self, client, test_user, auth_headers, db):
        """Get summary of billable hours"""
        # Create task and time entries
        task = Task(
            id=generate_id(),
            userId=test_user.id,
            title="Summary Task",
            status=TaskStatus.IN_PROGRESS,
            priority=3
        )
        db.add(task)

        now = datetime.utcnow()
        for i in range(3):
            entry = TimeEntry(
                id=generate_id(),
                user_id=test_user.id,
                task_id=task.id,
                start_time=now - timedelta(days=i, hours=3),
                end_time=now - timedelta(days=i, hours=1),
                duration_seconds=7200,
                billable=(i < 2),
                hourly_rate=7500
            )
            db.add(entry)
        db.commit()

        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": (now - timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": now.strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )

        assert response.status_code == 200


class TestExportsAuthentication:
    """Test authentication requirements"""

    def test_generate_invoice_requires_auth(self, client):
        """Invoice generation requires authentication"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "2025-11-01",
                "end_date": "2025-11-30"
            }
        )

        assert response.status_code == 401

    def test_summary_requires_auth(self, client):
        """Summary endpoint requires authentication"""
        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": "2025-11-01",
                "end_date": "2025-11-30"
            }
        )

        assert response.status_code == 401
