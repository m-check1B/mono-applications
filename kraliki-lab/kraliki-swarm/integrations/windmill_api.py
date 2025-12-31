#!/usr/bin/env python3
"""
Windmill API Server for Kraliki
================================
HTTP API bridge for Windmill workflow engine integration.

Runs on port 8101 (localhost only - SECURITY: internet-connected server).

Endpoints:
    GET  /health              - Health check
    GET  /workflows           - List workflows
    GET  /workflow/status     - Get workflow run status
    POST /workflow/create     - Create workflow from description
    POST /workflow/run        - Run a workflow
    POST /workflow/ai-create  - AI-generate workflow from natural language

Usage:
    python3 windmill_api.py
    # Then agents can call http://127.0.0.1:8101/workflow/run
"""

import json
import subprocess
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse
import urllib.request
import urllib.error

# Configuration - SECURITY: localhost only
HOST = "127.0.0.1"
PORT = 8101
WINDMILL_URL = "http://127.0.0.1:8100"

# Add parent paths for imports
KRALIKI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KRALIKI_DIR))
LOG_DIR = KRALIKI_DIR / "logs" / "integrations"


def log(msg: str, level: str = "INFO"):
    """Log with timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}")


class WindmillClient:
    """Client for Windmill REST API"""

    def __init__(self, base_url: str = WINDMILL_URL, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or self._get_token()

    def _get_token(self) -> Optional[str]:
        """Get Windmill token from secrets directory"""
        token_file = Path("/home/adminmatej/github/secrets/windmill_token.txt")
        if token_file.exists():
            return token_file.read_text().strip()
        return None

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Windmill API"""
        url = f"{self.base_url}/api{endpoint}"
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        body = json.dumps(data).encode() if data else None

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode()
                content_type = response.headers.get('Content-Type', '')
                # Handle plain text responses (like /api/version)
                if 'text/plain' in content_type:
                    return {"version": content.strip()}
                return json.loads(content)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            log(f"Windmill API error: {e.code} - {error_body}", "ERROR")
            return {"error": f"HTTP {e.code}: {error_body}"}
        except urllib.error.URLError as e:
            log(f"Windmill connection error: {e}", "ERROR")
            return {"error": f"Connection failed: {e}"}
        except Exception as e:
            log(f"Windmill request error: {e}", "ERROR")
            return {"error": str(e)}

    def get_version(self) -> Dict:
        """Get Windmill version info"""
        return self._request("GET", "/version")

    def list_workspaces(self) -> Dict:
        """List all workspaces"""
        return self._request("GET", "/workspaces/list")

    def list_scripts(self, workspace: str = "admin") -> Dict:
        """List all scripts in a workspace"""
        return self._request("GET", f"/w/{workspace}/scripts/list")

    def list_flows(self, workspace: str = "admin") -> Dict:
        """List all flows in a workspace"""
        return self._request("GET", f"/w/{workspace}/flows/list")

    def run_script(self, workspace: str, path: str, args: Dict = None) -> Dict:
        """Run a script by path"""
        payload = {"args": args or {}}
        return self._request("POST", f"/w/{workspace}/jobs/run/p/{path}", payload)

    def run_flow(self, workspace: str, path: str, args: Dict = None) -> Dict:
        """Run a flow by path"""
        payload = {"args": args or {}}
        return self._request("POST", f"/w/{workspace}/jobs/run_wait_result/f/{path}", payload)

    def get_job(self, workspace: str, job_id: str) -> Dict:
        """Get job status and result"""
        return self._request("GET", f"/w/{workspace}/jobs_u/get/{job_id}")

    def create_script(self, workspace: str, path: str, content: str,
                      language: str = "python3", summary: str = "") -> Dict:
        """Create a new script"""
        payload = {
            "path": path,
            "content": content,
            "language": language,
            "summary": summary
        }
        return self._request("POST", f"/w/{workspace}/scripts/create", payload)

    def create_flow(self, workspace: str, path: str, value: Dict,
                    summary: str = "") -> Dict:
        """Create a new flow"""
        payload = {
            "path": path,
            "value": value,
            "summary": summary
        }
        return self._request("POST", f"/w/{workspace}/flows/create", payload)


class WindmillAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Windmill API bridge"""

    client: WindmillClient = None

    def log_message(self, format, *args):
        """Override to use our logging"""
        log(f"{args[0]} {args[1]}")

    def _send_json(self, status: int, data: Dict[str, Any]):
        """Send JSON response"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self) -> Dict[str, Any]:
        """Read JSON body from request"""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/health":
            self._health_check()

        elif path == "/workflows":
            self._list_workflows(params)

        elif path == "/workflow/status":
            job_id = params.get("job_id", [""])[0]
            workspace = params.get("workspace", ["admin"])[0]
            self._get_workflow_status(workspace, job_id)

        elif path == "/version":
            self._get_version()

        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/workflow/create":
            self._create_workflow(body)

        elif path == "/workflow/run":
            self._run_workflow(body)

        elif path == "/workflow/ai-create":
            self._ai_create_workflow(body)

        elif path == "/script/create":
            self._create_script(body)

        elif path == "/script/run":
            self._run_script(body)

        else:
            self._send_json(404, {"error": "Not found"})

    def _health_check(self):
        """Health check - verify Windmill is accessible"""
        try:
            version = self.client.get_version()
            if "error" in version:
                self._send_json(503, {
                    "status": "unhealthy",
                    "service": "kraliki-windmill-api",
                    "windmill": "unreachable",
                    "error": version.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self._send_json(200, {
                    "status": "healthy",
                    "service": "kraliki-windmill-api",
                    "windmill": "connected",
                    "windmill_version": version,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as e:
            self._send_json(503, {
                "status": "unhealthy",
                "service": "kraliki-windmill-api",
                "windmill": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def _get_version(self):
        """Get Windmill version"""
        version = self.client.get_version()
        if "error" in version:
            self._send_json(500, version)
        else:
            self._send_json(200, version)

    def _list_workflows(self, params: Dict):
        """List all workflows (scripts + flows)"""
        workspace = params.get("workspace", ["admin"])[0]

        try:
            scripts = self.client.list_scripts(workspace)
            flows = self.client.list_flows(workspace)

            self._send_json(200, {
                "workspace": workspace,
                "scripts": scripts if not isinstance(scripts, dict) or "error" not in scripts else [],
                "flows": flows if not isinstance(flows, dict) or "error" not in flows else [],
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _get_workflow_status(self, workspace: str, job_id: str):
        """Get workflow run status"""
        if not job_id:
            self._send_json(400, {"error": "job_id parameter required"})
            return

        try:
            job = self.client.get_job(workspace, job_id)
            if "error" in job:
                self._send_json(500, job)
            else:
                self._send_json(200, {
                    "job_id": job_id,
                    "status": job.get("type", "unknown"),
                    "result": job.get("result"),
                    "started_at": job.get("started_at"),
                    "completed_at": job.get("completed_at"),
                    "workspace": workspace
                })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _create_workflow(self, body: Dict):
        """Create a workflow (script or flow)"""
        workflow_type = body.get("type", "script")  # script or flow
        workspace = body.get("workspace", "admin")
        path = body.get("path")
        content = body.get("content")
        summary = body.get("summary", "")
        language = body.get("language", "python3")

        if not path:
            self._send_json(400, {"error": "path is required"})
            return

        if workflow_type == "script":
            if not content:
                self._send_json(400, {"error": "content is required for scripts"})
                return
            result = self.client.create_script(workspace, path, content, language, summary)
        else:
            flow_value = body.get("value", {})
            result = self.client.create_flow(workspace, path, flow_value, summary)

        if "error" in result:
            self._send_json(500, result)
        else:
            self._send_json(200, {
                "status": "created",
                "type": workflow_type,
                "path": path,
                "workspace": workspace,
                "result": result
            })

    def _run_workflow(self, body: Dict):
        """Run a workflow (script or flow)"""
        workflow_type = body.get("type", "script")  # script or flow
        workspace = body.get("workspace", "admin")
        path = body.get("path")
        args = body.get("args", {})

        if not path:
            self._send_json(400, {"error": "path is required"})
            return

        try:
            if workflow_type == "flow":
                result = self.client.run_flow(workspace, path, args)
            else:
                result = self.client.run_script(workspace, path, args)

            if "error" in result:
                self._send_json(500, result)
            else:
                self._send_json(200, {
                    "status": "started" if workflow_type == "script" else "completed",
                    "type": workflow_type,
                    "path": path,
                    "workspace": workspace,
                    "result": result
                })
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _create_script(self, body: Dict):
        """Create a script"""
        workspace = body.get("workspace", "admin")
        path = body.get("path")
        content = body.get("content")
        language = body.get("language", "python3")
        summary = body.get("summary", "")

        if not path or not content:
            self._send_json(400, {"error": "path and content are required"})
            return

        result = self.client.create_script(workspace, path, content, language, summary)

        if "error" in result:
            self._send_json(500, result)
        else:
            self._send_json(200, {
                "status": "created",
                "type": "script",
                "path": path,
                "language": language,
                "workspace": workspace,
                "result": result
            })

    def _run_script(self, body: Dict):
        """Run a script"""
        workspace = body.get("workspace", "admin")
        path = body.get("path")
        args = body.get("args", {})

        if not path:
            self._send_json(400, {"error": "path is required"})
            return

        result = self.client.run_script(workspace, path, args)

        if "error" in result:
            self._send_json(500, result)
        else:
            self._send_json(200, {
                "status": "started",
                "type": "script",
                "path": path,
                "workspace": workspace,
                "job_id": result  # run_script returns job UUID
            })

    def _ai_create_workflow(self, body: Dict):
        """AI-generate a workflow from natural language description

        This is a placeholder for Windmill's AI generation feature.
        When configured with an AI provider, Windmill can generate
        scripts and flows from natural language descriptions.
        """
        description = body.get("description")
        workspace = body.get("workspace", "admin")
        language = body.get("language", "python3")

        if not description:
            self._send_json(400, {"error": "description is required"})
            return

        # For now, return a message about AI generation
        # In full implementation, this would call Windmill's AI endpoints
        self._send_json(200, {
            "status": "pending",
            "message": "AI workflow generation requires Windmill AI configuration",
            "description": description,
            "language": language,
            "workspace": workspace,
            "docs": "https://www.windmill.dev/docs/core_concepts/ai_generation",
            "timestamp": datetime.now().isoformat()
        })


def main():
    """Start the Windmill API bridge server"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize the Windmill client
    WindmillAPIHandler.client = WindmillClient()

    server = HTTPServer((HOST, PORT), WindmillAPIHandler)
    log(f"Kraliki Windmill API bridge starting on http://{HOST}:{PORT}")
    log(f"Windmill backend: {WINDMILL_URL}")
    log(f"Endpoints:")
    log(f"  GET  /health              - Health check")
    log(f"  GET  /version             - Windmill version")
    log(f"  GET  /workflows           - List workflows")
    log(f"  GET  /workflow/status     - Get job status")
    log(f"  POST /workflow/create     - Create workflow")
    log(f"  POST /workflow/run        - Run workflow")
    log(f"  POST /workflow/ai-create  - AI generate workflow")
    log(f"  POST /script/create       - Create script")
    log(f"  POST /script/run          - Run script")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
