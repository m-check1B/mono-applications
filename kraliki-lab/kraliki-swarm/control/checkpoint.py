#!/usr/bin/env python3
"""Checkpoint system for agent work rollback.

Usage:
    python3 checkpoint.py create --target /path/to/dir --label my-checkpoint
    python3 checkpoint.py restore --name my-checkpoint-20251224 --target /path/to/parent
    python3 checkpoint.py list
"""

import os
import tarfile
import argparse
from datetime import datetime

CHECKPOINT_DIR = "/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/checkpoints"


def create(target_dir: str, label: str = None) -> str:
    """Create checkpoint of target directory."""
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"{label}-{timestamp}" if label else timestamp
    path = f"{CHECKPOINT_DIR}/{name}.tar.gz"

    with tarfile.open(path, "w:gz") as tar:
        tar.add(target_dir, arcname=os.path.basename(target_dir))

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"Created checkpoint: {path} ({size_mb:.1f} MB)")
    return path


def restore(checkpoint_name: str, target_parent: str):
    """Restore checkpoint to target location."""
    path = f"{CHECKPOINT_DIR}/{checkpoint_name}"
    if not path.endswith('.tar.gz'):
        path += '.tar.gz'

    if not os.path.exists(path):
        print(f"Error: Checkpoint not found: {path}")
        return False

    with tarfile.open(path, "r:gz") as tar:
        tar.extractall(target_parent)

    print(f"Restored: {path} to {target_parent}")
    return True


def list_checkpoints():
    """List all checkpoints."""
    if not os.path.exists(CHECKPOINT_DIR):
        print("No checkpoints found")
        return []

    checkpoints = []
    for f in sorted(os.listdir(CHECKPOINT_DIR), reverse=True):
        if f.endswith('.tar.gz'):
            full_path = f"{CHECKPOINT_DIR}/{f}"
            size_mb = os.path.getsize(full_path) / 1024 / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            checkpoints.append({
                "name": f,
                "size_mb": size_mb,
                "created": mtime.isoformat()
            })
            print(f"  {f} ({size_mb:.1f} MB) - {mtime.strftime('%Y-%m-%d %H:%M')}")

    return checkpoints


def cleanup(keep_last: int = 10):
    """Remove old checkpoints, keeping only the last N."""
    if not os.path.exists(CHECKPOINT_DIR):
        return

    files = sorted(
        [f for f in os.listdir(CHECKPOINT_DIR) if f.endswith('.tar.gz')],
        key=lambda f: os.path.getmtime(f"{CHECKPOINT_DIR}/{f}"),
        reverse=True
    )

    for f in files[keep_last:]:
        os.remove(f"{CHECKPOINT_DIR}/{f}")
        print(f"Removed old checkpoint: {f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kraliki Checkpoint System")
    parser.add_argument("action", choices=["create", "restore", "list", "cleanup"])
    parser.add_argument("--target", "-t", help="Target directory")
    parser.add_argument("--label", "-l", help="Checkpoint label")
    parser.add_argument("--name", "-n", help="Checkpoint name to restore")
    parser.add_argument("--keep", "-k", type=int, default=10, help="Checkpoints to keep")

    args = parser.parse_args()

    if args.action == "create":
        if not args.target:
            print("Error: --target required for create")
        else:
            create(args.target, args.label)
    elif args.action == "restore":
        if not args.name or not args.target:
            print("Error: --name and --target required for restore")
        else:
            restore(args.name, args.target)
    elif args.action == "list":
        list_checkpoints()
    elif args.action == "cleanup":
        cleanup(args.keep)
