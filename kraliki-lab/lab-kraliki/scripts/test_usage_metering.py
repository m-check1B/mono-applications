#!/usr/bin/env python3
"""
Test script to verify usage metering system functionality.

This script creates a test database, adds sample data, and generates reports.
Run this to verify the system is working before deployment.
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from usage_metering import (
    UsageDatabase,
    APIUsageRecord,
    ResourceUsageRecord,
    ActivityRecord,
    UsageReporter,
)


def test_api_usage():
    """Test API usage recording and reporting."""
    print("Testing API usage...")

    db_path = tempfile.mktemp(suffix=".db")
    db = UsageDatabase(db_path)

    try:
        record = APIUsageRecord(
            timestamp=datetime.now(),
            customer_id="test-customer",
            vm_id="test-vm",
            provider="anthropic",
            model="claude-3-sonnet",
            tokens_in=1000,
            tokens_out=500,
            cost_usd=0.0075,
        )

        db.record_api_usage(record)
        print("  ✓ API usage recorded")

        summary = db.get_summary(
            "test-customer", datetime.now() - timedelta(hours=1), datetime.now()
        )

        assert (
            summary["api_usage"]
            .get("anthropic", {})
            .get("claude-3-sonnet", {})
            .get("total_tokens")
            == 1500
        )
        print("  ✓ API usage summary retrieved correctly")

        print("  API usage test PASSED")
        return True

    except Exception as e:
        print(f"  ✗ API usage test FAILED: {e}")
        return False
    finally:
        db.close()
        os.unlink(db_path)


def test_resource_usage():
    """Test resource usage recording and reporting."""
    print("Testing resource usage...")

    db_path = tempfile.mktemp(suffix=".db")
    db = UsageDatabase(db_path)

    try:
        record = ResourceUsageRecord(
            timestamp=datetime.now(),
            customer_id="test-customer",
            vm_id="test-vm",
            cpu_percent=45.5,
            memory_percent=60.2,
            disk_gb=25.5,
            network_in_mb=1000.0,
            network_out_mb=500.0,
        )

        db.record_resource_usage(record)
        print("  ✓ Resource usage recorded")

        summary = db.get_summary(
            "test-customer", datetime.now() - timedelta(hours=1), datetime.now()
        )

        assert summary["resource_usage"]["avg_cpu_percent"] == 45.5
        assert summary["resource_usage"]["avg_memory_percent"] == 60.2
        assert summary["resource_usage"]["max_disk_gb"] == 25.5
        print("  ✓ Resource usage summary retrieved correctly")

        print("  Resource usage test PASSED")
        return True

    except Exception as e:
        print(f"  ✗ Resource usage test FAILED: {e}")
        return False
    finally:
        db.close()
        os.unlink(db_path)


def test_activity_logging():
    """Test activity recording and reporting."""
    print("Testing activity logging...")

    db_path = tempfile.mktemp(suffix=".db")
    db = UsageDatabase(db_path)

    try:
        record = ActivityRecord(
            timestamp=datetime.now(),
            customer_id="test-customer",
            vm_id="test-vm",
            activity_type="command",
            pattern_name="build-website",
            command="opencode run build",
            duration_seconds=45.5,
        )

        db.record_activity(record)
        print("  ✓ Activity recorded")

        summary = db.get_summary(
            "test-customer", datetime.now() - timedelta(hours=1), datetime.now()
        )

        activity = summary["activity"].get("command", {})
        assert activity["count"] == 1
        assert activity["total_duration_seconds"] == 45.5
        print("  ✓ Activity summary retrieved correctly")

        print("  Activity logging test PASSED")
        return True

    except Exception as e:
        print(f"  ✗ Activity logging test FAILED: {e}")
        return False
    finally:
        db.close()
        os.unlink(db_path)


def test_report_generation():
    """Test report generation."""
    print("Testing report generation...")

    db_path = tempfile.mktemp(suffix=".db")
    db = UsageDatabase(db_path)

    try:
        db.add_customer("test-customer", "test-vm", "pro")
        print("  ✓ Customer added")

        reporter = UsageReporter(db)
        report = reporter.generate_report("test-customer", "day")

        assert report["report_type"] == "usage_report"
        assert report["customer_id"] == "test-customer"
        assert "summary" in report
        print("  ✓ Report generated")

        print("  Report generation test PASSED")
        return True

    except Exception as e:
        print(f"  ✗ Report generation test FAILED: {e}")
        return False
    finally:
        db.close()
        os.unlink(db_path)


def test_csv_export():
    """Test CSV export."""
    print("Testing CSV export...")

    db_path = tempfile.mktemp(suffix=".db")
    csv_path = tempfile.mktemp(suffix=".csv")
    db = UsageDatabase(db_path)

    try:
        db.add_customer("test-customer", "test-vm", "starter")

        record = APIUsageRecord(
            timestamp=datetime.now(),
            customer_id="test-customer",
            vm_id="test-vm",
            provider="openai",
            model="gpt-4-turbo",
            tokens_in=2000,
            tokens_out=1000,
            cost_usd=0.05,
        )
        db.record_api_usage(record)

        reporter = UsageReporter(db)
        report = reporter.generate_report("test-customer", "day")
        reporter.export_csv(report, csv_path)

        assert os.path.exists(csv_path)
        with open(csv_path, "r") as f:
            content = f.read()
            assert "openai" in content
            assert "gpt-4-turbo" in content

        print("  ✓ CSV export successful")
        os.unlink(csv_path)

        print("  CSV export test PASSED")
        return True

    except Exception as e:
        print(f"  ✗ CSV export test FAILED: {e}")
        return False
    finally:
        db.close()
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all tests."""
    print("=" * 60)
    print("Lab by Kraliki Usage Metering - Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_api_usage,
        test_resource_usage,
        test_activity_logging,
        test_report_generation,
        test_csv_export,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✓ All tests passed! System is ready for deployment.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please fix before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
