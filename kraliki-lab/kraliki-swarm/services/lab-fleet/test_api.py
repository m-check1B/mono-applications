#!/usr/bin/env python3
"""
Unit tests for Lab by Kraliki Fleet Management API
=========================================

Run with: pytest -v
"""

import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import api


@pytest.fixture
def test_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Patch DB_PATH
    original_db_path = api.DB_PATH
    api.DB_PATH = Path(path)

    # Initialize database
    api.init_db()

    yield path

    # Cleanup
    if os.path.exists(path):
        os.unlink(path)
    api.DB_PATH = original_db_path


@pytest.fixture
def test_conn(test_db):
    """Get database connection for tests"""
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_db_initialization(test_conn):
    """Test that all tables are created"""
    cursor = test_conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ["customers", "vms", "vm_metrics", "alerts", "updates"]
    for table in expected_tables:
        assert table in tables


def test_create_customer(test_db):
    """Test creating a customer manually in DB"""
    conn = api.get_db()
    cursor = conn.cursor()
    
    customer_id = "cust-test-001"
    cursor.execute(
        "INSERT INTO customers (id, name, email) VALUES (?, ?, ?)",
        (customer_id, "Test User", "test@example.com")
    )
    conn.commit()
    
    # Verify
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["name"] == "Test User"
    assert row["email"] == "test@example.com"
    
    conn.close()


def test_create_vm(test_db):
    """Test creating a VM manually in DB"""
    conn = api.get_db()
    cursor = conn.cursor()
    
    # Need a customer first
    cursor.execute(
        "INSERT INTO customers (id, name, email) VALUES (?, ?, ?)",
        ("c1", "User 1", "u1@example.com")
    )
    
    vm_id = "vm-test-001"
    cursor.execute(
        "INSERT INTO vms (id, hostname, ip_address, customer_id, tier) VALUES (?, ?, ?, ?, ?)",
        (vm_id, "test-host", "1.2.3.4", "c1", "pro")
    )
    conn.commit()
    
    # Verify
    cursor.execute("SELECT * FROM vms WHERE id = ?", (vm_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row["hostname"] == "test-host"
    assert row["ip_address"] == "1.2.3.4"
    
    conn.close()
