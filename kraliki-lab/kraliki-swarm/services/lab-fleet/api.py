#!/usr/bin/env python3
"""
Lab by Kraliki Fleet Management API
===================================
HTTP API for managing Lab by Kraliki VM fleet, customers, and monitoring.
Uses standard library http.server (no dependencies).
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import uuid

DB_PATH = Path("/opt/lab-fleet/fleet.db")


def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            company TEXT,
            tier TEXT DEFAULT 'starter',
            billing_status TEXT DEFAULT 'active',
            monthly_fee REAL DEFAULT 99.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vms (
            id TEXT PRIMARY KEY,
            hostname TEXT NOT NULL,
            ip_address TEXT NOT NULL UNIQUE,
            customer_id TEXT NOT NULL,
            tier TEXT NOT NULL,
            status TEXT DEFAULT 'offline',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_heartbeat TIMESTAMP,
            cpu_cores INTEGER DEFAULT 2,
            memory_gb INTEGER DEFAULT 4,
            disk_gb INTEGER DEFAULT 50,
            version TEXT DEFAULT '1.0.0',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vm_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vm_id TEXT NOT NULL,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            disk_used_gb REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vm_id) REFERENCES vms(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            vm_id TEXT,
            customer_id TEXT,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved BOOLEAN DEFAULT 0,
            FOREIGN KEY (vm_id) REFERENCES vms(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS updates (
            id TEXT PRIMARY KEY,
            version TEXT NOT NULL,
            description TEXT,
            rollout_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


class FleetAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for fleet management API"""

    def _set_cors_headers(self):
        """Enable CORS"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self._set_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def _send_error(self, status_code, message):
        """Send error response"""
        self._send_json_response(status_code, {"error": message})

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        try:
            if path == "/":
                self._handle_root()
            elif path == "/api/health":
                self._handle_health_check()
            elif path == "/api/vms":
                self._handle_list_vms(query)
            elif path.startswith("/api/vms/") and "/metrics" in path:
                vm_id = path.split("/")[3]
                self._handle_vm_metrics(vm_id, query)
            elif path.startswith("/api/vms/"):
                vm_id = path.split("/")[3]
                self._handle_get_vm(vm_id)
            elif path == "/api/customers":
                self._handle_list_customers(query)
            elif path.startswith("/api/customers/") and "/vms" in path:
                customer_id = path.split("/")[3]
                self._handle_get_customer_vms(customer_id)
            elif path.startswith("/api/customers/"):
                customer_id = path.split("/")[3]
                self._handle_get_customer(customer_id)
            elif path == "/api/metrics/fleet":
                self._handle_fleet_metrics()
            elif path == "/api/alerts":
                self._handle_list_alerts(query)
            elif path == "/api/updates":
                self._handle_list_updates()
            else:
                self._send_error(404, "Not found")
        except Exception as e:
            self._send_error(500, str(e))

    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        data = json.loads(body) if body else {}

        try:
            if path == "/api/vms":
                self._handle_create_vm(data)
            elif path.startswith("/api/vms/") and "/restart" in path:
                vm_id = path.split("/")[3]
                self._handle_restart_vm(vm_id)
            elif path.startswith("/api/vms/") and "/rebuild" in path:
                vm_id = path.split("/")[3]
                self._handle_rebuild_vm(vm_id)
            elif path == "/api/customers":
                self._handle_create_customer(data)
            elif path == "/api/alerts":
                self._handle_create_alert(data)
            elif path == "/api/seed-test-data":
                self._handle_seed_test_data()
            else:
                self._send_error(404, "Not found")
        except Exception as e:
            self._send_error(500, str(e))

    def do_PUT(self):
        """Handle PUT requests"""
        path = urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
        data = json.loads(body) if body else {}

        try:
            if path.startswith("/api/vms/") and "/status" in path:
                vm_id = path.split("/")[3]
                self._handle_update_vm_status(vm_id, data)
            elif path.startswith("/api/vms/") and "/heartbeat" in path:
                vm_id = path.split("/")[3]
                self._handle_vm_heartbeat(vm_id, data)
            elif path.startswith("/api/alerts/") and "/resolve" in path:
                alert_id = path.split("/")[3]
                self._handle_resolve_alert(alert_id)
            else:
                self._send_error(404, "Not found")
        except Exception as e:
            self._send_error(500, str(e))

    def _handle_root(self):
        """Root endpoint"""
        self._send_json_response(
            200,
            {
                "service": "Lab by Kraliki Fleet Management",
                "version": "1.0.0",
                "status": "running",
            },
        )

    def _handle_health_check(self):
        """Health check endpoint"""
        db_exists = DB_PATH.exists()
        self._send_json_response(
            200,
            {
                "status": "healthy" if db_exists else "unhealthy",
                "database": str(DB_PATH),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _handle_list_vms(self, query):
        """List all VMs, optionally filtered by status"""
        conn = get_db()
        cursor = conn.cursor()

        status = query.get("status", [None])[0]
        if status:
            cursor.execute("SELECT * FROM vms WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM vms ORDER BY hostname")

        vms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self._send_json_response(200, vms)

    def _handle_get_vm(self, vm_id):
        """Get VM details"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vms WHERE id = ?", (vm_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self._send_error(404, "VM not found")
            return

        self._send_json_response(200, dict(row))

    def _handle_create_vm(self, data):
        """Create new VM"""
        vm_id = f"vm-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        required_fields = ["hostname", "ip_address", "customer_id", "tier"]

        for field in required_fields:
            if field not in data:
                self._send_error(400, f"Missing required field: {field}")
                return

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO vms (id, hostname, ip_address, customer_id, tier, status,
                               created_at, cpu_cores, memory_gb, disk_gb, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    vm_id,
                    data["hostname"],
                    data["ip_address"],
                    data["customer_id"],
                    data["tier"],
                    data.get("status", "offline"),
                    datetime.now().isoformat(),
                    data.get("cpu_cores", 2),
                    data.get("memory_gb", 4),
                    data.get("disk_gb", 50),
                    data.get("version", "1.0.0"),
                ),
            )
            conn.commit()
            conn.close()

            data["id"] = vm_id
            data["created_at"] = datetime.now().isoformat()
            self._send_json_response(201, data)
        except sqlite3.IntegrityError as e:
            conn.close()
            self._send_error(400, str(e))

    def _handle_update_vm_status(self, vm_id, data):
        """Update VM status"""
        if "status" not in data:
            self._send_error(400, "Missing required field: status")
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE vms SET status = ?, last_heartbeat = ? WHERE id = ?",
            (data["status"], datetime.now().isoformat(), vm_id),
        )
        conn.commit()
        changes = cursor.rowcount
        conn.close()

        if changes == 0:
            self._send_error(404, "VM not found")
            return

        self._send_json_response(200, {"success": True, "status": data["status"]})

    def _handle_vm_heartbeat(self, vm_id, data):
        """Handle VM heartbeat with metrics"""
        conn = get_db()
        cursor = conn.cursor()

        # Update heartbeat timestamp
        cursor.execute(
            "UPDATE vms SET last_heartbeat = ? WHERE id = ?",
            (datetime.now().isoformat(), vm_id),
        )

        # Store metrics if provided
        if "cpu_percent" in data:
            cursor.execute(
                """
                INSERT INTO vm_metrics (vm_id, cpu_percent, memory_percent, 
                                      disk_percent, disk_used_gb)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    vm_id,
                    data.get("cpu_percent"),
                    data.get("memory_percent"),
                    data.get("disk_percent"),
                    data.get("disk_used_gb"),
                ),
            )

        conn.commit()
        conn.close()
        self._send_json_response(200, {"success": True})

    def _handle_restart_vm(self, vm_id):
        """Restart VM via SSH (placeholder)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address FROM vms WHERE id = ?", (vm_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self._send_error(404, "VM not found")
            return

        # In production, this would execute SSH command
        # For now, return success message
        self._send_json_response(
            200, {"success": True, "message": f"Restart command queued for VM {vm_id}"}
        )

    def _handle_rebuild_vm(self, vm_id):
        """Rebuild VM using provisioning script (placeholder)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT ip_address FROM vms WHERE id = ?", (vm_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self._send_error(404, "VM not found")
            return

        # In production, this would execute provisioning script
        self._send_json_response(
            200, {"success": True, "message": f"Rebuild command queued for VM {vm_id}"}
        )

    def _handle_list_customers(self, query):
        """List all customers"""
        conn = get_db()
        cursor = conn.cursor()

        billing_status = query.get("billing_status", [None])[0]
        if billing_status:
            cursor.execute(
                "SELECT * FROM customers WHERE billing_status = ?", (billing_status,)
            )
        else:
            cursor.execute("SELECT * FROM customers ORDER BY name")

        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self._send_json_response(200, customers)

    def _handle_get_customer(self, customer_id):
        """Get customer details"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self._send_error(404, "Customer not found")
            return

        self._send_json_response(200, dict(row))

    def _handle_create_customer(self, data):
        """Create new customer"""
        customer_id = (
            f"cust-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        )
        required_fields = ["name", "email"]

        for field in required_fields:
            if field not in data:
                self._send_error(400, f"Missing required field: {field}")
                return

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO customers (id, name, email, company, tier, billing_status,
                                     monthly_fee, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    customer_id,
                    data["name"],
                    data["email"],
                    data.get("company"),
                    data.get("tier", "starter"),
                    data.get("billing_status", "active"),
                    data.get("monthly_fee", 99.0),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()

            data["id"] = customer_id
            data["created_at"] = datetime.now().isoformat()
            self._send_json_response(201, data)
        except sqlite3.IntegrityError as e:
            conn.close()
            self._send_error(400, str(e))

    def _handle_get_customer_vms(self, customer_id):
        """Get VMs for a customer"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vms WHERE customer_id = ?", (customer_id,))
        vms = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self._send_json_response(200, vms)

    def _handle_fleet_metrics(self):
        """Get fleet-wide metrics"""
        conn = get_db()
        cursor = conn.cursor()

        # VM counts
        cursor.execute("SELECT COUNT(*) FROM vms")
        total_vms = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vms WHERE status = 'online'")
        online_vms = cursor.fetchone()[0]

        offline_vms = total_vms - online_vms

        # Customer counts
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        # Revenue
        cursor.execute(
            "SELECT SUM(monthly_fee) FROM customers WHERE billing_status = 'active'"
        )
        revenue_row = cursor.fetchone()
        revenue = revenue_row[0] or 0.0

        # Costs (estimate from VM specs)
        cursor.execute("""
            SELECT SUM(cpu_cores * 10 + memory_gb * 2 + disk_gb * 0.1)
            FROM vms WHERE status = 'online'
        """)
        cost_row = cursor.fetchone()
        cost = cost_row[0] or 0.0

        # Average resource usage
        cursor.execute("""
            SELECT AVG(cpu_percent), AVG(memory_percent)
            FROM vm_metrics
            WHERE timestamp > datetime('now', '-1 hour')
        """)
        row = cursor.fetchone()
        avg_cpu = row[0] or 0.0
        avg_memory = row[1] or 0.0

        # Alerts
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = 0")
        alerts_count = cursor.fetchone()[0]

        conn.close()

        self._send_json_response(
            200,
            {
                "total_vms": total_vms,
                "total_customers": total_customers,
                "online_vms": online_vms,
                "offline_vms": offline_vms,
                "monthly_revenue": round(revenue, 2),
                "monthly_cost": round(cost, 2),
                "avg_cpu": round(avg_cpu, 2),
                "avg_memory": round(avg_memory, 2),
                "alerts_count": alerts_count,
            },
        )

    def _handle_vm_metrics(self, vm_id, query):
        """Get VM metrics history"""
        hours = int(query.get("hours", [24])[0])
        start_time = datetime.now() - timedelta(hours=hours)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM vm_metrics
            WHERE vm_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 100
        """,
            (vm_id, start_time.isoformat()),
        )
        metrics = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self._send_json_response(200, metrics)

    def _handle_list_alerts(self, query):
        """List alerts"""
        conn = get_db()
        cursor = conn.cursor()

        resolved = query.get("resolved", [None])[0]
        if resolved is not None:
            resolved_bool = resolved.lower() == "true"
            cursor.execute(
                "SELECT * FROM alerts WHERE resolved = ? ORDER BY created_at DESC",
                (resolved_bool,),
            )
        else:
            cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 50")

        alerts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self._send_json_response(200, alerts)

    def _handle_create_alert(self, data):
        """Create alert"""
        alert_id = (
            f"alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
        )

        required_fields = ["type", "severity", "message"]
        for field in required_fields:
            if field not in data:
                self._send_error(400, f"Missing required field: {field}")
                return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (id, vm_id, customer_id, type, severity, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                alert_id,
                data.get("vm_id"),
                data.get("customer_id"),
                data["type"],
                data["severity"],
                data["message"],
            ),
        )
        conn.commit()
        conn.close()

        data["id"] = alert_id
        data["created_at"] = datetime.now().isoformat()
        data["resolved"] = False
        self._send_json_response(201, data)

    def _handle_resolve_alert(self, alert_id):
        """Mark alert as resolved"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        changes = cursor.rowcount
        conn.close()

        if changes == 0:
            self._send_error(404, "Alert not found")
            return

        self._send_json_response(200, {"success": True})

    def _handle_list_updates(self):
        """List updates"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM updates ORDER BY created_at DESC")
        updates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self._send_json_response(200, updates)

    def _handle_seed_test_data(self):
        """Seed test data for development"""
        conn = get_db()
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM vm_metrics")
        cursor.execute("DELETE FROM vms")
        cursor.execute("DELETE FROM customers")

        # Add test customers
        test_customers = [
            (
                "cust-001",
                "Acme Corp",
                "admin@acme.com",
                "Acme Corp",
                "starter",
                "active",
                99.0,
            ),
            (
                "cust-002",
                "TechStartup",
                "cto@techstartup.com",
                "TechStartup",
                "pro",
                "active",
                199.0,
            ),
            (
                "cust-003",
                "Enterprise Ltd",
                "it@enterprise.com",
                "Enterprise Ltd",
                "enterprise",
                "active",
                499.0,
            ),
        ]

        for c in test_customers:
            cursor.execute(
                """
                INSERT INTO customers (id, name, email, company, tier, billing_status, monthly_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                c,
            )

        # Add test VMs
        test_vms = [
            ("vm-001", "acme-vm-1", "10.0.1.101", "cust-001", "starter", "online"),
            ("vm-002", "tech-vm-1", "10.0.1.102", "cust-002", "pro", "online"),
            ("vm-003", "tech-vm-2", "10.0.1.103", "cust-002", "pro", "offline"),
            ("vm-004", "ent-vm-1", "10.0.1.104", "cust-003", "enterprise", "online"),
            ("vm-005", "ent-vm-2", "10.0.1.105", "cust-003", "enterprise", "online"),
        ]

        for v in test_vms:
            cursor.execute(
                """
                INSERT INTO vms (id, hostname, ip_address, customer_id, tier, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                v,
            )

        # Add some metrics
        for vm_id, _ in [(v[0], v[1]) for v in test_vms]:
            for i in range(5):
                cursor.execute(
                    """
                    INSERT INTO vm_metrics (vm_id, cpu_percent, memory_percent, disk_percent, disk_used_gb)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (vm_id, 20.0 + i * 5, 45.0 + i * 3, 30.0 + i, 15.0 + i),
                )

        # Add alerts
        test_alerts = [
            (
                "alert-001",
                "vm-003",
                "cust-002",
                "vm_offline",
                "high",
                "VM has been offline for more than 24 hours",
            ),
            (
                "alert-002",
                "vm-004",
                "cust-003",
                "disk_space",
                "warning",
                "Disk usage above 80%",
            ),
        ]

        for a in test_alerts:
            cursor.execute(
                """
                INSERT INTO alerts (id, vm_id, customer_id, type, severity, message)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                a,
            )

        conn.commit()
        conn.close()

        self._send_json_response(200, {"success": True, "message": "Test data seeded"})

    def log_message(self, format, *args):
        """Silence default logging"""
        pass


def main():
    """Start API server"""
    import argparse

    parser = argparse.ArgumentParser(description="Lab by Kraliki Fleet Management API")
    parser.add_argument("--port", type=int, default=8686, help="Port to listen on")
    parser.add_argument(
        "--db", default="/opt/lab-fleet/fleet.db", help="Database path"
    )

    args = parser.parse_args()

    global DB_PATH
    DB_PATH = Path(args.db)

    # Initialize database
    init_db()

    server = HTTPServer(("127.0.0.1", args.port), FleetAPIHandler)
    print(f"Lab by Kraliki Fleet API running on port {args.port}")
    print(f"Database: {DB_PATH}")
    print(f"Health check: http://localhost:{args.port}/api/health")
    print(f"VMs: http://localhost:{args.port}/api/vms")
    print(f"Customers: http://localhost:{args.port}/api/customers")
    print(f"Metrics: http://localhost:{args.port}/api/metrics/fleet")
    server.serve_forever()


if __name__ == "__main__":
    main()
