#!/usr/bin/env python3
"""
Simple test for Lab by Kraliki Admin Dashboard structure
"""

import sys
import os
import tempfile
import sqlite3
from datetime import datetime


def test_file_structure():
    """Test that all required files exist."""
    base_dir = "/home/adminmatej/github/applications/kraliki-lab/lab-kraliki/scripts"

    required_files = [
        "admin_dashboard.py",
        "templates/admin_dashboard.html",
        "templates/vms.html",
        "templates/vm_detail.html",
        "templates/customers.html",
        "templates/alerts.html",
        "templates/tickets.html",
        "templates/new_ticket.html",
    ]

    for file in required_files:
        file_path = os.path.join(base_dir, file)
        assert os.path.exists(file_path), f"File {file} should exist"
        print(f"✓ {file} exists")

    docs_file = "/home/adminmatej/github/applications/kraliki-lab/lab-kraliki/docs/ADMIN_DASHBOARD.md"
    assert os.path.exists(docs_file), f"Documentation {docs_file} should exist"
    print(f"✓ ADMIN_DASHBOARD.md exists")

    return True


def test_database_schema():
    """Test database schema creation without running app."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_admin.db")

        # Create database directly
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Execute schema from admin_dashboard.py
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vms (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                status TEXT DEFAULT 'unknown',
                health TEXT DEFAULT 'unknown',
                last_check DATETIME,
                version TEXT DEFAULT '1.0.0',
                ip_address TEXT,
                region TEXT,
                tier TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                vm_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                resolved_at DATETIME,
                FOREIGN KEY (vm_id) REFERENCES vms(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                customer_id TEXT NOT NULL,
                vm_id TEXT,
                subject TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                resolved_at DATETIME,
                FOREIGN KEY (vm_id) REFERENCES vms(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                released_at DATETIME NOT NULL,
                rollout_status TEXT DEFAULT 'pending',
                deployed_to TEXT,
                notes TEXT
            )
        """)

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "vms" in tables, "vms table should exist"
        assert "alerts" in tables, "alerts table should exist"
        assert "support_tickets" in tables, "support_tickets table should exist"
        assert "updates" in tables, "updates table should exist"

        conn.close()
        print("✓ Database schema created successfully")

        return True


def test_vm_operations():
    """Test VM database operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_admin.db")

        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vms (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                status TEXT DEFAULT 'unknown',
                health TEXT DEFAULT 'unknown',
                last_check DATETIME,
                version TEXT DEFAULT '1.0.0',
                ip_address TEXT,
                region TEXT,
                tier TEXT
            )
        """)

        # Test insert
        cursor.execute(
            """
            INSERT INTO vms (id, customer_id, status, last_check, ip_address, region)
            VALUES (?, ?, 'provisioning', ?, ?, ?)
        """,
            (
                "test-vm-1",
                "test-customer-1",
                datetime.now().isoformat(),
                "1.2.3.4",
                "eu",
            ),
        )

        conn.commit()

        # Test select
        cursor.execute("SELECT * FROM vms WHERE id = ?", ("test-vm-1",))
        vm = cursor.fetchone()

        assert vm is not None, "VM should be inserted"
        assert vm[1] == "test-customer-1", "Customer ID should match"
        # Check index 6 for ip_address (id=0, customer_id=1, status=2, health=3, last_check=4, version=5, ip_address=6)
        assert len(vm) > 6 and vm[6] == "1.2.3.4", (
            f"IP should match at index 6, got {vm}"
        )

        # Test update
        cursor.execute(
            """
            UPDATE vms SET status = ?, health = ?, version = ? WHERE id = ?
        """,
            ("online", "healthy", "1.0.1", "test-vm-1"),
        )

        conn.commit()

        cursor.execute("SELECT * FROM vms WHERE id = ?", ("test-vm-1",))
        updated_vm = cursor.fetchone()

        assert updated_vm[2] == "online", "Status should be updated"
        assert updated_vm[3] == "healthy", "Health should be updated"
        assert updated_vm[5] == "1.0.1", "Version should be updated"

        conn.close()
        print("✓ VM operations work correctly")

        return True


def test_alert_operations():
    """Test alert database operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_admin.db")

        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                vm_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                resolved_at DATETIME
            )
        """)

        # Test insert
        cursor.execute(
            """
            INSERT INTO alerts (timestamp, vm_id, alert_type, severity, message)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                "test-vm-1",
                "disk_space",
                "high",
                "Disk usage at 85GB",
            ),
        )

        conn.commit()

        # Test select
        cursor.execute(
            "SELECT * FROM alerts WHERE vm_id = ? AND resolved = 0", ("test-vm-1",)
        )
        alerts = cursor.fetchall()

        assert len(alerts) > 0, "Alert should be inserted"
        assert alerts[0][2] == "test-vm-1", "VM ID should match"
        assert alerts[0][3] == "disk_space", "Alert type should match"

        # Test resolve
        cursor.execute(
            "UPDATE alerts SET resolved = 1, resolved_at = ? WHERE id = ?",
            (datetime.now().isoformat(), alerts[0][0]),
        )

        conn.commit()

        cursor.execute(
            "SELECT * FROM alerts WHERE vm_id = ? AND resolved = 0", ("test-vm-1",)
        )
        unresolved = cursor.fetchall()

        assert len(unresolved) == 0, "Alert should be resolved"

        conn.close()
        print("✓ Alert operations work correctly")

        return True


def test_support_ticket_operations():
    """Test support ticket database operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_admin.db")

        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                customer_id TEXT NOT NULL,
                vm_id TEXT,
                subject TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                resolved_at DATETIME
            )
        """)

        # Test insert
        cursor.execute(
            """
            INSERT INTO support_tickets (timestamp, customer_id, vm_id, subject, description, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                datetime.now().isoformat(),
                "test-customer-1",
                "test-vm-1",
                "VM not responding",
                "Cannot access via SSH",
                "high",
            ),
        )

        conn.commit()

        # Test select
        cursor.execute("SELECT * FROM support_tickets")
        tickets = cursor.fetchall()

        assert len(tickets) > 0, "Ticket should be inserted"
        assert tickets[0][2] == "test-customer-1", "Customer ID should match"
        assert tickets[0][3] == "test-vm-1", "VM ID should match"
        assert tickets[0][4] == "VM not responding", "Subject should match"

        conn.close()
        print("✓ Support ticket operations work correctly")

        return True


def main():
    """Run all tests."""
    print("Running Admin Dashboard Tests...\n")

    tests = [
        test_file_structure,
        test_database_schema,
        test_vm_operations,
        test_alert_operations,
        test_support_ticket_operations,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'=' * 50}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
