#!/usr/bin/env python3
"""
Usage Metering REST API
======================

Provides HTTP API for querying usage data and generating reports.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import os


class UsageAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for usage API"""

    db_path = "/opt/magic-box/usage.db"  # Class variable

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        # Enable CORS
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        if path == "/api/usage/summary":
            self._get_usage_summary(query)
        elif path == "/api/usage/resources":
            self._get_resource_history(query)
        elif path == "/api/usage/api":
            self._get_api_history(query)
        elif path == "/api/usage/commands":
            self._get_command_history(query)
        elif path == "/api/usage/patterns":
            self._get_pattern_history(query)
        elif path == "/api/billing/report":
            self._get_billing_report(query)
        elif path in ("/api/health", "/health"):
            self._health_check()
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def _get_usage_summary(self, query):
        """Get usage summary for date range"""
        try:
            start_date = query.get("start", [None])[0]
            end_date = query.get("end", [None])[0]

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Determine date range
                if start_date:
                    start = datetime.fromisoformat(start_date)
                else:
                    start = datetime.now() - timedelta(days=30)

                if end_date:
                    end = datetime.fromisoformat(end_date)
                else:
                    end = datetime.now()

                # API usage
                cursor = conn.execute(
                    """
                    SELECT ai_providers.name as provider, api_usage.model as model,
                           SUM(input_tokens) as input_tokens,
                           SUM(output_tokens) as output_tokens, SUM(estimated_cost) as total_cost
                    FROM api_usage
                    JOIN ai_providers ON api_usage.provider_id = ai_providers.id
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY api_usage.model, ai_providers.name
                    """,
                    (start.isoformat(), end.isoformat()),
                )
                api_usage = [dict(row) for row in cursor.fetchall()]

                # Resource stats
                cursor = conn.execute(
                    """
                    SELECT AVG(cpu_percent) as avg_cpu,
                           AVG(memory_percent) as avg_memory,
                           MAX(memory_percent) as max_memory,
                           AVG(disk_used_gb) as avg_disk
                    FROM resource_usage
                    WHERE timestamp BETWEEN ? AND ?
                    """,
                    (start.isoformat(), end.isoformat()),
                )
                resources = dict(cursor.fetchone())

                # Total metrics
                cursor = conn.execute(
                    """
                    SELECT
                        (SELECT SUM(input_tokens) FROM api_usage WHERE timestamp BETWEEN ? AND ?) as total_input_tokens,
                        (SELECT SUM(output_tokens) FROM api_usage WHERE timestamp BETWEEN ? AND ?) as total_output_tokens,
                        (SELECT SUM(estimated_cost) FROM api_usage WHERE timestamp BETWEEN ? AND ?) as total_cost,
                        (SELECT COUNT(*) FROM command_usage WHERE timestamp BETWEEN ? AND ?) as total_commands,
                        (SELECT COUNT(*) FROM resource_usage WHERE timestamp BETWEEN ? AND ?) * 5 / 60 as compute_hours
                    """,
                    [start.isoformat(), end.isoformat()] * 5,
                )
                totals = dict(cursor.fetchone())

            response = {
                "period": {"start": start.isoformat(), "end": end.isoformat()},
                "api_usage": api_usage,
                "resources": resources,
                "totals": {
                    "input_tokens": totals["total_input_tokens"] or 0,
                    "output_tokens": totals["total_output_tokens"] or 0,
                    "cost": round(totals["total_cost"] or 0, 2),
                    "commands": totals["total_commands"] or 0,
                    "compute_hours": round(totals["compute_hours"] or 0, 2),
                },
            }

            self.wfile.write(json.dumps(response, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_resource_history(self, query):
        """Get resource usage history"""
        try:
            hours = int(query.get("hours", [24])[0])
            limit = int(query.get("limit", [100])[0])

            start = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT timestamp, cpu_percent, memory_percent, memory_used_mb,
                           disk_used_gb, disk_percent
                    FROM resource_usage
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (start.isoformat(), limit),
                )
                data = [dict(row) for row in cursor.fetchall()]

            self.wfile.write(json.dumps(data, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_api_history(self, query):
        """Get API usage history"""
        try:
            hours = int(query.get("hours", [24])[0])
            limit = int(query.get("limit", [50])[0])

            start = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT timestamp, ai_providers.name as provider, api_usage.model as model,
                           input_tokens, output_tokens, estimated_cost, endpoint
                    FROM api_usage
                    JOIN ai_providers ON api_usage.provider_id = ai_providers.id
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (start.isoformat(), limit),
                )
                data = [dict(row) for row in cursor.fetchall()]

            self.wfile.write(json.dumps(data, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_command_history(self, query):
        """Get command usage history"""
        try:
            hours = int(query.get("hours", [24])[0])
            limit = int(query.get("limit", [50])[0])

            start = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT timestamp, command, args, exit_code, duration_seconds
                    FROM command_usage
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (start.isoformat(), limit),
                )
                data = [dict(row) for row in cursor.fetchall()]

            self.wfile.write(json.dumps(data, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_pattern_history(self, query):
        """Get pattern usage history"""
        try:
            hours = int(query.get("hours", [168])[0])  # Default 7 days
            limit = int(query.get("limit", [50])[0])

            start = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT timestamp, pattern_name, ai_provider
                    FROM pattern_usage
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (start.isoformat(), limit),
                )
                data = [dict(row) for row in cursor.fetchall()]

            self.wfile.write(json.dumps(data, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_billing_report(self, query):
        """Generate billing report for a month"""
        try:
            month = query.get("month", [datetime.now().strftime("%Y-%m")])[0]

            year, month_num = map(int, month.split("-"))
            start_date = datetime(year, month_num, 1)
            if month_num == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Customer info
                cursor = conn.execute("SELECT * FROM customers LIMIT 1")
                customer = dict(cursor.fetchone()) if cursor.fetchone() else {}

                # API costs
                cursor = conn.execute(
                    """
                    SELECT ai_providers.name as provider, api_usage.model as model,
                           SUM(input_tokens) as input_tokens,
                           SUM(output_tokens) as output_tokens, SUM(estimated_cost) as cost
                    FROM api_usage
                    JOIN ai_providers ON api_usage.provider_id = ai_providers.id
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY api_usage.model, ai_providers.name
                    """,
                    (start_date.isoformat(), end_date.isoformat()),
                )
                api_costs = [dict(row) for row in cursor.fetchall()]

                # Totals
                cursor = conn.execute(
                    """
                    SELECT SUM(estimated_cost) as total_cost
                    FROM api_usage
                    WHERE timestamp BETWEEN ? AND ?
                    """,
                    (start_date.isoformat(), end_date.isoformat()),
                )
                total_cost_row = cursor.fetchone()
                total_cost = total_cost_row["total_cost"] if total_cost_row else 0

                # Compute usage
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) * 5 / 60 as hours
                    FROM resource_usage
                    WHERE timestamp BETWEEN ? AND ?
                    """,
                    (start_date.isoformat(), end_date.isoformat()),
                )
                compute_hours = cursor.fetchone()["hours"] or 0

            report = {
                "customer": customer,
                "period": {
                    "month": month,
                    "start": start_date.date().isoformat(),
                    "end": end_date.date().isoformat(),
                },
                "api_costs": api_costs,
                "compute_hours": round(compute_hours, 2),
                "total_cost": round(total_cost, 2),
            }

            self.wfile.write(json.dumps(report, indent=2).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _health_check(self):
        """Health check endpoint"""
        db_exists = Path(self.db_path).exists()

        response = {
            "status": "healthy" if db_exists else "unhealthy",
            "database": "ok" if db_exists else "not_found",
            "timestamp": datetime.now().isoformat(),
        }

        self.wfile.write(json.dumps(response, indent=2).encode())

    def log_message(self, format, *args):
        """Silence default logging"""
        pass


def main():
    """Start API server"""
    import argparse

    parser = argparse.ArgumentParser(description="Usage Metering API")
    parser.add_argument("--port", type=int, default=8585, help="Port to listen on")
    parser.add_argument("--db", default="/opt/magic-box/usage.db", help="Database path")

    args = parser.parse_args()

    # Update handler's db path (class variable)
    class HandlerWithDB(UsageAPIHandler):
        db_path = args.db

    server = HTTPServer(("0.0.0.0", args.port), HandlerWithDB)
    print(f"Usage Metering API running on port {args.port}")
    print(f"Database: {args.db}")
    print(f"Health check: http://localhost:{args.port}/api/health")
    print(f"Usage summary: http://localhost:{args.port}/api/usage/summary")
    server.serve_forever()


if __name__ == "__main__":
    main()
