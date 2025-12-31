#!/usr/bin/env python3
"""
Stripe Usage Sync
=================

Sync Magic Box usage costs into Stripe as a metered usage record.
Defaults to dry-run; pass --commit to send.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from usage_tracker import UsageMeteringService


def month_end_timestamp(month: str) -> int:
    year, month_num = map(int, month.split("-"))
    start = datetime(year, month_num, 1, tzinfo=timezone.utc)
    if month_num == 12:
        next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_month = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)
    end = next_month - timedelta(seconds=1)
    return int(end.timestamp())


def stripe_post(api_key: str, endpoint: str, payload: dict) -> dict:
    body = urlencode(payload).encode("utf-8")
    req = Request(f"https://api.stripe.com/v1/{endpoint}", data=body)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Magic Box usage to Stripe")
    parser.add_argument(
        "--month",
        default=datetime.now(timezone.utc).strftime("%Y-%m"),
        help="Billing month in YYYY-MM (default: current month)",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MAGIC_BOX_USAGE_DB", "/opt/magic-box/usage.db"),
        help="Path to usage.db",
    )
    parser.add_argument(
        "--subscription-item",
        default=os.getenv("STRIPE_SUBSCRIPTION_ITEM_ID", ""),
        help="Stripe subscription item ID for the metered price",
    )
    parser.add_argument(
        "--currency",
        default=os.getenv("STRIPE_CURRENCY", "eur"),
        help="Currency for reporting (default: eur)",
    )
    parser.add_argument(
        "--fx-rate",
        type=float,
        default=float(os.getenv("STRIPE_FX_RATE", "1.0")),
        help="FX rate to convert usage cost into target currency",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Send usage record to Stripe (default: dry-run)",
    )

    args = parser.parse_args()

    if not args.subscription_item:
        print("Missing --subscription-item or STRIPE_SUBSCRIPTION_ITEM_ID.", file=sys.stderr)
        return 2

    service = UsageMeteringService(db_path=args.db)
    report = service.generate_billing_report(args.month)
    if not report:
        print("No customer registered in usage database; aborting.", file=sys.stderr)
        return 2

    total_cost = float(report["total_cost"]) * args.fx_rate
    quantity_cents = int(round(total_cost * 100))
    timestamp = month_end_timestamp(args.month)

    payload = {
        "subscription_item": args.subscription_item,
        "quantity": quantity_cents,
        "timestamp": timestamp,
        "action": "set",
    }

    output = {
        "month": args.month,
        "currency": args.currency,
        "total_cost": round(total_cost, 2),
        "quantity_cents": quantity_cents,
        "payload": payload,
    }

    if not args.commit:
        print(json.dumps({"dry_run": True, **output}, indent=2))
        return 0

    api_key = os.getenv("STRIPE_API_KEY", "")
    if not api_key:
        print("Missing STRIPE_API_KEY for --commit.", file=sys.stderr)
        return 2

    response = stripe_post(api_key, "usage_records", payload)
    print(json.dumps({"dry_run": False, **output, "stripe_response": response}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
