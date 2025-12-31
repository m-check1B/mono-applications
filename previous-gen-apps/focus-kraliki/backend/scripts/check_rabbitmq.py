#!/usr/bin/env python3
"""
Simple RabbitMQ health check.

Usage:
    python scripts/check_rabbitmq.py

Loads backend/.env (if present), reads RABBITMQ_URL, and attempts to open
and close a connection. Exits non-zero on failure so it can be wired into
pre-deploy CI or release scripts.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from aio_pika import connect_robust
from dotenv import load_dotenv


def load_rabbitmq_url() -> str:
    """Load RABBITMQ_URL from backend/.env or fall back to localhost."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    return os.environ.get("RABBITMQ_URL", "amqp://127.0.0.1:5672")


async def main() -> int:
    url = load_rabbitmq_url()
    try:
        connection = await connect_robust(url, timeout=5)
        await connection.close()
        print(f"✅ RabbitMQ reachable at {url}")
        return 0
    except Exception as exc:  # pragma: no cover - operational script
        print(f"❌ RabbitMQ health check failed for {url}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
