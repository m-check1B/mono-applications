"""
Comprehensive Unit tests for Exports Router
Tests invoice generation, billable hours summary, and export formats
"""

import pytest
from datetime import datetime, timedelta
from io import StringIO
import csv

from app.routers.exports import (
    InvoiceExportRequest,
    BillableHoursSummary,
)
from app.models.time_entry import TimeEntry
from app.models.task import Project
from app.core.security import generate_id


class TestPydanticModels:
    """Tests for exports Pydantic models"""

    def test_invoice_export_request_defaults(self):
        """InvoiceExportRequest has correct defaults"""
        req = InvoiceExportRequest(
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        assert req.start_date == "2025-01-01"
        assert req.end_date == "2025-01-31"
        assert req.project_id is None
        assert req.client_name is None
        assert req.invoice_number is None
        assert req.hourly_rate is None
        assert req.format == "csv"
        assert req.include_non_billable is False

    def test_invoice_export_request_full(self):
        """InvoiceExportRequest accepts all fields"""
        req = InvoiceExportRequest(
            start_date="2025-01-01",
            end_date="2025-01-31",
            project_id="proj-123",
            client_name="Acme Corp",
            invoice_number="INV-001",
            hourly_rate=75.0,
            format="json",
            include_non_billable=True
        )
        assert req.client_name == "Acme Corp"
        assert req.hourly_rate == 75.0
        assert req.format == "json"

    def test_billable_hours_summary_model(self):
        """BillableHoursSummary validates correctly"""
        summary = BillableHoursSummary(
            total_hours=40.0,
            billable_hours=35.0,
            non_billable_hours=5.0,
            total_amount=2625.0,
            currency="USD",
            projects=[],
            date_range={"start": "2025-01-01", "end": "2025-01-31"}
        )
        assert summary.total_hours == 40.0
        assert summary.billable_hours == 35.0
        assert summary.total_amount == 2625.0


class TestBillableSummaryEndpoint:
    """Tests for billable summary endpoint"""

    def test_summary_empty_period(self, client, db, test_user, auth_headers):
        """Summary returns zeros for empty period"""
        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_hours"] == 0
        assert data["billable_hours"] == 0
        assert data["total_amount"] == 0

    def test_summary_with_entries(self, client, db, test_user, auth_headers):
        """Summary calculates correctly with entries"""
        # Create time entries
        now = datetime.utcnow()
        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=2),
            end_time=now,
            duration_seconds=7200,  # 2 hours
            billable=True,
            hourly_rate=7500,  # $75/hr in cents
            description="Test work"
        )
        db.add(entry)
        db.commit()

        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_hours"] == 2.0
        assert data["billable_hours"] == 2.0
        assert data["total_amount"] == 150.0  # 2 hours * $75

    def test_summary_invalid_date_format(self, client, auth_headers):
        """Summary rejects invalid date format"""
        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": "invalid",
                "end_date": "2025-01-31"
            },
            headers=auth_headers
        )
        assert response.status_code == 400

    def test_summary_date_range(self, client, db, test_user, auth_headers):
        """Summary respects date range filter"""
        now = datetime.utcnow()

        # Entry within range
        entry1 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            duration_seconds=3600,
            billable=True,
            hourly_rate=5000,
            description="Within range"
        )

        # Entry outside range
        entry2 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(days=30),
            end_time=now - timedelta(days=30) + timedelta(hours=1),
            duration_seconds=3600,
            billable=True,
            hourly_rate=5000,
            description="Outside range"
        )

        db.add_all([entry1, entry2])
        db.commit()

        response = client.get(
            "/exports/billable/summary",
            params={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d")
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_hours"] == 1.0  # Only entry within range


class TestWeeklyBillableEndpoint:
    """Tests for weekly billable breakdown"""

    def test_weekly_empty(self, client, db, test_user, auth_headers):
        """Weekly returns empty for no entries"""
        response = client.get(
            "/exports/billable/weekly",
            params={"weeks": 4},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["weeks"] == []
        assert data["summary"]["total_weeks"] == 0

    def test_weekly_with_entries(self, client, db, test_user, auth_headers):
        """Weekly breaks down by week correctly"""
        now = datetime.utcnow()

        # Create entries for this week
        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=2),
            end_time=now,
            duration_seconds=7200,
            billable=True,
            hourly_rate=5000,
            description="This week"
        )
        db.add(entry)
        db.commit()

        response = client.get(
            "/exports/billable/weekly",
            params={"weeks": 4},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["weeks"]) >= 1
        assert data["summary"]["total_weeks"] >= 1

    def test_weekly_custom_weeks(self, client, auth_headers):
        """Weekly accepts custom week count"""
        for weeks in [1, 4, 12, 52]:
            response = client.get(
                "/exports/billable/weekly",
                params={"weeks": weeks},
                headers=auth_headers
            )
            assert response.status_code == 200


class TestInvoiceGenerationEndpoint:
    """Tests for invoice generation"""

    def test_generate_invoice_no_entries(self, client, db, test_user, auth_headers):
        """Generate invoice fails with no entries"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "format": "json"
            },
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "No billable hours" in response.json()["detail"]

    def test_generate_invoice_json_format(self, client, db, test_user, auth_headers):
        """Generate JSON invoice with entries"""
        now = datetime.utcnow()

        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=8),
            end_time=now,
            duration_seconds=28800,  # 8 hours
            billable=True,
            hourly_rate=7500,  # $75/hr
            description="Development work"
        )
        db.add(entry)
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "client_name": "Acme Corp",
                "invoice_number": "INV-001",
                "format": "json"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "invoice" in data
        assert data["invoice"]["client_name"] == "Acme Corp"
        assert data["invoice"]["invoice_number"] == "INV-001"
        assert data["summary"]["billable_hours"] == 8.0
        assert data["summary"]["total_amount"] == 600.0

    def test_generate_invoice_csv_format(self, client, db, test_user, auth_headers):
        """Generate CSV invoice"""
        now = datetime.utcnow()

        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=4),
            end_time=now,
            duration_seconds=14400,
            billable=True,
            hourly_rate=5000,
            description="Test work"
        )
        db.add(entry)
        db.commit()

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
        assert "text/csv" in response.headers.get("content-type", "")

        # Parse CSV content
        content = response.text
        assert "INVOICE" in content
        assert "Date" in content
        assert "SUMMARY" in content

    def test_generate_invoice_with_hourly_rate_override(self, client, db, test_user, auth_headers):
        """Generate invoice with hourly rate override"""
        now = datetime.utcnow()

        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=1),
            end_time=now,
            duration_seconds=3600,
            billable=True,
            hourly_rate=5000,  # $50/hr original
            description="Work"
        )
        db.add(entry)
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "hourly_rate": 100.0,  # Override to $100/hr
                "format": "json"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_amount"] == 100.0  # 1 hr * $100

    def test_generate_invoice_with_project_filter(self, client, db, test_user, auth_headers):
        """Generate invoice filtered by project"""
        now = datetime.utcnow()

        # Create project
        project = Project(
            id=generate_id(),
            userId=test_user.id,
            name="Client Project",
            createdAt=now
        )
        db.add(project)
        db.flush()

        # Entry with project
        entry1 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            project_id=project.id,
            start_time=now - timedelta(hours=2),
            end_time=now,
            duration_seconds=7200,
            billable=True,
            hourly_rate=5000,
            description="Project work"
        )

        # Entry without project
        entry2 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=4),
            end_time=now - timedelta(hours=2),
            duration_seconds=7200,
            billable=True,
            hourly_rate=5000,
            description="Other work"
        )

        db.add_all([entry1, entry2])
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "project_id": project.id,
                "format": "json"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["billable_hours"] == 2.0  # Only project entry

    def test_generate_invoice_include_non_billable(self, client, db, test_user, auth_headers):
        """Generate invoice including non-billable time"""
        now = datetime.utcnow()

        # Billable entry
        entry1 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=2),
            end_time=now,
            duration_seconds=7200,
            billable=True,
            hourly_rate=5000,
            description="Billable"
        )

        # Non-billable entry
        entry2 = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=4),
            end_time=now - timedelta(hours=2),
            duration_seconds=7200,
            billable=False,
            hourly_rate=0,
            description="Non-billable"
        )

        db.add_all([entry1, entry2])
        db.commit()

        # Without non-billable
        response1 = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "include_non_billable": False,
                "format": "json"
            },
            headers=auth_headers
        )
        data1 = response1.json()
        assert data1["summary"]["total_hours"] == 2.0

        # With non-billable
        response2 = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "include_non_billable": True,
                "format": "json"
            },
            headers=auth_headers
        )
        data2 = response2.json()
        assert data2["summary"]["total_hours"] == 4.0

    def test_generate_invoice_invalid_date(self, client, auth_headers):
        """Generate invoice rejects invalid date"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "invalid-date",
                "end_date": "2025-01-31",
                "format": "json"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]

    def test_generate_invoice_unsupported_format(self, client, auth_headers):
        """Generate invoice rejects unsupported format"""
        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "format": "xlsx"  # Not supported
            },
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error


class TestPdfGeneration:
    """Tests for PDF invoice generation"""

    def test_generate_pdf_invoice(self, client, db, test_user, auth_headers):
        """Generate PDF invoice if reportlab available"""
        now = datetime.utcnow()

        entry = TimeEntry(
            id=generate_id(),
            user_id=test_user.id,
            start_time=now - timedelta(hours=4),
            end_time=now,
            duration_seconds=14400,
            billable=True,
            hourly_rate=7500,
            description="PDF test"
        )
        db.add(entry)
        db.commit()

        response = client.post(
            "/exports/invoices/generate",
            json={
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                "end_date": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
                "client_name": "PDF Client",
                "format": "pdf"
            },
            headers=auth_headers
        )

        # May return 503 if reportlab not installed, or 200 with PDF
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            assert "application/pdf" in response.headers.get("content-type", "")
