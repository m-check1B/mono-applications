#!/usr/bin/env python3
"""Load and execute instruments (reusable agent procedures).

From Agent Zero research - procedures stored in memory,
recalled without prompt bloat.
"""

import os
import subprocess
from typing import Dict, Optional, List
from datetime import datetime

INSTRUMENTS_DIR = "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/instruments/custom"


def load_all() -> Dict[str, dict]:
    """Load all available instruments."""
    instruments = {}

    if not os.path.exists(INSTRUMENTS_DIR):
        os.makedirs(INSTRUMENTS_DIR, exist_ok=True)
        return instruments

    for name in os.listdir(INSTRUMENTS_DIR):
        folder = os.path.join(INSTRUMENTS_DIR, name)
        if not os.path.isdir(folder):
            continue

        desc_file = os.path.join(folder, f"{name}.md")
        script_file = os.path.join(folder, f"{name}.sh")

        # Also check for .py scripts
        if not os.path.exists(script_file):
            script_file = os.path.join(folder, f"{name}.py")

        if os.path.exists(desc_file) and os.path.exists(script_file):
            with open(desc_file) as f:
                description = f.read()

            instruments[name] = {
                "name": name,
                "description": description,
                "script": script_file,
                "type": "python" if script_file.endswith(".py") else "bash"
            }

    return instruments


def run(name: str, args: List[str] = None, timeout: int = 300) -> dict:
    """Execute an instrument."""
    instruments = load_all()

    if name not in instruments:
        return {
            "success": False,
            "error": f"Instrument '{name}' not found",
            "available": list(instruments.keys())
        }

    inst = instruments[name]
    script = inst["script"]

    if inst["type"] == "python":
        cmd = ["python3", script] + (args or [])
    else:
        cmd = ["bash", script] + (args or [])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(script)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "instrument": name
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_prompt_injection() -> str:
    """Get instrument descriptions for system prompt injection."""
    instruments = load_all()
    if not instruments:
        return ""

    lines = ["\n## AVAILABLE INSTRUMENTS\n"]
    lines.append("These are pre-built procedures you can invoke:\n")

    for name, info in sorted(instruments.items()):
        lines.append(f"### {name}")
        # Only include first 500 chars of description
        desc = info["description"][:500]
        if len(info["description"]) > 500:
            desc += "..."
        lines.append(desc)
        lines.append(f"\nRun with: `python3 /github/applications/kraliki-lab/kraliki-swarm/instruments/loader.py run {name}`\n")

    return "\n".join(lines)


def create_instrument(name: str, description: str, script_content: str, script_type: str = "bash") -> dict:
    """Create a new instrument."""
    folder = os.path.join(INSTRUMENTS_DIR, name)
    os.makedirs(folder, exist_ok=True)

    # Write description
    desc_file = os.path.join(folder, f"{name}.md")
    with open(desc_file, "w") as f:
        f.write(description)

    # Write script
    ext = ".py" if script_type == "python" else ".sh"
    script_file = os.path.join(folder, f"{name}{ext}")
    with open(script_file, "w") as f:
        f.write(script_content)

    # Make executable
    os.chmod(script_file, 0o755)

    return {
        "success": True,
        "instrument": name,
        "path": folder
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Kraliki Instruments System")
        print("=" * 40)
        print("\nUsage:")
        print("  python loader.py list              - List all instruments")
        print("  python loader.py run <name> [args] - Run an instrument")
        print("  python loader.py prompt            - Get prompt injection")
        sys.exit(0)

    action = sys.argv[1]

    if action == "list":
        instruments = load_all()
        if not instruments:
            print("No instruments found")
        else:
            print(f"Found {len(instruments)} instruments:\n")
            for name, info in sorted(instruments.items()):
                print(f"  {name} ({info['type']})")
                print(f"    {info['description'][:80]}...")
                print()

    elif action == "run":
        if len(sys.argv) < 3:
            print("Error: instrument name required")
            sys.exit(1)
        name = sys.argv[2]
        args = sys.argv[3:] if len(sys.argv) > 3 else []
        result = run(name, args)
        print(f"Success: {result['success']}")
        if result.get("stdout"):
            print(f"Output:\n{result['stdout']}")
        if result.get("stderr"):
            print(f"Errors:\n{result['stderr']}")
        if result.get("error"):
            print(f"Error: {result['error']}")

    elif action == "prompt":
        print(get_prompt_injection())
