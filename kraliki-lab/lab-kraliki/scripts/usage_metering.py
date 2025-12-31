#!/usr/bin/env python3
"""
Lab by Kraliki Usage Metering Service

Tracks and reports usage metrics for billing integration:
- API usage (Claude, OpenAI, Gemini tokens/calls)
- Compute resources (CPU, memory, disk)
- User activity (commands run, patterns used)

Usage:
    python -m usage_metering --customer-id <id> --period day|week|month
"""

import os
import sys
import json
import sqlite3
import logging
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class APIUsageRecord:
    """Record of API usage."""

    timestamp: datetime
    customer_id: str
    vm_id: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = d["timestamp"].isoformat()
        return d


@dataclass
class ResourceUsageRecord:
    """Record of compute resource usage."""

    timestamp: datetime
    customer_id: str
    vm_id: str
    cpu_percent: float
    memory_percent: float
    disk_gb: float
    network_in_mb: float
    network_out_mb: float

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = d["timestamp"].isoformat()
        return d


@dataclass
class ActivityRecord:
    """Record of user activity."""

    timestamp: datetime
    customer_id: str
    vm_id: str
    activity_type: str
    pattern_name: Optional[str]
    command: Optional[str]
    duration_seconds: Optional[float]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = d["timestamp"].isoformat()
        return d


class UsageDatabase:
    """SQLite database for storing usage metrics."""

    def __init__(self, db_path: str = "/var/lib/magic-box/usage.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Create database tables."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                customer_id TEXT NOT NULL,
                vm_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT,
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                customer_id TEXT NOT NULL,
                vm_id TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_gb REAL,
                network_in_mb REAL,
                network_out_mb REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                customer_id TEXT NOT NULL,
                vm_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                pattern_name TEXT,
                command TEXT,
                duration_seconds REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                vm_id TEXT NOT NULL,
                tier TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                status TEXT DEFAULT 'active'
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_usage_customer ON api_usage(customer_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_usage_customer ON resource_usage(customer_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_usage_timestamp ON resource_usage(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_log_customer ON activity_log(customer_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp)
        """)

        self.conn.commit()

    def record_api_usage(self, record: APIUsageRecord):
        """Store API usage record."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO api_usage
            (timestamp, customer_id, vm_id, provider, model, tokens_in, tokens_out, cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.timestamp.isoformat(),
                record.customer_id,
                record.vm_id,
                record.provider,
                record.model,
                record.tokens_in,
                record.tokens_out,
                record.cost_usd,
            ),
        )
        self.conn.commit()

    def record_resource_usage(self, record: ResourceUsageRecord):
        """Store resource usage record."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO resource_usage
            (timestamp, customer_id, vm_id, cpu_percent, memory_percent, disk_gb, network_in_mb, network_out_mb)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.timestamp.isoformat(),
                record.customer_id,
                record.vm_id,
                record.cpu_percent,
                record.memory_percent,
                record.disk_gb,
                record.network_in_mb,
                record.network_out_mb,
            ),
        )
        self.conn.commit()

    def record_activity(self, record: ActivityRecord):
        """Store activity record."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO activity_log
            (timestamp, customer_id, vm_id, activity_type, pattern_name, command, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                record.timestamp.isoformat(),
                record.customer_id,
                record.vm_id,
                record.activity_type,
                record.pattern_name,
                record.command,
                record.duration_seconds,
            ),
        )
        self.conn.commit()

    def add_customer(self, customer_id: str, vm_id: str, tier: str):
        """Add or update customer."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO customers (id, vm_id, tier, created_at, status)
            VALUES (?, ?, ?, ?, 'active')
        """,
            (customer_id, vm_id, tier, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_api_usage(
        self, customer_id: str, start: datetime, end: datetime
    ) -> List[Dict]:
        """Get API usage for a period."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM api_usage
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_resource_usage(
        self, customer_id: str, start: datetime, end: datetime
    ) -> List[Dict]:
        """Get resource usage for a period."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM resource_usage
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_activity_log(
        self, customer_id: str, start: datetime, end: datetime
    ) -> List[Dict]:
        """Get activity log for a period."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM activity_log
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_summary(self, customer_id: str, start: datetime, end: datetime) -> Dict:
        """Get usage summary for billing."""
        cursor = self.conn.cursor()

        summary = {
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "customer_id": customer_id,
            "api_usage": {},
            "resource_usage": {},
            "activity": {},
        }

        cursor.execute(
            """
            SELECT
                provider,
                model,
                SUM(tokens_in) as total_tokens_in,
                SUM(tokens_out) as total_tokens_out,
                SUM(tokens_in + tokens_out) as total_tokens,
                SUM(cost_usd) as total_cost
            FROM api_usage
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
            GROUP BY provider, model
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        api_rows = cursor.fetchall()
        total_cost = 0.0

        for row in api_rows:
            provider = row["provider"]
            model = row["model"]
            cost = row["total_cost"] or 0.0
            total_cost += cost

            if provider not in summary["api_usage"]:
                summary["api_usage"][provider] = {}

            summary["api_usage"][provider][model or "default"] = {
                "tokens_in": row["total_tokens_in"] or 0,
                "tokens_out": row["total_tokens_out"] or 0,
                "total_tokens": row["total_tokens"] or 0,
                "cost_usd": cost,
            }

        summary["api_usage"]["total_cost_usd"] = total_cost

        cursor.execute(
            """
            SELECT
                AVG(cpu_percent) as avg_cpu,
                AVG(memory_percent) as avg_memory,
                MAX(disk_gb) as max_disk,
                SUM(network_in_mb) as total_network_in,
                SUM(network_out_mb) as total_network_out
            FROM resource_usage
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        row = cursor.fetchone()
        if row:
            summary["resource_usage"] = {
                "avg_cpu_percent": round(row["avg_cpu"] or 0.0, 2),
                "avg_memory_percent": round(row["avg_memory"] or 0.0, 2),
                "max_disk_gb": round(row["max_disk"] or 0.0, 2),
                "total_network_in_mb": round(row["total_network_in"] or 0.0, 2),
                "total_network_out_mb": round(row["total_network_out"] or 0.0, 2),
            }

        cursor.execute(
            """
            SELECT
                activity_type,
                COUNT(*) as count,
                SUM(duration_seconds) as total_duration
            FROM activity_log
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
            GROUP BY activity_type
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        activity_rows = cursor.fetchall()
        for row in activity_rows:
            summary["activity"][row["activity_type"]] = {
                "count": row["count"],
                "total_duration_seconds": row["total_duration"] or 0.0,
            }

        cursor.execute(
            """
            SELECT COUNT(*) as total_activities
            FROM activity_log
            WHERE customer_id = ?
            AND timestamp BETWEEN ? AND ?
        """,
            (customer_id, start.isoformat(), end.isoformat()),
        )

        summary["activity"]["total_count"] = cursor.fetchone()["total_activities"] or 0

        return summary

    def close(self):
        """Close database connection."""
        self.conn.close()


class UsageCollector:
    """Collect usage metrics from system."""

    def __init__(self, customer_id: str, vm_id: str, db: UsageDatabase):
        self.customer_id = customer_id
        self.vm_id = vm_id
        self.db = db

    def collect_resource_usage(self) -> ResourceUsageRecord:
        """Collect current resource usage."""
        try:
            cpu = self._get_cpu_usage()
            memory = self._get_memory_usage()
            disk = self._get_disk_usage()
            network = self._get_network_usage()

            return ResourceUsageRecord(
                timestamp=datetime.now(),
                customer_id=self.customer_id,
                vm_id=self.vm_id,
                cpu_percent=cpu,
                memory_percent=memory,
                disk_gb=disk,
                network_in_mb=network["in"],
                network_out_mb=network["out"],
            )
        except Exception as e:
            logger.error(f"Failed to collect resource usage: {e}")
            raise

    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage."""
        try:
            with open("/proc/stat", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("cpu "):
                        parts = line.split()
                        idle = int(parts[4])
                        total = sum(int(p) for p in parts[1:])
                        usage = (1 - (idle / total)) * 100 if total > 0 else 0
                        return round(usage, 2)
        except Exception as e:
            logger.warning(f"Could not read CPU usage: {e}")
        return 0.0

    def _get_memory_usage(self) -> float:
        """Get memory usage percentage."""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        meminfo[parts[0].rstrip(":")] = int(parts[1])

                total = meminfo.get("MemTotal", 0)
                available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
                used = total - available
                usage = (used / total * 100) if total > 0 else 0
                return round(usage, 2)
        except Exception as e:
            logger.warning(f"Could not read memory usage: {e}")
        return 0.0

    def _get_disk_usage(self) -> float:
        """Get disk usage in GB."""
        try:
            import shutil

            usage = shutil.disk_usage("/")
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            return round(used_gb, 2)
        except Exception as e:
            logger.warning(f"Could not read disk usage: {e}")
        return 0.0

    def _get_network_usage(self) -> Dict[str, float]:
        """Get network usage in MB."""
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
                total_in = 0
                total_out = 0
                for line in lines[2:]:
                    parts = line.split()
                    if len(parts) >= 10:
                        total_in += int(parts[1])
                        total_out += int(parts[9])

                return {
                    "in": round(total_in / (1024**2), 2),
                    "out": round(total_out / (1024**2), 2),
                }
        except Exception as e:
            logger.warning(f"Could not read network usage: {e}")
        return {"in": 0.0, "out": 0.0}


class UsageReporter:
    """Generate usage reports for billing."""

    def __init__(self, db: UsageDatabase):
        self.db = db

    def generate_report(self, customer_id: str, period: str = "month") -> Dict:
        """
        Generate usage report for billing.

        Args:
            customer_id: Customer identifier
            period: Report period (day, week, month)

        Returns:
            Dictionary with usage summary
        """
        now = datetime.now()

        if period == "day":
            start = now - timedelta(days=1)
        elif period == "week":
            start = now - timedelta(weeks=1)
        elif period == "month":
            start = now - timedelta(days=30)
        else:
            raise ValueError(f"Invalid period: {period}")

        end = now

        summary = self.db.get_summary(customer_id, start, end)

        report = {
            "report_type": "usage_report",
            "generated_at": now.isoformat(),
            "customer_id": customer_id,
            "billing_period": period,
            "summary": summary,
        }

        return report

    def export_csv(self, report: Dict, output_path: str):
        """Export report to CSV format."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Report Type", "Generated At", "Customer ID", "Period"])

            summary = report["summary"]
            writer.writerow(
                [
                    report["report_type"],
                    report["generated_at"],
                    report["customer_id"],
                    report["billing_period"],
                ]
            )

            f.write("\nAPI Usage\n")
            writer.writerow(
                [
                    "Provider",
                    "Model",
                    "Tokens In",
                    "Tokens Out",
                    "Total Tokens",
                    "Cost USD",
                ]
            )

            for provider, models in summary["api_usage"].items():
                if provider == "total_cost_usd":
                    continue
                for model, data in models.items():
                    writer.writerow(
                        [
                            provider,
                            model,
                            data.get("tokens_in", 0),
                            data.get("tokens_out", 0),
                            data.get("total_tokens", 0),
                            data.get("cost_usd", 0),
                        ]
                    )

            writer.writerow([])
            writer.writerow(
                ["Total API Cost USD", summary["api_usage"].get("total_cost_usd", 0)]
            )

            f.write("\nResource Usage\n")
            writer.writerow(["Metric", "Value"])

            for metric, value in summary["resource_usage"].items():
                writer.writerow([metric, value])

            f.write("\nActivity\n")
            writer.writerow(["Activity Type", "Count", "Total Duration (seconds)"])

            for activity, data in summary["activity"].items():
                if activity == "total_count":
                    continue
                writer.writerow(
                    [
                        activity,
                        data.get("count", 0),
                        data.get("total_duration_seconds", 0),
                    ]
                )

        logger.info(f"Report exported to {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Lab by Kraliki Usage Metering")
    parser.add_argument("--customer-id", required=True, help="Customer ID")
    parser.add_argument("--vm-id", required=True, help="VM ID")
    parser.add_argument(
        "--tier", choices=["starter", "pro", "enterprise"], help="Customer tier"
    )
    parser.add_argument(
        "--period",
        choices=["day", "week", "month"],
        default="month",
        help="Report period",
    )
    parser.add_argument(
        "--collect", action="store_true", help="Collect current metrics"
    )
    parser.add_argument("--report", action="store_true", help="Generate usage report")
    parser.add_argument("--export-csv", help="Export report to CSV file")
    parser.add_argument(
        "--output", choices=["json", "text"], default="text", help="Output format"
    )

    args = parser.parse_args()

    try:
        db = UsageDatabase()

        if args.tier:
            db.add_customer(args.customer_id, args.vm_id, args.tier)
            logger.info(f"Customer {args.customer_id} added with tier {args.tier}")

        if args.collect:
            collector = UsageCollector(args.customer_id, args.vm_id, db)
            record = collector.collect_resource_usage()
            db.record_resource_usage(record)
            logger.info("Resource usage collected and stored")

        if args.report:
            reporter = UsageReporter(db)
            report = reporter.generate_report(args.customer_id, args.period)

            if args.export_csv:
                reporter.export_csv(report, args.export_csv)

            if args.output == "json":
                print(json.dumps(report, indent=2))
            else:
                print(f"\nUsage Report for {args.customer_id}")
                print(
                    f"Period: {args.period} ({report['summary']['period']['start']} to {report['summary']['period']['end']})"
                )

                api_cost = report["summary"]["api_usage"].get("total_cost_usd", 0)
                print(f"\nAPI Usage Cost: ${api_cost:.4f}")

                res = report["summary"].get("resource_usage", {})
                print(f"  Avg CPU: {res.get('avg_cpu_percent', 0)}%")
                print(f"  Avg Memory: {res.get('avg_memory_percent', 0)}%")
                print(f"  Max Disk: {res.get('max_disk_gb', 0)} GB")

                activity = report["summary"].get("activity", {})
                print(f"\nTotal Activities: {activity.get('total_count', 0)}")

        db.close()

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
