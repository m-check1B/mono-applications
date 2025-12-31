#!/usr/bin/env python3
"""
Interactive consumer for Focus by Kraliki planning events.

Usage:
    python scripts/consume_planning_events.py [--routing planning.#]

Creates a temporary queue bound to the `ocelot.planning` exchange and prints
each event envelope as it is published. Handy for local debugging.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from aio_pika import ExchangeType, connect_robust
from dotenv import load_dotenv


def load_rabbitmq_url() -> str:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    return os.environ.get("RABBITMQ_URL", "amqp://127.0.0.1:5672")


async def consume(routing_key: str) -> None:
    url = load_rabbitmq_url()
    print(f"🔌 Connecting to RabbitMQ at {url} (routing key: {routing_key})")
    connection = await connect_robust(url)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "ocelot.planning",
        ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue(exclusive=True, auto_delete=True)
    await queue.bind(exchange, routing_key=routing_key)

    print("👂 Listening for planning events. Press Ctrl+C to stop.\n")
    try:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    payload = json.loads(message.body.decode())
                    print(f"[{message.routing_key}] {json.dumps(payload, indent=2)}\n")
    finally:
        await connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consume planning events in real time.")
    parser.add_argument(
        "--routing",
        default="planning.#",
        help="Routing key binding for the planning exchange (default: planning.#)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(consume(args.routing))
    except KeyboardInterrupt:  # pragma: no cover - operational script
        print("\n👋 Event consumer stopped")
