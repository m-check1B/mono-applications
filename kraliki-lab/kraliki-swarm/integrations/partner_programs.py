#!/usr/bin/env python3
"""
Partner Program Integration Tracker
===================================
Tracks partner program status and notifies Kraliki comm hub (and optional n8n webhook).

Usage:
  python3 integrations/partner_programs.py init
  python3 integrations/partner_programs.py list
  python3 integrations/partner_programs.py update --partner pleo --status applied --next-action "Submit application" --notify
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

KRALIKI_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = KRALIKI_DIR / "data" / "partner-programs.json"
N8N_WEBHOOKS_FILE = KRALIKI_DIR / "integrations" / "n8n_webhooks.json"
COMM_HUB_URL = os.getenv("KRALIKI_COMM_URL", "http://127.0.0.1:8199")
N8N_PARTNER_WEBHOOK = os.getenv("N8N_PARTNER_WEBHOOK")

DEFAULT_PARTNERS: List[Dict[str, Any]] = [
    {
        "id": "pleo",
        "name": "Pleo",
        "program_url": "https://www.pleo.io/partners",
        "status": "not_applied",
        "commission": "20-30% first-year commission + setup fee",
        "owner": "unassigned",
        "next_action": "Prepare application checklist and references",
        "notes": "Expense management platform partner program",
    },
    {
        "id": "make",
        "name": "Make.com",
        "program_url": "https://www.make.com/en/partners",
        "status": "not_applied",
        "commission": "Certified partner fees + monthly management",
        "owner": "unassigned",
        "next_action": "Book certification slot and gather case studies",
        "notes": "Automation platform partner program",
    },
    {
        "id": "deel",
        "name": "Deel",
        "program_url": "https://www.deel.com/partners",
        "status": "not_applied",
        "commission": "10-20% commission + setup fee",
        "owner": "unassigned",
        "next_action": "Draft pitch for HR automation use cases",
        "notes": "Global HR and payroll partner program",
    },
]


def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"updated_at": None, "partners": DEFAULT_PARTNERS}


def save_data(data: Dict[str, Any]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    DATA_FILE.write_text(json.dumps(data, indent=2) + "\n")


def find_partner(data: Dict[str, Any], partner_id: str) -> Optional[Dict[str, Any]]:
    for partner in data.get("partners", []):
        if partner.get("id") == partner_id:
            return partner
    return None


def send_comm_broadcast(message: str) -> bool:
    payload = {"from": "partner-programs", "content": message}
    url = f"{COMM_HUB_URL}/broadcast"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode() == 200
    except Exception:
        return False


def resolve_n8n_webhook() -> Optional[str]:
    if N8N_PARTNER_WEBHOOK:
        return N8N_PARTNER_WEBHOOK
    if not N8N_WEBHOOKS_FILE.exists():
        return None
    try:
        data = json.loads(N8N_WEBHOOKS_FILE.read_text())
    except json.JSONDecodeError:
        return None
    return data.get("partner-program")


def send_n8n_webhook(webhook_url: str, payload: Dict[str, Any]) -> bool:
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.getcode() < 300
    except Exception:
        return False


def cmd_init(_: argparse.Namespace) -> int:
    data = load_data()
    if DATA_FILE.exists():
        print(f"Partner program data already exists: {DATA_FILE}")
        return 0
    save_data(data)
    print(f"Initialized partner program data at {DATA_FILE}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    data = load_data()
    print(f"Updated: {data.get('updated_at')}")
    for partner in data.get("partners", []):
        print(
            f"- {partner['id']} | {partner['status']} | {partner['name']} | "
            f"owner={partner.get('owner')} | next={partner.get('next_action')}"
        )
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    data = load_data()
    partner = find_partner(data, args.partner)
    if not partner:
        print(f"Unknown partner id: {args.partner}", file=sys.stderr)
        return 1

    changes = []
    for field in ("status", "owner", "next_action", "notes"):
        value = getattr(args, field)
        if value:
            partner[field] = value
            changes.append(f"{field}={value}")

    if not changes:
        print("No updates provided. Use --status/--owner/--next-action/--notes.")
        return 1

    save_data(data)
    print(f"Updated {partner['name']}: {', '.join(changes)}")

    if args.notify:
        message = (
            f"Partner update: {partner['name']} "
            f"status={partner.get('status')} "
            f"owner={partner.get('owner')} "
            f"next={partner.get('next_action')}"
        )
        comm_ok = send_comm_broadcast(message)
        webhook_url = resolve_n8n_webhook()
        n8n_ok = True
        if webhook_url:
            n8n_ok = send_n8n_webhook(
                webhook_url,
                {
                    "partner": partner,
                    "updated_at": data.get("updated_at"),
                    "message": message,
                },
            )
        print(f"Notify: comm_hub={'ok' if comm_ok else 'failed'} n8n={'ok' if n8n_ok else 'skipped'}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Partner program integration tracker.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize partner program data file.")
    sub.add_parser("list", help="List partner program statuses.")

    update = sub.add_parser("update", help="Update partner program status.")
    update.add_argument("--partner", required=True, help="Partner id (pleo, make, deel)")
    update.add_argument("--status", help="Status (not_applied, applied, approved, rejected, live)")
    update.add_argument("--owner", help="Owner of the partner program")
    update.add_argument("--next-action", dest="next_action", help="Next action to take")
    update.add_argument("--notes", help="Notes")
    update.add_argument("--notify", action="store_true", help="Notify comm hub and n8n")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "update":
        return cmd_update(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
