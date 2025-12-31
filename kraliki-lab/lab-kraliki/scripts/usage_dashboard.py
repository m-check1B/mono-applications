#!/usr/bin/env python3
"""
Lab by Kraliki Usage Dashboard

Simple HTTP server to display usage metrics via web interface.
Binds to 127.0.0.1 for security.

Usage:
    python usage_dashboard.py --port 8080
"""

import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from usage_metering import UsageDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard."""

    def __init__(self, *args, db_path="/var/lib/magic-box/usage.db", **kwargs):
        self.db_path = db_path
        self.db = UsageDatabase(db_path)
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/index.html":
            self.send_html(self.get_dashboard_html())
        elif self.path.startswith("/api/"):
            self.send_api_response(self.path[5:])
        else:
            self.send_response(404)
            self.end_headers()

    def send_html(self, html):
        """Send HTML response."""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def send_api_response(self, endpoint):
        """Handle API requests."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        try:
            if endpoint == "customers":
                data = self.get_customers()
            elif endpoint.startswith("usage/"):
                customer_id = endpoint[6:]
                params = self.parse_query_params()
                period = params.get("period", ["month"])[0]
                data = self.get_usage_summary(customer_id, period)
            else:
                data = {"error": "Unknown endpoint"}

            self.wfile.write(json.dumps(data, indent=2, default=str).encode("utf-8"))
        except Exception as e:
            logger.error(f"API error: {e}")
            error = {"error": str(e)}
            self.wfile.write(json.dumps(error).encode("utf-8"))

    def parse_query_params(self):
        """Parse URL query parameters."""
        if "?" not in self.path:
            return {}

        query_string = self.path.split("?", 1)[1]
        params = {}

        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                if key not in params:
                    params[key] = []
                params[key].append(value)

        return params

    def get_customers(self):
        """Get list of customers."""
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, vm_id, tier, status FROM customers ORDER BY id")
        customers = []

        for row in cursor.fetchall():
            customers.append(
                {
                    "id": row["id"],
                    "vm_id": row["vm_id"],
                    "tier": row["tier"],
                    "status": row["status"],
                }
            )

        return customers

    def get_usage_summary(self, customer_id, period):
        """Get usage summary for customer."""
        from datetime import timedelta

        now = datetime.now()

        if period == "day":
            start = now - timedelta(days=1)
        elif period == "week":
            start = now - timedelta(weeks=1)
        elif period == "month":
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=30)

        summary = self.db.get_summary(customer_id, start, now)

        return {"customer_id": customer_id, "period": period, "summary": summary}

    def get_dashboard_html(self):
        """Generate dashboard HTML."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lab by Kraliki Usage Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .header h1 {{ color: #667eea; margin-bottom: 10px; }}
        .header p {{ color: #666; font-size: 14px; }}
        .controls {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        select, button {{
            padding: 10px 15px;
            border: 2px solid #667eea;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
        }}
        button {{ background: #667eea; color: white; border: none; }}
        button:hover {{ background: #764ba2; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .metric-label {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .metric-unit {{ font-size: 16px; color: #999; margin-left: 5px; }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section h2 {{ color: #667eea; margin-bottom: 20px; font-size: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{
            background: #f8f9fa;
            color: #667eea;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .loading {{ text-align: center; padding: 40px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Lab by Kraliki Usage Dashboard</h1>
            <p>Monitor resource usage, API costs, and activity metrics in real-time</p>
            <p style="margin-top: 10px; font-size: 12px;">Generated: {now_str}</p>
        </div>

        <div class="controls">
            <select id="customerSelect">
                <option value="">Loading customers...</option>
            </select>
            <select id="periodSelect">
                <option value="day">Last 24 Hours</option>
                <option value="week" selected>Last 7 Days</option>
                <option value="month">Last 30 Days</option>
            </select>
            <button onclick="loadUsage()">Refresh</button>
        </div>

        <div id="loading" class="loading">Loading data...</div>

        <div id="metrics" style="display: none;">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">API Cost</div>
                    <div class="metric-value" id="apiCost">$0.00</div>
                    <span class="metric-unit">USD</span>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Tokens</div>
                    <div class="metric-value" id="totalTokens">0</div>
                    <span class="metric-unit">tokens</span>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg CPU</div>
                    <div class="metric-value" id="avgCpu">0%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Memory</div>
                    <div class="metric-value" id="avgMemory">0%</div>
                </div>
            </div>

            <div class="section">
                <h2>🤖 API Usage</h2>
                <table id="apiTable">
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Model</th>
                            <th>Tokens In</th>
                            <th>Tokens Out</th>
                            <th>Total Tokens</th>
                            <th>Cost USD</th>
                        </tr>
                    </thead>
                    <tbody id="apiTableBody"></tbody>
                </table>
            </div>

            <div class="section">
                <h2>📈 Resource Usage</h2>
                <table>
                    <tr><td>Avg CPU</td><td id="resCpu">-</td></tr>
                    <tr><td>Avg Memory</td><td id="resMemory">-</td></tr>
                    <tr><td>Max Disk</td><td id="resDisk">-</td></tr>
                    <tr><td>Network In</td><td id="resNetIn">-</td></tr>
                    <tr><td>Network Out</td><td id="resNetOut">-</td></tr>
                </table>
            </div>

            <div class="section">
                <h2>⚡ Activity</h2>
                <table id="activityTable">
                    <thead>
                        <tr>
                            <th>Activity Type</th>
                            <th>Count</th>
                            <th>Total Duration</th>
                        </tr>
                    </thead>
                    <tbody id="activityTableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function loadCustomers() {{
            try {{
                const response = await fetch('/api/customers');
                const customers = await response.json();

                const select = document.getElementById('customerSelect');
                select.innerHTML = '<option value="">Select a customer</option>';

                customers.forEach(c => {{
                    const option = document.createElement('option');
                    option.value = c.id;
                    option.textContent = c.id + ' (' + c.tier + ')';
                    select.appendChild(option);
                }});

                if (customers.length > 0) {{
                    select.value = customers[0].id;
                    loadUsage();
                }}
            }} catch (error) {{
                console.error('Error loading customers:', error);
            }}
        }}

        async function loadUsage() {{
            const customerId = document.getElementById('customerSelect').value;
            const period = document.getElementById('periodSelect').value;

            if (!customerId) {{
                document.getElementById('loading').style.display = 'block';
                document.getElementById('metrics').style.display = 'none';
                return;
            }}

            try {{
                const response = await fetch('/api/usage/' + customerId + '?period=' + period);
                const data = await response.json();
                displayMetrics(data);
            }} catch (error) {{
                console.error('Error loading usage:', error);
            }}
        }}

        function displayMetrics(data) {{
            document.getElementById('loading').style.display = 'none';
            document.getElementById('metrics').style.display = 'block';

            const summary = data.summary;
            const apiUsage = summary.api_usage || {{}};
            const resourceUsage = summary.resource_usage || {{}};
            const activity = summary.activity || {{}};

            document.getElementById('apiCost').textContent = '$' + (apiUsage.total_cost_usd || 0).toFixed(4);

            let totalTokens = 0;
            const apiTableBody = document.getElementById('apiTableBody');
            apiTableBody.innerHTML = '';

            for (const [provider, models] of Object.entries(apiUsage)) {{
                if (provider === 'total_cost_usd') continue;

                for (const [model, modelData] of Object.entries(models)) {{
                    totalTokens += modelData.total_tokens || 0;

                    const row = document.createElement('tr');
                    row.innerHTML = '<td>' + provider + '</td>' +
                        '<td>' + model + '</td>' +
                        '<td>' + (modelData.tokens_in || 0).toLocaleString() + '</td>' +
                        '<td>' + (modelData.tokens_out || 0).toLocaleString() + '</td>' +
                        '<td>' + (modelData.total_tokens || 0).toLocaleString() + '</td>' +
                        '<td>$' + (modelData.cost_usd || 0).toFixed(4) + '</td>';
                    apiTableBody.appendChild(row);
                }}
            }}

            document.getElementById('totalTokens').textContent = totalTokens.toLocaleString();
            document.getElementById('avgCpu').textContent = (resourceUsage.avg_cpu_percent || 0).toFixed(1) + '%';
            document.getElementById('avgMemory').textContent = (resourceUsage.avg_memory_percent || 0).toFixed(1) + '%';
            document.getElementById('resCpu').textContent = (resourceUsage.avg_cpu_percent || 0).toFixed(1) + '%';
            document.getElementById('resMemory').textContent = (resourceUsage.avg_memory_percent || 0).toFixed(1) + '%';
            document.getElementById('resDisk').textContent = (resourceUsage.max_disk_gb || 0).toFixed(2) + ' GB';
            document.getElementById('resNetIn').textContent = (resourceUsage.total_network_in_mb || 0).toFixed(2) + ' MB';
            document.getElementById('resNetOut').textContent = (resourceUsage.total_network_out_mb || 0).toFixed(2) + ' MB';

            const activityTableBody = document.getElementById('activityTableBody');
            activityTableBody.innerHTML = '';

            for (const [type, typeData] of Object.entries(activity)) {{
                if (type === 'total_count') continue;

                const row = document.createElement('tr');
                row.innerHTML = '<td>' + type + '</td>' +
                    '<td>' + (typeData.count || 0) + '</td>' +
                    '<td>' + (typeData.total_duration_seconds || 0).toFixed(1) + 's</td>';
                activityTableBody.appendChild(row);
            }}
        }}

        document.getElementById('customerSelect').addEventListener('change', loadUsage);
        document.getElementById('periodSelect').addEventListener('change', loadUsage);

        loadCustomers();
    </script>
</body>
</html>"""


def create_handler(db_path):
    """Factory function to create handler with db_path."""

    class Handler(DashboardHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, db_path=db_path, **kwargs)

    return Handler


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Lab by Kraliki Usage Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument(
        "--db-path",
        default="/var/lib/magic-box/usage.db",
        help="Path to usage database",
    )

    args = parser.parse_args()

    try:
        Handler = create_handler(args.db_path)
        server = HTTPServer((args.host, args.port), Handler)
        logger.info(f"Dashboard running at http://{args.host}:{args.port}")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
