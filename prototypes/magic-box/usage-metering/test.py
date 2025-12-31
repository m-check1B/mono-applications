#!/usr/bin/env python3
"""
Test script for Usage Metering System
==================================
"""

import sqlite3
import tempfile
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from usage_tracker import UsageMeteringService


def test_database_initialization():
    """Test database creation"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)

        # Check tables exist
        with sqlite3.connect(tmp.name) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                "customers",
                "ai_providers",
                "api_usage",
                "resource_usage",
                "command_usage",
                "pattern_usage",
                "billing_reports",
            ]

            for table in expected_tables:
                assert table in tables, f"Table {table} missing"


def test_customer_registration():
    """Test customer registration"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)

        service.register_customer(
            customer_id="test-customer-001",
            name="Test Customer",
            email="test@example.com",
            billing_plan="pro",
        )

        customer_id = service.get_customer_id()
        assert customer_id == "test-customer-001", f"Customer ID mismatch: {customer_id}"


def test_api_tracking():
    """Test API usage tracking"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)
        service.register_customer("test-customer", "Test", "test@test.com")

        result = service.track_api_usage(
            provider="claude",
            model="claude-3-5-sonnet",
            input_tokens=1000,
            output_tokens=500,
            endpoint="/v1/messages",
        )

        assert result, "Failed to track API usage"

        with sqlite3.connect(tmp.name) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM api_usage")
            count = cursor.fetchone()[0]
            assert count == 1, f"Expected 1 API record, got {count}"


def test_resource_collection():
    """Test resource collection"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)
        service.register_customer("test-customer", "Test", "test@test.com")

        result = service.collect_system_resources()

        assert result, "Failed to collect resources"

        with sqlite3.connect(tmp.name) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM resource_usage")
            count = cursor.fetchone()[0]
            assert count >= 1, f"Expected at least 1 resource record, got {count}"


def test_usage_summary():
    """Test usage summary generation"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)
        service.register_customer("test-customer", "Test", "test@test.com")

        # Add some test data
        service.track_api_usage("claude", "claude-3-5-sonnet", 1000, 500)
        service.collect_system_resources()

        summary = service.get_usage_summary()

        assert "api_usage" in summary, "Summary missing api_usage"
        assert "resources" in summary, "Summary missing resources"
        assert summary["api_usage"][0]["input_tokens"] == 1000, \
            f"Token count mismatch: {summary['api_usage'][0]['input_tokens']}"


def test_billing_report():
    """Test billing report generation"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)
        service.register_customer("test-customer", "Test", "test@test.com")

        # Add test data for current month
        service.track_api_usage("claude", "claude-3-5-sonnet", 1000000, 500000)
        service.collect_system_resources()

        report = service.generate_billing_report()

        assert report is not None, "Failed to generate report"
        assert "total_cost" in report, "Report missing total_cost"
        assert report["total_cost"] > 0, f"Invalid total_cost: {report['total_cost']}"


def test_export():
    """Test data export"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        service = UsageMeteringService(tmp.name)
        service.register_customer("test-customer", "Test", "test@test.com")

        # Add test data
        service.track_api_usage("claude", "claude-3-5-sonnet", 1000, 500)

        # Test JSON export
        json_data = service.export_usage_data("json")
        assert '"api_usage"' in json_data, "JSON export missing api_usage"

        # Test CSV export
        csv_data = service.export_usage_data("csv")
        assert "provider,model" in csv_data, "CSV export missing headers"


def main():
    """Run all tests"""
    print("=" * 60)
    print("Magic Box Usage Metering - Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("database_initialization", test_database_initialization),
        ("customer_registration", test_customer_registration),
        ("api_tracking", test_api_tracking),
        ("resource_collection", test_resource_collection),
        ("usage_summary", test_usage_summary),
        ("billing_report", test_billing_report),
        ("export", test_export),
    ]

    passed = 0
    failed = 0

    for name, test in tests:
        print(f"Testing {name}...")
        try:
            test()
            print(f"  ✅ {name} passed")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {name} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ {name} failed with exception: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
