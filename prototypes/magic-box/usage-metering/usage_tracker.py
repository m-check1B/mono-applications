#!/usr/bin/env python3
"""
Magic Box Usage Metering Service
================================

Collects and stores usage metrics for billing and monitoring:
- API usage (Claude, OpenAI, Gemini)
- System resources (CPU, memory, disk)
- Command usage
- Pattern usage
"""

import os
import sqlite3
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import time


class UsageMeteringService:
    """Main usage tracking service"""

    def __init__(self, db_path: str = "/opt/magic-box/usage.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path) as f:
                conn.executescript(f.read())
            conn.commit()

    def register_customer(
        self,
        customer_id: str,
        name: str,
        email: Optional[str] = None,
        vm_id: Optional[str] = None,
        billing_plan: str = "basic",
    ):
        """Register a new customer"""
        if not vm_id:
            vm_id = subprocess.check_output(["hostname", "-I"]).decode().strip()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO customers (id, name, email, vm_id, billing_plan)
                VALUES (?, ?, ?, ?, ?)
                """,
                (customer_id, name, email, vm_id, billing_plan),
            )
            conn.commit()

    def get_customer_id(self) -> Optional[str]:
        """Get the customer ID for this VM"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM customers LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def track_api_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        endpoint: Optional[str] = None,
    ) -> bool:
        """Track API usage (tokens/calls)"""
        customer_id = self.get_customer_id()
        if not customer_id:
            return False

        with sqlite3.connect(self.db_path) as conn:
            # Get provider ID
            cursor = conn.execute(
                "SELECT id, input_token_price, output_token_price FROM ai_providers WHERE name = ?",
                (provider,),
            )
            row = cursor.fetchone()
            if not row:
                return False

            provider_id, input_price, output_price = row

            # Calculate estimated cost
            estimated_cost = (input_tokens / 1_000_000) * input_price + (
                output_tokens / 1_000_000
            ) * output_price

            conn.execute(
                """
                INSERT INTO api_usage
                (customer_id, provider_id, model, input_tokens, output_tokens, estimated_cost, endpoint)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    provider_id,
                    model,
                    input_tokens,
                    output_tokens,
                    estimated_cost,
                    endpoint,
                ),
            )
            conn.commit()

        return True

    def collect_system_resources(self) -> bool:
        """Collect current system resource usage"""
        customer_id = self.get_customer_id()
        if not customer_id:
            return False

        try:
            # Get CPU usage
            cpu_percent = self._get_cpu_usage()

            # Get memory usage
            mem_info = self._get_memory_usage()

            # Get disk usage
            disk_info = self._get_disk_usage()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO resource_usage
                    (customer_id, cpu_percent, memory_percent, memory_used_mb, memory_total_mb,
                     disk_used_gb, disk_total_gb)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        customer_id,
                        cpu_percent,
                        mem_info["percent"],
                        mem_info["used_mb"],
                        mem_info["total_mb"],
                        disk_info["used_gb"],
                        disk_info["total_gb"],
                    ),
                )
                conn.commit()

            return True
        except Exception as e:
            print(f"Error collecting system resources: {e}")
            return False

    def track_command(
        self,
        command: str,
        args: Optional[str] = None,
        exit_code: Optional[int] = None,
        duration_seconds: Optional[float] = None,
    ) -> bool:
        """Track a command execution"""
        customer_id = self.get_customer_id()
        if not customer_id:
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO command_usage (customer_id, command, args, exit_code, duration_seconds)
                VALUES (?, ?, ?, ?, ?)
                """,
                (customer_id, command, args, exit_code, duration_seconds),
            )
            conn.commit()

        return True

    def track_pattern_usage(self, pattern_name: str, ai_provider: str) -> bool:
        """Track usage of a prompt pattern"""
        customer_id = self.get_customer_id()
        if not customer_id:
            return False

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO pattern_usage (customer_id, pattern_name, ai_provider)
                VALUES (?, ?, ?)
                """,
                (customer_id, pattern_name, ai_provider),
            )
            conn.commit()

        return True

    def get_usage_summary(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get usage summary for a date range"""
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # API costs
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
                (start_date.isoformat(), end_date.isoformat()),
            )
            api_summary = [dict(row) for row in cursor.fetchall()]

            # Resource usage (averages)
            cursor = conn.execute(
                """
                SELECT AVG(cpu_percent) as avg_cpu,
                       AVG(memory_percent) as avg_memory,
                       MAX(memory_percent) as max_memory
                FROM resource_usage
                WHERE timestamp BETWEEN ? AND ?
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            resource_summary = dict(cursor.fetchone())

            # Command count
            cursor = conn.execute(
                """
                SELECT COUNT(*) as total_commands, command
                FROM command_usage
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY command
                ORDER BY total_commands DESC
                LIMIT 10
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            command_summary = [dict(row) for row in cursor.fetchall()]

            # Pattern usage
            cursor = conn.execute(
                """
                SELECT pattern_name, ai_provider, COUNT(*) as usage_count
                FROM pattern_usage
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY pattern_name, ai_provider
                ORDER BY usage_count DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            pattern_summary = [dict(row) for row in cursor.fetchall()]

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "api_usage": api_summary,
            "resources": resource_summary,
            "commands": command_summary,
            "patterns": pattern_summary,
        }

    def generate_billing_report(
        self, month: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate monthly billing report"""
        if not month:
            month = datetime.now().strftime("%Y-%m")

        year, month_num = map(int, month.split("-"))
        start_date = datetime(year, month_num, 1)
        if month_num == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)

        customer_id = self.get_customer_id()
        if not customer_id:
            return None

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Calculate totals
            cursor = conn.execute(
                """
                SELECT SUM(estimated_cost) as total_api_cost
                FROM api_usage
                WHERE customer_id = ? AND timestamp BETWEEN ? AND ?
                """,
                (customer_id, start_date.isoformat(), end_date.isoformat()),
            )
            total_api_cost = cursor.fetchone()["total_api_cost"] or 0.0

            # Count commands
            cursor = conn.execute(
                """
                SELECT COUNT(*) as total_commands
                FROM command_usage
                WHERE customer_id = ? AND timestamp BETWEEN ? AND ?
                """,
                (customer_id, start_date.isoformat(), end_date.isoformat()),
            )
            total_commands = cursor.fetchone()["total_commands"] or 0

            # Compute hours (resource samples * 5 minutes / 60)
            cursor = conn.execute(
                """
                SELECT COUNT(*) as sample_count
                FROM resource_usage
                WHERE customer_id = ? AND timestamp BETWEEN ? AND ?
                """,
                (customer_id, start_date.isoformat(), end_date.isoformat()),
            )
            sample_count = cursor.fetchone()["sample_count"] or 0
            total_compute_hours = (sample_count * 5) / 60  # samples * 5min / 60min

        # Calculate total cost (API cost + compute cost)
        # Compute pricing: $0.05 per hour (typical VM cost estimate)
        compute_cost = total_compute_hours * 0.05
        total_cost = total_api_cost + compute_cost

        report = {
            "customer_id": customer_id,
            "month": month,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "total_api_cost": round(total_api_cost, 2),
            "total_compute_cost": round(compute_cost, 2),
            "total_compute_hours": round(total_compute_hours, 2),
            "total_commands": total_commands,
            "total_cost": round(total_cost, 2),
        }

        return report

    def export_usage_data(
        self,
        format: str = "json",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """Export usage data in specified format"""
        summary = self.get_usage_summary(start_date, end_date)

        if format == "json":
            return json.dumps(summary, indent=2)
        elif format == "csv":
            # Simple CSV export of API usage
            lines = ["provider,model,input_tokens,output_tokens,cost"]
            for item in summary["api_usage"]:
                lines.append(
                    f"{item['provider']},{item['model']},"
                    f"{item['input_tokens']},{item['output_tokens']},{item['total_cost']}"
                )
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            result = (
                subprocess.check_output(
                    [
                        "sh",
                        "-c",
                        "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
                    ],
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            return float(result)
        except:
            return 0.0

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage"""
        try:
            with open("/proc/meminfo") as f:
                meminfo = dict(
                    (i.split()[0].rstrip(":"), int(i.split()[1]))
                    for i in f.readlines()[:20]
                )

            total_kb = meminfo["MemTotal"]
            free_kb = meminfo["MemFree"]
            buffers_kb = meminfo["Buffers"]
            cached_kb = meminfo["Cached"]

            used_kb = total_kb - free_kb - buffers_kb - cached_kb
            total_mb = total_kb / 1024
            used_mb = used_kb / 1024

            return {
                "total_mb": total_mb,
                "used_mb": used_mb,
                "percent": (used_kb / total_kb) * 100,
            }
        except:
            return {"total_mb": 0, "used_mb": 0, "percent": 0}

    def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage"""
        try:
            result = (
                subprocess.check_output(["df", "-BG", "/"], stderr=subprocess.DEVNULL)
                .decode()
                .strip()
                .split("\n")[1]
            )

            parts = result.split()
            used_gb = float(parts[2].rstrip("G"))
            total_gb = float(parts[1].rstrip("G"))

            return {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "percent": (used_gb / total_gb) * 100,
            }
        except:
            return {"total_gb": 0, "used_gb": 0, "percent": 0}


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Magic Box Usage Metering")
    parser.add_argument("--init", action="store_true", help="Initialize database")
    parser.add_argument(
        "--register",
        nargs=3,
        metavar=("ID", "NAME", "EMAIL"),
        help="Register customer (id name email)",
    )
    parser.add_argument(
        "--collect", action="store_true", help="Collect system resources"
    )
    parser.add_argument("--summary", action="store_true", help="Show usage summary")
    parser.add_argument(
        "--report", metavar="MONTH", help="Generate billing report (YYYY-MM)"
    )
    parser.add_argument("--export", choices=["json", "csv"], help="Export usage data")
    parser.add_argument("--db", default="/opt/magic-box/usage.db", help="Database path")

    args = parser.parse_args()

    service = UsageMeteringService(args.db)

    if args.init:
        print("Database initialized")

    if args.register:
        service.register_customer(*args.register)
        print(f"Customer registered: {args.register[1]}")

    if args.collect:
        if service.collect_system_resources():
            print("System resources collected")
        else:
            print("Failed to collect resources")

    if args.summary:
        summary = service.get_usage_summary()
        print(json.dumps(summary, indent=2))

    if args.report:
        report = service.generate_billing_report(args.report)
        if report:
            print(json.dumps(report, indent=2))
        else:
            print("No report generated")

    if args.export:
        data = service.export_usage_data(args.export)
        print(data)


if __name__ == "__main__":
    main()
