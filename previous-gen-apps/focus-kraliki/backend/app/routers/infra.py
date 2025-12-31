from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional
import os
import signal
import subprocess
import time

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/infra", tags=["infra"])

# Start time for uptime calculation
START_TIME = time.time()


def _restart_command(service: str) -> str:
    """Return a restart command per service (uses prod scripts)."""
    if service in {"backend", "frontend"}:
        # prod scripts stop & start both; keep single entrypoint for safety
        return "../prod-stop.sh && ../prod-start.sh"
    raise ValueError("Unsupported service")

@router.get("/status")
async def get_infra_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system infrastructure status"""
    status = {
        "system": "healthy",
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": time.time(),
        "services": {}
    }

    # Check Database
    try:
        db.execute(text("SELECT 1"))
        status["services"]["database"] = "healthy"
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["system"] = "degraded"

    return status

@router.get("/logs/{service}")
async def get_service_logs(
    service: str,
    lines: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get logs for a specific service (backend/frontend)"""
    if service not in ["backend", "frontend"]:
        raise HTTPException(status_code=400, detail="Invalid service name. Use 'backend' or 'frontend'.")

    # Logs are expected in project root (parent of backend/)
    log_path = f"../{service}.log"

    if not os.path.exists(log_path):
        # Try current dir just in case
        log_path = f"{service}.log"
        if not os.path.exists(log_path):
             return {"service": service, "error": "Log file not found", "path": log_path, "content": ""}

    try:
        with open(log_path, "r") as f:
            # Read all lines and take last N
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            return {
                "service": service,
                "lines": len(last_lines),
                "content": "".join(last_lines)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.post("/restart/{service}")
async def restart_service(
    service: str,
    current_user: User = Depends(get_current_user)
):
    """Restart a service using existing prod scripts (backend/frontend).

    Security: only allow the logged-in user (single-tenant) and restrict service names.
    """
    if service not in ["backend", "frontend"]:
        raise HTTPException(status_code=400, detail="Invalid service name. Use 'backend' or 'frontend'.")

    try:
        cmd = _restart_command(service)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported service")

    cmd = _restart_command(service)
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
            timeout=60,
        )
        if completed.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Restart failed (exit {completed.returncode})")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Restart timed out")
    except Exception as e:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")

    return {"service": service, "status": "restarted"}
