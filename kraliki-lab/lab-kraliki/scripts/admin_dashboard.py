#!/usr/bin/env python3
"""
Lab by Kraliki Admin Dashboard for VM Fleet Management

Features:
1. VM status overview (online/offline, health)
2. Resource usage monitoring (CPU, memory, disk per VM)
3. Alert system (disk space, API quotas, unusual activity)
4. Fleet-wide metrics (total customers, revenue, costs)
5. Customer management (list, view details, billing status)
6. One-click VM restart/rebuild actions
7. Update management (track versions, roll out updates)
8. Support ticket integration

Usage:
    python -m admin_dashboard [--host 127.0.0.1] [--port 8002]
"""

import os
import sys
import json
import sqlite3
import logging
import subprocess
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).parent
DB_PATH = "/var/lib/magic-box/usage.db"
ADMIN_DB_PATH = "/var/lib/magic-box/admin.db"


@dataclass
class VMStatus:
    """VM status information."""

    vm_id: str
    customer_id: str
    status: str
    health: str
    cpu_percent: float
    memory_percent: float
    disk_gb: float
    disk_percent: float
    last_check: Optional[datetime]
    version: str
    ip_address: str


@dataclass
class Alert:
    """Alert information."""

    id: int
    timestamp: datetime
    vm_id: str
    alert_type: str
    severity: str
    message: str
    resolved: bool


@dataclass
class FleetMetrics:
    """Fleet-wide metrics."""

    total_customers: int
    active_vms: int
    total_revenue: float
    monthly_costs: float
    gross_margin: float


@dataclass
class SupportTicket:
    """Support ticket information."""

    id: int
    timestamp: datetime
    customer_id: str
    vm_id: str
    subject: str
    status: str
    priority: str


class AdminDatabase:
    """SQLite database for admin dashboard."""

    def __init__(self, db_path: str = ADMIN_DB_PATH, usage_db_path: str = DB_PATH):
        """Initialize admin database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.usage_db_path = usage_db_path
        self.usage_conn = sqlite3.connect(usage_db_path)
        self.usage_conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Create admin database tables."""
        cursor = self.conn.cursor()

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
                FOREIGN KEY (customer_id) REFERENCES customers(id),
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

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_vm ON alerts(vm_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_status ON support_tickets(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tickets_customer ON support_tickets(customer_id)
        """)

        self.conn.commit()

    def register_vm(
        self, vm_id: str, customer_id: str, ip_address: str, region: str = "eu"
    ):
        """Register a new VM in the system."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO vms (id, customer_id, status, last_check, ip_address, region)
            VALUES (?, ?, 'provisioning', ?, ?, ?)
            """,
            (
                vm_id,
                customer_id,
                datetime.now().isoformat(),
                ip_address or "N/A",
                region,
            ),
        )
        self.conn.commit()
        logger.info(f"Registered VM {vm_id} for customer {customer_id}")

    def update_vm_status(
        self, vm_id: str, status: str, health: str, version: Optional[str] = None
    ):
        """Update VM status."""
        cursor = self.conn.cursor()
        update_fields = ["status = ?", "health = ?", "last_check = ?"]
        values: List[Any] = [status, health, datetime.now().isoformat()]

        if version:
            update_fields.append("version = ?")
            values.append(version)

        values.append(vm_id)

        cursor.execute(
            f"""
            UPDATE vms SET {", ".join(update_fields)} WHERE id = ?
            """,
            values,
        )
        self.conn.commit()

    def get_all_vms(self) -> List[VMStatus]:
        """Get all VMs with current status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT v.*, c.tier
            FROM vms v
            LEFT JOIN usage_customers c ON v.customer_id = c.id
            ORDER BY v.customer_id
        """)

        usage_cursor = self.usage_conn.cursor()
        usage_cursor.execute(
            """
            SELECT ru.vm_id, ru.cpu_percent, ru.memory_percent, ru.disk_gb
            FROM resource_usage ru
            JOIN (
                SELECT vm_id, MAX(timestamp) AS latest_timestamp
                FROM resource_usage
                GROUP BY vm_id
            ) latest
              ON ru.vm_id = latest.vm_id
             AND ru.timestamp = latest.latest_timestamp
        """
        )
        usage_by_vm = {row["vm_id"]: row for row in usage_cursor.fetchall()}

        vms = []
        for row in cursor.fetchall():
            usage = usage_by_vm.get(row["id"])

            disk_percent = 0
            if usage and usage["disk_gb"]:
                disk_percent = min(100, (usage["disk_gb"] / 100.0) * 100)

            last_check = None
            if row["last_check"]:
                try:
                    last_check = datetime.fromisoformat(row["last_check"])
                except (ValueError, TypeError):
                    pass

            vms.append(
                VMStatus(
                    vm_id=row["id"],
                    customer_id=row["customer_id"],
                    status=row["status"],
                    health=row["health"],
                    cpu_percent=usage["cpu_percent"] if usage else 0,
                    memory_percent=usage["memory_percent"] if usage else 0,
                    disk_gb=usage["disk_gb"] if usage else 0,
                    disk_percent=disk_percent,
                    last_check=last_check,
                    version=row["version"] or "1.0.0",
                    ip_address=row["ip_address"] or "N/A",
                )
            )

        return vms

    def get_vm(self, vm_id: str) -> Optional[VMStatus]:
        """Get a specific VM."""
        vms = self.get_all_vms()
        return next((vm for vm in vms if vm.vm_id == vm_id), None)

    def create_alert(
        self, vm_id: str, alert_type: str, severity: str, message: str
    ) -> Optional[int]:
        """Create a new alert."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (timestamp, vm_id, alert_type, severity, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), vm_id, alert_type, severity, message),
        )
        self.conn.commit()
        alert_id = cursor.lastrowid
        logger.warning(f"Alert created for VM {vm_id}: {message}")
        return alert_id

    def get_active_alerts(self, vm_id: Optional[str] = None) -> List[Alert]:
        """Get unresolved alerts."""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM alerts WHERE resolved = 0
        """
        params: List[Any] = []

        if vm_id:
            query += " AND vm_id = ?"
            params.append(vm_id)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        return [
            Alert(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                vm_id=row["vm_id"],
                alert_type=row["alert_type"],
                severity=row["severity"],
                message=row["message"],
                resolved=bool(row["resolved"]),
            )
            for row in cursor.fetchall()
        ]

    def resolve_alert(self, alert_id: int):
        """Mark an alert as resolved."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE alerts SET resolved = 1, resolved_at = ? WHERE id = ?
            """,
            (datetime.now().isoformat(), alert_id),
        )
        self.conn.commit()

    def create_support_ticket(
        self,
        customer_id: str,
        vm_id: str,
        subject: str,
        description: str,
        priority: str = "medium",
    ) -> Optional[int]:
        """Create a new support ticket."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO support_tickets (timestamp, customer_id, vm_id, subject, description, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                customer_id,
                vm_id,
                subject,
                description,
                priority,
            ),
        )
        self.conn.commit()
        ticket_id = cursor.lastrowid
        logger.info(f"Support ticket created: {ticket_id} - {subject}")
        return ticket_id

    def get_support_tickets(self, status: Optional[str] = None) -> List[SupportTicket]:
        """Get support tickets."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM support_tickets"
        params: List[Any] = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        return [
            SupportTicket(
                id=row["id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                customer_id=row["customer_id"],
                vm_id=row["vm_id"] or "N/A",
                subject=row["subject"],
                status=row["status"],
                priority=row["priority"],
            )
            for row in cursor.fetchall()
        ]

    def get_fleet_metrics(self) -> FleetMetrics:
        """Calculate fleet-wide metrics."""
        cursor = self.usage_conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) as total FROM customers WHERE status = 'active'"
        )
        total_customers = cursor.fetchone()["total"] or 0

        cursor.execute(
            "SELECT COUNT(DISTINCT vm_id) as total FROM customers WHERE status = 'active'"
        )
        active_vms = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT SUM(cost_usd) as total FROM api_usage
            WHERE timestamp >= datetime('now', '-30 days')
        """)
        monthly_api_cost = cursor.fetchone()["total"] or 0

        monthly_vm_cost = active_vms * 50
        monthly_costs = monthly_api_cost + monthly_vm_cost

        cursor.execute("""
            SELECT c.tier, COUNT(*) as count
            FROM customers c
            WHERE c.status = 'active'
            GROUP BY c.tier
        """)
        tier_counts = {row["tier"]: row["count"] for row in cursor.fetchall()}

        monthly_revenue = 0.0
        for tier, count in tier_counts.items():
            if tier == "starter":
                monthly_revenue += count * 299
            elif tier == "pro":
                monthly_revenue += count * 499
            elif tier == "enterprise":
                monthly_revenue += count * 833

        gross_margin = monthly_revenue - monthly_costs
        if monthly_revenue > 0:
            gross_margin_pct = (gross_margin / monthly_revenue) * 100
        else:
            gross_margin_pct = 0.0

        return FleetMetrics(
            total_customers=total_customers,
            active_vms=active_vms,
            total_revenue=monthly_revenue,
            monthly_costs=monthly_costs,
            gross_margin=gross_margin_pct,
        )

    def check_disk_alerts(self):
        """Check for disk space issues and create alerts."""
        cursor = self.usage_conn.cursor()
        cursor.execute("""
            SELECT vm_id, disk_gb, customer_id
            FROM resource_usage
            WHERE timestamp >= datetime('now', '-1 hour')
            GROUP BY vm_id
            HAVING disk_gb > 80
        """)

        for row in cursor.fetchall():
            vm_id = row["vm_id"]
            existing = self.conn.cursor()
            existing.execute(
                """
                SELECT id FROM alerts
                WHERE vm_id = ? AND alert_type = 'disk_space' AND resolved = 0
                LIMIT 1
            """,
                (vm_id,),
            )

            if not existing.fetchone():
                self.create_alert(
                    vm_id=vm_id,
                    alert_type="disk_space",
                    severity="high",
                    message=f"Disk usage at {row['disk_gb']:.1f}GB (threshold: 80GB)",
                )

    def check_api_quota_alerts(self):
        """Check for API quota issues."""
        cursor = self.usage_conn.cursor()
        cursor.execute("""
            SELECT customer_id, SUM(cost_usd) as total_cost
            FROM api_usage
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY customer_id
            HAVING total_cost > 50
        """)

        for row in cursor.fetchall():
            customer_id = row["customer_id"]
            existing = self.conn.cursor()
            existing.execute(
                """
                SELECT id FROM alerts
                WHERE vm_id IN (SELECT id FROM vms WHERE customer_id = ?)
                AND alert_type = 'api_quota' AND resolved = 0
                LIMIT 1
            """,
                (customer_id,),
            )

            if not existing.fetchone():
                self.create_alert(
                    vm_id="all",
                    alert_type="api_quota",
                    severity="medium",
                    message=f"Customer {customer_id} exceeded $50 API quota this week",
                )


app = Flask(__name__)
admin_db = AdminDatabase()


@app.route("/")
def dashboard():
    """Main admin dashboard."""
    metrics = admin_db.get_fleet_metrics()
    vms = admin_db.get_all_vms()
    alerts = admin_db.get_active_alerts()[:10]
    tickets = admin_db.get_support_tickets(status="open")[:10]

    return render_template(
        "admin_dashboard.html",
        metrics=metrics,
        vms=vms,
        alerts=alerts,
        tickets=tickets,
        current_time=datetime.now(),
    )


@app.route("/vms")
def vms_page():
    """VM fleet overview page."""
    vms = admin_db.get_all_vms()
    alerts_by_vm = {vm.vm_id: admin_db.get_active_alerts(vm.vm_id) for vm in vms}

    return render_template(
        "vms.html", vms=vms, alerts_by_vm=alerts_by_vm, current_time=datetime.now()
    )


@app.route("/vms/<vm_id>")
def vm_detail(vm_id: str):
    """VM detail page."""
    vm = admin_db.get_vm(vm_id)
    if not vm:
        return "VM not found", 404

    alerts = admin_db.get_active_alerts(vm_id)
    tickets = admin_db.get_support_tickets()

    return render_template(
        "vm_detail.html",
        vm=vm,
        alerts=alerts,
        tickets=[t for t in tickets if t.vm_id == vm_id],
        current_time=datetime.now(),
    )


@app.route("/customers")
def customers_page():
    """Customer management page."""
    vms = admin_db.get_all_vms()
    tickets = admin_db.get_support_tickets()

    customers: Dict[str, Dict[str, Any]] = {}
    for vm in vms:
        if vm.customer_id not in customers:
            customers[vm.customer_id] = {"id": vm.customer_id, "vms": [], "tickets": []}
        customers[vm.customer_id]["vms"].append(vm)

    for ticket in tickets:
        if ticket.customer_id in customers:
            customers[ticket.customer_id]["tickets"].append(ticket)

    return render_template(
        "customers.html",
        customers=list(customers.values()),
        current_time=datetime.now(),
    )


@app.route("/alerts")
def alerts_page():
    """Alerts monitoring page."""
    alerts = admin_db.get_active_alerts()

    return render_template("alerts.html", alerts=alerts, current_time=datetime.now())


@app.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
def resolve_alert_route(alert_id: int):
    """Resolve an alert."""
    admin_db.resolve_alert(alert_id)
    return redirect(url_for("alerts_page"))


@app.route("/tickets")
def tickets_page():
    """Support tickets page."""
    tickets = admin_db.get_support_tickets()

    return render_template("tickets.html", tickets=tickets, current_time=datetime.now())


@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    """Create new support ticket."""
    if request.method == "POST":
        customer_id = request.form.get("customer_id", "")
        vm_id = request.form.get("vm_id", "")
        subject = request.form.get("subject", "No Subject")
        description = request.form.get("description", "")
        priority = request.form.get("priority", "medium")

        admin_db.create_support_ticket(
            customer_id, vm_id, subject, description, priority
        )
        return redirect(url_for("tickets_page"))

    vms = admin_db.get_all_vms()
    return render_template("new_ticket.html", vms=vms, current_time=datetime.now())


@app.route("/api/metrics")
def api_metrics():
    """API endpoint for fleet metrics."""
    metrics = admin_db.get_fleet_metrics()
    return jsonify(asdict(metrics))


@app.route("/api/vms")
def api_vms():
    """API endpoint for VM list."""
    vms = admin_db.get_all_vms()
    return jsonify([asdict(vm) for vm in vms])


@app.route("/api/alerts")
def api_alerts():
    """API endpoint for alerts."""
    alerts = admin_db.get_active_alerts()
    return jsonify([asdict(alert) for alert in alerts])


@app.route("/api/vms/<vm_id>/restart", methods=["POST"])
def restart_vm(vm_id: str):
    """Trigger VM restart (placeholder - integrate with Hetzner API)."""
    logger.info(f"Restart request for VM {vm_id}")

    admin_db.update_vm_status(vm_id, "restarting", "unknown")

    try:
        subprocess.run(["sudo", "systemctl", "restart", "magic-box-stack"], check=True)
        admin_db.update_vm_status(vm_id, "online", "healthy")
        return jsonify({"status": "success", "message": f"VM {vm_id} restarted"})
    except subprocess.CalledProcessError as e:
        admin_db.update_vm_status(vm_id, "error", "unhealthy")
        logger.error(f"Failed to restart VM {vm_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/vms/<vm_id>/rebuild", methods=["POST"])
def rebuild_vm(vm_id: str):
    """Trigger VM rebuild (placeholder - integrate with Hetzner API)."""
    logger.info(f"Rebuild request for VM {vm_id}")
    admin_db.update_vm_status(vm_id, "rebuilding", "unknown")

    admin_db.create_alert(
        vm_id=vm_id,
        alert_type="vm_rebuild",
        severity="info",
        message=f"VM rebuild initiated",
    )

    return jsonify({"status": "pending", "message": f"VM {vm_id} rebuild scheduled"})


def run_health_checks():
    """Run periodic health checks and create alerts."""
    admin_db.check_disk_alerts()
    admin_db.check_api_quota_alerts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab by Kraliki Admin Dashboard")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8002, help="Port to bind to (default: 8002)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    run_health_checks()

    logger.info(f"Starting admin dashboard on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
