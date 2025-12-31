"""Integration smoke tests for companies and call disposition APIs.

These tests run without a real PostgreSQL instance by triggering the
in-memory fallbacks defined in the API modules.
"""

from __future__ import annotations

import importlib
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from psycopg2 import OperationalError

import app.api.companies as companies
import app.api.call_dispositions as dispositions
import app.main as main


def _force_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch psycopg2.connect to raise so modules fall back to in-memory storage."""

    def fail_connect(*_: object, **__: object):  # pragma: no cover - helper used in tests
        raise OperationalError("forced test failure")

    monkeypatch.setattr(companies.psycopg2, "connect", fail_connect)
    monkeypatch.setattr(dispositions.psycopg2, "connect", fail_connect)

    importlib.reload(companies)
    importlib.reload(dispositions)
    importlib.reload(main)

    # Ensure clean state for every test
    companies._IN_MEMORY_COMPANIES.clear()  # type: ignore[attr-defined]
    companies._IN_MEMORY_COUNTER = 1  # type: ignore[attr-defined]
    companies._DB_AVAILABLE = False  # type: ignore[attr-defined]

    dispositions._IN_MEMORY_DISPOSITIONS.clear()  # type: ignore[attr-defined]
    dispositions._IN_MEMORY_COUNTER = 1  # type: ignore[attr-defined]
    dispositions._DB_AVAILABLE = False  # type: ignore[attr-defined]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """FastAPI test client with in-memory data stores."""

    _force_in_memory(monkeypatch)
    app = main.create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_create_and_list_companies(client: TestClient) -> None:
    payload = {
        "name": "Acme Corp",
        "domain": "acme.example",
        "industry": "Sales",
        "size": "medium",
        "settings": {"call_recording": True},
    }

    create_resp = client.post("/api/companies", json=payload)
    assert create_resp.status_code == 200
    company = create_resp.json()
    assert company["name"] == "Acme Corp"
    assert company["domain"] == "acme.example"
    assert company["settings"]["call_recording"] is True

    list_resp = client.get("/api/companies")
    assert list_resp.status_code == 200
    companies_payload = list_resp.json()
    assert len(companies_payload) == 1
    assert companies_payload[0]["name"] == "Acme Corp"


def test_create_and_fetch_disposition(client: TestClient) -> None:
    disposition_payload = {
        "call_id": "call_test123",
        "disposition_type": "sale",
        "agent_id": 42,
        "company_id": 1,
        "notes": "Closed the deal",
        "sale_amount": 199.99,
        "sale_currency": "USD",
    }

    create_resp = client.post("/api/call-dispositions", json=disposition_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["call_id"] == "call_test123"
    assert created["disposition_type"] == "sale"
    assert created["sale_amount"] == 199.99

    list_resp = client.get("/api/call-dispositions")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["call_id"] == "call_test123"

