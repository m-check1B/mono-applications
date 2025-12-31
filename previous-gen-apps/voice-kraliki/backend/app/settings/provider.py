"""Provider settings management endpoints."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import psycopg2
from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field, field_validator

from app.providers.registry import ProviderType, TelephonyType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings/provider", tags=["provider-settings"])


_DEFAULT_TELEPHONY_FROM = (
    os.getenv("TELNYX_FROM_NUMBER")
    or os.getenv("TELNYX_PHONE_NUMBER")
    or os.getenv("TWILIO_PHONE_NUMBER_CZ")
    or os.getenv("TWILIO_PHONE_NUMBER_US")
    or os.getenv("TWILIO_FROM_NUMBER")
    or ""
)

DEFAULT_PROVIDER_SETTINGS: dict[str, Any] = {
    "default_provider": ProviderType.OPENAI.value,
    "strategy": "realtime",
    "openai_model": "gpt-4o-mini-realtime-preview-2024-12-17",
    "telephony_provider": TelephonyType.TELNYX.value,
    "telephony_from_number": _DEFAULT_TELEPHONY_FROM,
    "fallback_enabled": False,
    "fallback_order": [
        ProviderType.OPENAI.value,
        ProviderType.GEMINI.value,
        ProviderType.DEEPGRAM.value,
    ],
    "latency_preference": "balanced",
}

ALLOWED_LATENCY = {"low", "balanced", "quality"}
SETTINGS_KEY = "global"


_DB_AVAILABLE: bool | None = None
_IN_MEMORY_STORE: dict[str, Any] = {}


class ProviderSettingsPayload(BaseModel):
    """Payload schema for provider settings."""

    default_provider: ProviderType = Field(
        description="Default AI provider (openai, gemini, deepgram)"
    )
    strategy: str = Field(description="Execution strategy (realtime or segmented)")
    openai_model: str = Field(description="Selected OpenAI realtime model ID")
    telephony_provider: TelephonyType = Field(
        description="Default telephony provider (twilio or telnyx)"
    )
    telephony_from_number: str | None = Field(
        default=None,
        description="Default caller ID used for outbound telephony sessions",
    )
    fallback_enabled: bool = Field(default=False)
    fallback_order: list[ProviderType] = Field(default_factory=list)
    latency_preference: str = Field(default="balanced")

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        if value not in {"realtime", "segmented"}:
            raise ValueError("strategy must be 'realtime' or 'segmented'")
        return value

    @field_validator("latency_preference")
    @classmethod
    def validate_latency(cls, value: str) -> str:
        if value not in ALLOWED_LATENCY:
            raise ValueError("Invalid latency preference")
        return value

    @field_validator("fallback_order")
    @classmethod
    def validate_fallback_order(cls, value: list[ProviderType]) -> list[ProviderType]:
        # Remove duplicates while preserving order
        seen: set[ProviderType] = set()
        ordered: list[ProviderType] = []
        for item in value:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    @field_validator("telephony_from_number")
    @classmethod
    def validate_from_number(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if value and not value.startswith("+"):
            raise ValueError("telephony_from_number must be in E.164 format (e.g., +15551234567)")
        return value or None

    def to_json(self) -> str:
        payload = json.loads(self.model_dump_json())
        return json.dumps(payload)

    @classmethod
    def from_record(cls, record: dict[str, Any] | None) -> ProviderSettingsPayload:
        if not record:
            return cls(**DEFAULT_PROVIDER_SETTINGS)
        stored_value = record.get("value") or {}
        merged = {**DEFAULT_PROVIDER_SETTINGS, **stored_value}
        return cls(**merged)


class SettingsResponse(BaseModel):
    settings: ProviderSettingsPayload
    updated_at: datetime


def get_db_connection():
    """Create a database connection using DATABASE_URL."""

    global _DB_AVAILABLE

    if _DB_AVAILABLE is False:
        raise psycopg2.OperationalError("Database disabled")

    db_url = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/operator_demo"
    )

    # Only attempt PostgreSQL connection if URL is PostgreSQL
    if not db_url.startswith(("postgresql://", "postgres://")):
        logger.info("Provider settings: Non-PostgreSQL DATABASE_URL detected, using in-memory store")
        _DB_AVAILABLE = False
        raise psycopg2.OperationalError("Non-PostgreSQL database URL")

    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except psycopg2.OperationalError as exc:
        _DB_AVAILABLE = False
        raise exc

    _DB_AVAILABLE = True
    return conn


def ensure_table_exists() -> None:
    """Ensure the provider settings table exists."""

    try:
        conn = get_db_connection()
    except psycopg2.OperationalError:
        logger.warning("Provider settings using in-memory store; database unavailable")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_settings (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    except Exception as exc:  # pragma: no cover - logged error
        conn.rollback()
        logger.error("Failed to ensure provider_settings table: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


def fetch_settings() -> tuple[ProviderSettingsPayload, datetime]:
    """Fetch stored provider settings, falling back to defaults."""

    ensure_table_exists()
    if _DB_AVAILABLE is False:
        stored = _IN_MEMORY_STORE.get(SETTINGS_KEY)
        payload = ProviderSettingsPayload.from_record(stored)
        updated_at = stored["updated_at"] if stored and stored.get("updated_at") else datetime.now(UTC)
        return payload, updated_at

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT value, updated_at FROM provider_settings WHERE key = %s",
            (SETTINGS_KEY,),
        )
        record = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    payload = ProviderSettingsPayload.from_record(record)
    updated_at = record["updated_at"] if record and record.get("updated_at") else datetime.now(UTC)
    return payload, updated_at


def upsert_settings(payload: ProviderSettingsPayload) -> datetime:
    """Persist provider settings and return updated timestamp."""

    ensure_table_exists()
    if _DB_AVAILABLE is False:
        now = datetime.now(UTC)
        _IN_MEMORY_STORE[SETTINGS_KEY] = {
            "value": json.loads(payload.model_dump_json()),
            "updated_at": now,
        }
        return now

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO provider_settings (key, value, updated_at)
            VALUES (%s, %s::jsonb, CURRENT_TIMESTAMP)
            ON CONFLICT (key)
            DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            RETURNING updated_at
            """,
            (SETTINGS_KEY, payload.to_json()),
        )
        updated_at_record = cursor.fetchone()
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("Failed to persist provider settings: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to persist settings") from exc
    finally:
        cursor.close()
        conn.close()

    return updated_at_record["updated_at"] if updated_at_record else datetime.now(UTC)


@router.get("", response_model=SettingsResponse)
async def get_provider_settings() -> SettingsResponse:
    """Retrieve provider settings."""

    payload, updated_at = fetch_settings()
    return SettingsResponse(settings=payload, updated_at=updated_at)


@router.put("", response_model=SettingsResponse)
async def update_provider_settings(
    payload: ProviderSettingsPayload,
) -> SettingsResponse:
    """Update provider settings."""

    updated_at = upsert_settings(payload)
    return SettingsResponse(settings=payload, updated_at=updated_at)
