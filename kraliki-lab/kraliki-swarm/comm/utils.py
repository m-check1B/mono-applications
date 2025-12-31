#!/usr/bin/env python3
import json
import time
import fcntl
from pathlib import Path
from typing import Callable, Dict, Any

class FileLock:
    """File-based locking for shared resources."""
    def __init__(self, file_path: Path, timeout: float = 30.0):
        self.file_path = file_path
        self.lock_path = self.file_path.with_suffix(self.file_path.suffix + ".lock")
        self.timeout = timeout
        self._lock_file = None

    def __enter__(self):
        start = time.time()
        while True:
            try:
                # Use append mode to avoid truncating another process's lock
                # We don't unlink the lock file to avoid a race condition where
                # a new process opens a new inode while another holds the old one.
                self._lock_file = open(self.lock_path, "a")
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except (IOError, OSError):
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"Could not acquire lock on {self.file_path} within {self.timeout}s")
                time.sleep(0.1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock_file:
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            finally:
                self._lock_file.close()
                self._lock_file = None

def atomic_json_update(file_path: Path, update_func: Callable[[Dict], Dict], default: Any = None) -> Dict:
    """Atomically update a JSON file with locking."""
    if default is None:
        default = {}
        
    with FileLock(file_path):
        # Read
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except:
                data = default
        else:
            data = default

        # Update
        data = update_func(data)

        # Write atomically (to temp file, then rename)
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        temp_path.rename(file_path)

        return data

def load_json_safe(file_path: Path, default: Any = None) -> Dict:
    """Safely read a JSON file, using the lock to ensure we don't read during a write."""
    if default is None:
        default = {}
        
    if not file_path.exists():
        return default
        
    with FileLock(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return default
