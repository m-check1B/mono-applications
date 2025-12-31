"""Auto-sync Linear on task completion."""

from extensions.hooks import register
import subprocess

@register("task_complete", priority=50)
async def sync_linear_on_complete(task_id: str, **kwargs):
    """Sync with Linear when a task is completed."""
    try:
        # Trigger Linear sync
        result = subprocess.run(
            ["python3", "/github/applications/kraliki-lab/kraliki-swarm/instruments/loader.py", "run", "sync-linear"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {"synced": result.returncode == 0}
    except Exception as e:
        return {"synced": False, "error": str(e)}
