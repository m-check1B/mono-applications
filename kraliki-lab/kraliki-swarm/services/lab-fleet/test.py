#!/usr/bin/env python3
"""
Test script for Lab by Kraliki Fleet Management API
==========================================

Tests all API endpoints and verifies functionality.
"""

import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:8686"


def test_health():
    """Test health check endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{API_BASE}/api/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"], f"Invalid status: {data}"
    print("✓ Health check passed")


def test_seed_data():
    """Seed test data"""
    print("\nSeeding test data...")
    response = requests.post(f"{API_BASE}/api/seed-test-data")
    assert response.status_code == 200, f"Seed failed: {response.status_code}"
    print("✓ Test data seeded")


def test_list_vms():
    """Test listing VMs"""
    print("\nTesting /api/vms...")
    response = requests.get(f"{API_BASE}/api/vms")
    assert response.status_code == 200, f"List VMs failed: {response.status_code}"
    vms = response.json()
    assert len(vms) > 0, "No VMs found"
    print(f"✓ Listed {len(vms)} VMs")


def test_get_vm():
    """Test getting specific VM"""
    print("\nTesting GET /api/vms/{vm_id}...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        response = requests.get(f"{API_BASE}/api/vms/{vm_id}")
        assert response.status_code == 200, f"Get VM failed: {response.status_code}"
        vm = response.json()
        assert vm["id"] == vm_id, "VM ID mismatch"
        print(f"✓ Got VM: {vm['hostname']}")


def test_create_vm():
    """Test creating VM"""
    print("\nTesting POST /api/vms...")
    vm_data = {
        "hostname": f"test-vm-{datetime.now().strftime('%H%M%S')}",
        "ip_address": "10.0.1.200",
        "customer_id": "cust-001",
        "tier": "starter",
    }
    response = requests.post(f"{API_BASE}/api/vms", json=vm_data)
    assert response.status_code == 201, f"Create VM failed: {response.status_code}"
    vm = response.json()
    assert "id" in vm, "No VM ID returned"
    print(f"✓ Created VM: {vm['hostname']} ({vm['id']})")


def test_update_vm_status():
    """Test updating VM status"""
    print("\nTesting PUT /api/vms/{vm_id}/status...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        response = requests.put(
            f"{API_BASE}/api/vms/{vm_id}/status", json={"status": "maintenance"}
        )
        assert response.status_code == 200, (
            f"Update status failed: {response.status_code}"
        )
        print(f"✓ Updated VM status")


def test_vm_heartbeat():
    """Test VM heartbeat"""
    print("\nTesting PUT /api/vms/{vm_id}/heartbeat...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        metrics = {
            "cpu_percent": 35.5,
            "memory_percent": 55.2,
            "disk_percent": 70.0,
            "disk_used_gb": 35.0,
        }
        response = requests.put(f"{API_BASE}/api/vms/{vm_id}/heartbeat", json=metrics)
        assert response.status_code == 200, f"Heartbeat failed: {response.status_code}"
        print(f"✓ VM heartbeat sent")


def test_list_customers():
    """Test listing customers"""
    print("\nTesting /api/customers...")
    response = requests.get(f"{API_BASE}/api/customers")
    assert response.status_code == 200, f"List customers failed: {response.status_code}"
    customers = response.json()
    assert len(customers) > 0, "No customers found"
    print(f"✓ Listed {len(customers)} customers")


def test_create_customer():
    """Test creating customer"""
    print("\nTesting POST /api/customers...")
    customer_data = {
        "name": f"Test Customer {datetime.now().strftime('%H%M%S')}",
        "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
        "company": "Test Corp",
        "tier": "pro",
        "monthly_fee": 199.0,
    }
    response = requests.post(f"{API_BASE}/api/customers", json=customer_data)
    assert response.status_code == 201, (
        f"Create customer failed: {response.status_code}"
    )
    customer = response.json()
    assert "id" in customer, "No customer ID returned"
    print(f"✓ Created customer: {customer['name']} ({customer['id']})")


def test_get_customer_vms():
    """Test getting customer VMs"""
    print("\nTesting GET /api/customers/{customer_id}/vms...")
    response = requests.get(f"{API_BASE}/api/customers")
    customers = response.json()
    if customers:
        customer_id = customers[0]["id"]
        response = requests.get(f"{API_BASE}/api/customers/{customer_id}/vms")
        assert response.status_code == 200, (
            f"Get customer VMs failed: {response.status_code}"
        )
        vms = response.json()
        print(f"✓ Got {len(vms)} VMs for customer")


def test_fleet_metrics():
    """Test fleet metrics"""
    print("\nTesting /api/metrics/fleet...")
    response = requests.get(f"{API_BASE}/api/metrics/fleet")
    assert response.status_code == 200, f"Fleet metrics failed: {response.status_code}"
    metrics = response.json()
    assert "total_vms" in metrics, "Missing total_vms"
    assert "total_customers" in metrics, "Missing total_customers"
    assert "monthly_revenue" in metrics, "Missing monthly_revenue"
    assert "monthly_cost" in metrics, "Missing monthly_cost"
    print(
        f"✓ Fleet metrics: {metrics['total_vms']} VMs, {metrics['total_customers']} customers, €{metrics['monthly_revenue']}/mo"
    )


def test_vm_metrics():
    """Test VM metrics"""
    print("\nTesting GET /api/vms/{vm_id}/metrics...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        response = requests.get(f"{API_BASE}/api/vms/{vm_id}/metrics?hours=24")
        assert response.status_code == 200, f"VM metrics failed: {response.status_code}"
        metrics = response.json()
        print(f"✓ Got {len(metrics)} metric points for VM")


def test_list_alerts():
    """Test listing alerts"""
    print("\nTesting /api/alerts...")
    response = requests.get(f"{API_BASE}/api/alerts")
    assert response.status_code == 200, f"List alerts failed: {response.status_code}"
    alerts = response.json()
    print(f"✓ Listed {len(alerts)} alerts")


def test_create_alert():
    """Test creating alert"""
    print("\nTesting POST /api/alerts...")
    alert_data = {
        "vm_id": "vm-001",
        "customer_id": "cust-001",
        "type": "test_alert",
        "severity": "info",
        "message": "Test alert from test script",
    }
    response = requests.post(f"{API_BASE}/api/alerts", json=alert_data)
    assert response.status_code == 201, f"Create alert failed: {response.status_code}"
    alert = response.json()
    assert "id" in alert, "No alert ID returned"
    print(f"✓ Created alert: {alert['id']}")


def test_resolve_alert():
    """Test resolving alert"""
    print("\nTesting PUT /api/alerts/{alert_id}/resolve...")
    response = requests.get(f"{API_BASE}/api/alerts?resolved=false")
    alerts = response.json()
    if alerts:
        alert_id = alerts[0]["id"]
        response = requests.put(f"{API_BASE}/api/alerts/{alert_id}/resolve")
        assert response.status_code == 200, (
            f"Resolve alert failed: {response.status_code}"
        )
        print(f"✓ Resolved alert: {alert_id}")


def test_restart_vm():
    """Test VM restart"""
    print("\nTesting POST /api/vms/{vm_id}/restart...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        response = requests.post(f"{API_BASE}/api/vms/{vm_id}/restart")
        assert response.status_code == 200, f"Restart VM failed: {response.status_code}"
        print(f"✓ Restart command sent to VM")


def test_rebuild_vm():
    """Test VM rebuild"""
    print("\nTesting POST /api/vms/{vm_id}/rebuild...")
    response = requests.get(f"{API_BASE}/api/vms")
    vms = response.json()
    if vms:
        vm_id = vms[0]["id"]
        response = requests.post(f"{API_BASE}/api/vms/{vm_id}/rebuild")
        assert response.status_code == 200, f"Rebuild VM failed: {response.status_code}"
        print(f"✓ Rebuild command sent to VM")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Lab by Kraliki Fleet Management API - Test Suite")
    print("=" * 60)

    try:
        test_health()
        test_seed_data()
        test_list_vms()
        test_get_vm()
        test_create_vm()
        test_update_vm_status()
        test_vm_heartbeat()
        test_list_customers()
        test_create_customer()
        test_get_customer_vms()
        test_fleet_metrics()
        test_vm_metrics()
        test_list_alerts()
        test_create_alert()
        test_resolve_alert()
        test_restart_vm()
        test_rebuild_vm()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Connection error: API server not running on {API_BASE}")
        print("Start the server with: ./api.py")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
