"""
API endpoints for call disposition tracking backed by PostgreSQL.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any

import psycopg2
from fastapi import APIRouter, HTTPException, Query, Request
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    CALL_INITIATION_RATE_LIMIT,
    WRITE_OPERATION_RATE_LIMIT,
    limiter,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/call-dispositions", tags=["call-dispositions"])

_DB_AVAILABLE: bool | None = None
_IN_MEMORY_DISPOSITIONS: dict[int, dict[str, Any]] = {}
_IN_MEMORY_COUNTER: int = 1


def get_db_connection():
    """Create a database connection using DATABASE_URL."""
    global _DB_AVAILABLE

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/operator_demo",
    )

    # Only attempt PostgreSQL connection if URL is PostgreSQL
    if not db_url.startswith(("postgresql://", "postgres://")):
        logger.info("Call dispositions API: Non-PostgreSQL DATABASE_URL detected, using in-memory store")
        _DB_AVAILABLE = False
        raise OperationalError("Non-PostgreSQL database URL")

    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except OperationalError as exc:
        logger.warning("Call dispositions API falling back to in-memory store: %s", exc)
        _DB_AVAILABLE = False
        raise

    _DB_AVAILABLE = True
    return conn


def ensure_table_exists() -> None:
    """Ensure the call_dispositions table exists."""

    try:
        conn = get_db_connection()
    except OperationalError:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS call_dispositions (
                id SERIAL PRIMARY KEY,
                call_id TEXT NOT NULL,
                disposition_type TEXT NOT NULL,
                notes TEXT,
                agent_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                script_id INTEGER,
                customer_satisfaction INTEGER,
                follow_up_required BOOLEAN DEFAULT FALSE,
                follow_up_date DATE,
                follow_up_notes TEXT,
                sale_amount NUMERIC,
                sale_currency VARCHAR(3) DEFAULT 'USD',
                tags JSONB DEFAULT '[]'::jsonb,
                custom_fields JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS call_dispositions_company_idx
            ON call_dispositions (company_id);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS call_dispositions_call_idx
            ON call_dispositions (call_id);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS call_dispositions_follow_up_idx
            ON call_dispositions (follow_up_required, follow_up_date);
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


try:
    ensure_table_exists()
except OperationalError:
    _DB_AVAILABLE = False


def _isoformat(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if isinstance(dt, str):
        return dt if dt.endswith("Z") else f"{dt}Z"
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def _serialize_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


class DispositionType(str, Enum):
    SALE = "sale"
    NOT_INTERESTED = "not_interested"
    CALLBACK = "callback"
    WRONG_NUMBER = "wrong_number"
    LEFT_MESSAGE = "left_message"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    DISCONNECTED = "disconnected"
    TRANSFERRED = "transferred"


class CallDisposition(BaseModel):
    id: int
    call_id: str
    disposition_type: DispositionType
    notes: str | None = Field(None, max_length=2000)
    agent_id: int
    company_id: int
    script_id: int | None = None
    customer_satisfaction: int | None = Field(None, ge=1, le=5)
    follow_up_required: bool = Field(default=False)
    follow_up_date: str | None = None
    follow_up_notes: str | None = Field(None, max_length=1000)
    sale_amount: float | None = Field(None, ge=0)
    sale_currency: str | None = Field(default="USD", pattern=r"^[A-Z]{3}$")
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class CallDispositionCreate(BaseModel):
    call_id: str
    disposition_type: DispositionType
    notes: str | None = Field(None, max_length=2000)
    agent_id: int
    company_id: int
    script_id: int | None = None
    customer_satisfaction: int | None = Field(None, ge=1, le=5)
    follow_up_required: bool = Field(default=False)
    follow_up_date: str | None = None
    follow_up_notes: str | None = Field(None, max_length=1000)
    sale_amount: float | None = Field(None, ge=0)
    sale_currency: str | None = Field(default="USD", pattern=r"^[A-Z]{3}$")
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class CallDispositionUpdate(BaseModel):
    disposition_type: DispositionType | None = None
    notes: str | None = Field(None, max_length=2000)
    customer_satisfaction: int | None = Field(None, ge=1, le=5)
    follow_up_required: bool | None = None
    follow_up_date: str | None = None
    follow_up_notes: str | None = Field(None, max_length=1000)
    sale_amount: float | None = Field(None, ge=0)
    sale_currency: str | None = Field(None, pattern=r"^[A-Z]{3}$")
    tags: list[str] | None = None
    custom_fields: dict[str, Any] | None = None


class DispositionStats(BaseModel):
    company_id: int
    total_dispositions: int
    dispositions_by_type: dict[str, int]
    sales_count: int
    total_revenue: float
    average_satisfaction: float | None
    follow_ups_required: int
    conversion_rate: float


def _row_to_disposition(row: dict[str, Any]) -> CallDisposition:
    return CallDisposition(
        id=row["id"],
        call_id=row["call_id"],
        disposition_type=DispositionType(row["disposition_type"]),
        notes=row.get("notes"),
        agent_id=row["agent_id"],
        company_id=row["company_id"],
        script_id=row.get("script_id"),
        customer_satisfaction=row.get("customer_satisfaction"),
        follow_up_required=row.get("follow_up_required", False),
        follow_up_date=_serialize_date(row.get("follow_up_date")),
        follow_up_notes=row.get("follow_up_notes"),
        sale_amount=float(row["sale_amount"]) if row.get("sale_amount") is not None else None,
        sale_currency=row.get("sale_currency") or "USD",
        tags=row.get("tags") or [],
        custom_fields=row.get("custom_fields") or {},
        created_at=_isoformat(row.get("created_at")) or "",
        updated_at=_isoformat(row.get("updated_at")) or "",
    )


def _memory_create_disposition(data: dict[str, Any]) -> CallDisposition:
    global _IN_MEMORY_COUNTER

    disposition_id = _IN_MEMORY_COUNTER
    _IN_MEMORY_COUNTER += 1

    now = datetime.now(UTC).isoformat() + "Z"
    record = {
        "id": disposition_id,
        "created_at": now,
        "updated_at": now,
        **data,
    }
    _IN_MEMORY_DISPOSITIONS[disposition_id] = record
    return _row_to_disposition(record)


def _memory_get_disposition(disposition_id: int) -> CallDisposition:
    record = _IN_MEMORY_DISPOSITIONS.get(disposition_id)
    if not record:
        raise HTTPException(status_code=404, detail="Disposition not found")
    return _row_to_disposition(record)


def _memory_list_dispositions(filters: dict[str, Any], limit: int, offset: int) -> list[CallDisposition]:
    records = list(_IN_MEMORY_DISPOSITIONS.values())

    def matches(record: dict[str, Any]) -> bool:
        if filters.get("company_id") is not None and record.get("company_id") != filters["company_id"]:
            return False
        if filters.get("agent_id") is not None and record.get("agent_id") != filters["agent_id"]:
            return False
        if filters.get("disposition_type") and record.get("disposition_type") != filters["disposition_type"].value:
            return False
        if filters.get("call_id") and record.get("call_id") != filters["call_id"]:
            return False
        # ignore date filters for simplicity in memory mode
        return True

    filtered = [rec for rec in records if matches(rec)]
    sliced = filtered[offset : offset + limit]
    return [_row_to_disposition(rec) for rec in sliced]


def _memory_update_disposition(disposition_id: int, data: dict[str, Any]) -> CallDisposition:
    record = _IN_MEMORY_DISPOSITIONS.get(disposition_id)
    if not record:
        raise HTTPException(status_code=404, detail="Disposition not found")

    record.update(data)
    record["updated_at"] = datetime.now(UTC).isoformat() + "Z"
    _IN_MEMORY_DISPOSITIONS[disposition_id] = record
    return _row_to_disposition(record)


def _memory_delete_disposition(disposition_id: int) -> None:
    if disposition_id not in _IN_MEMORY_DISPOSITIONS:
        raise HTTPException(status_code=404, detail="Disposition not found")
    del _IN_MEMORY_DISPOSITIONS[disposition_id]

def _build_filters(
    company_id: int | None,
    agent_id: int | None,
    disposition_type: DispositionType | None,
    call_id: str | None,
    date_from: str | None,
    date_to: str | None,
) -> tuple[str, list[Any]]:
    clauses = []
    params: list[Any] = []

    if company_id is not None:
        clauses.append("company_id = %s")
        params.append(company_id)
    if agent_id is not None:
        clauses.append("agent_id = %s")
        params.append(agent_id)
    if disposition_type is not None:
        clauses.append("disposition_type = %s")
        params.append(disposition_type.value)
    if call_id is not None:
        clauses.append("call_id = %s")
        params.append(call_id)
    if date_from:
        clauses.append("created_at >= %s")
        params.append(date_from)
    if date_to:
        clauses.append("created_at <= %s")
        params.append(date_to)

    where_clause = ""
    if clauses:
        where_clause = "WHERE " + " AND ".join(clauses)

    return where_clause, params


@router.get("/", response_model=list[CallDisposition])
async def get_dispositions(
    company_id: int | None = Query(None),
    agent_id: int | None = Query(None),
    disposition_type: DispositionType | None = Query(None),
    call_id: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get call dispositions with filtering."""

    filters = {
        "company_id": company_id,
        "agent_id": agent_id,
        "disposition_type": disposition_type,
        "call_id": call_id,
        "date_from": date_from,
        "date_to": date_to,
    }

    if _DB_AVAILABLE is False:
        return _memory_list_dispositions(filters, limit, offset)

    where_clause, params = _build_filters(
        company_id, agent_id, disposition_type, call_id, date_from, date_to
    )
    params.extend([limit, offset])

    query = f"""
        SELECT *
        FROM call_dispositions
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_disposition(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.get("/{disposition_id}", response_model=CallDisposition)
async def get_disposition(request: Request, disposition_id: int):
    """Get a specific call disposition."""

    if _DB_AVAILABLE is False:
        return _memory_get_disposition(disposition_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM call_dispositions WHERE id = %s", (disposition_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Disposition not found")
        return _row_to_disposition(row)
    finally:
        cursor.close()
        conn.close()


@limiter.limit(CALL_INITIATION_RATE_LIMIT)
@router.post("/", response_model=CallDisposition)
async def create_disposition(request: Request, disposition_data: CallDispositionCreate):
    """Create a new call disposition."""

    if _DB_AVAILABLE is False:
        payload = disposition_data.model_dump()
        return _memory_create_disposition(payload)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO call_dispositions (
                call_id,
                disposition_type,
                notes,
                agent_id,
                company_id,
                script_id,
                customer_satisfaction,
                follow_up_required,
                follow_up_date,
                follow_up_notes,
                sale_amount,
                sale_currency,
                tags,
                custom_fields
            )
            VALUES (
                %(call_id)s,
                %(disposition_type)s,
                %(notes)s,
                %(agent_id)s,
                %(company_id)s,
                %(script_id)s,
                %(customer_satisfaction)s,
                %(follow_up_required)s,
                %(follow_up_date)s,
                %(follow_up_notes)s,
                %(sale_amount)s,
                %(sale_currency)s,
                %(tags)s,
                %(custom_fields)s
            )
            RETURNING *
            """,
            {
                **disposition_data.model_dump(exclude={"tags", "custom_fields"}),
                "follow_up_date": disposition_data.follow_up_date,
                "tags": json.dumps(disposition_data.tags),
                "custom_fields": json.dumps(disposition_data.custom_fields),
            },
        )
        row = cursor.fetchone()
        conn.commit()
        return _row_to_disposition(row)
    except psycopg2.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.put("/{disposition_id}", response_model=CallDisposition)
async def update_disposition(
    request: Request, disposition_id: int, disposition_data: CallDispositionUpdate
):
    """Update a call disposition."""

    updates = []
    params: dict[str, Any] = {"disposition_id": disposition_id}
    data = disposition_data.model_dump(exclude_unset=True)

    if _DB_AVAILABLE is False:
        payload: dict[str, Any] = {}
        for field, value in data.items():
            if field in {"tags", "custom_fields"} and value is not None:
                payload[field] = value
            elif field == "disposition_type" and value is not None:
                payload[field] = value.value
            else:
                payload[field] = value
        return _memory_update_disposition(disposition_id, payload)

    for field, value in data.items():
        if field in {"tags", "custom_fields"} and value is not None:
            updates.append(f"{field} = %({field})s")
            params[field] = json.dumps(value)
        elif field == "follow_up_date":
            updates.append("follow_up_date = %(follow_up_date)s")
            params["follow_up_date"] = value
        elif field == "disposition_type" and value is not None:
            updates.append("disposition_type = %(disposition_type)s")
            params["disposition_type"] = value.value
        elif value is not None:
            updates.append(f"{field} = %({field})s")
            params[field] = value

    if not updates:
        return await get_disposition(request, disposition_id)

    updates.append("updated_at = CURRENT_TIMESTAMP")
    set_clause = ", ".join(updates)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            UPDATE call_dispositions
            SET {set_clause}
            WHERE id = %(disposition_id)s
            RETURNING *
            """,
            params,
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Disposition not found")
        conn.commit()
        return _row_to_disposition(row)
    except psycopg2.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.delete("/{disposition_id}")
async def delete_disposition(request: Request, disposition_id: int):
    """Delete a call disposition."""

    if _DB_AVAILABLE is False:
        _memory_delete_disposition(disposition_id)
        return {"message": "Disposition deleted successfully"}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM call_dispositions WHERE id = %s RETURNING id",
            (disposition_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Disposition not found")
        conn.commit()
        return {"message": "Disposition deleted successfully"}
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.get("/types", response_model=list[dict[str, Any]])
async def get_disposition_types(request: Request):
    """Get available disposition types."""

    types = [
        {
            "value": DispositionType.SALE.value,
            "label": "Sale",
            "description": "Successful sale or conversion",
            "color": "green",
            "revenue_impact": "positive",
        },
        {
            "value": DispositionType.NOT_INTERESTED.value,
            "label": "Not Interested",
            "description": "Customer not interested in product/service",
            "color": "red",
            "revenue_impact": "none",
        },
        {
            "value": DispositionType.CALLBACK.value,
            "label": "Callback",
            "description": "Customer requested callback",
            "color": "yellow",
            "revenue_impact": "potential",
        },
        {
            "value": DispositionType.WRONG_NUMBER.value,
            "label": "Wrong Number",
            "description": "Called wrong number",
            "color": "gray",
            "revenue_impact": "none",
        },
        {
            "value": DispositionType.LEFT_MESSAGE.value,
            "label": "Left Message",
            "description": "Left voicemail or message",
            "color": "blue",
            "revenue_impact": "potential",
        },
        {
            "value": DispositionType.NO_ANSWER.value,
            "label": "No Answer",
            "description": "Call not answered",
            "color": "gray",
            "revenue_impact": "none",
        },
        {
            "value": DispositionType.BUSY.value,
            "label": "Busy",
            "description": "Line was busy",
            "color": "orange",
            "revenue_impact": "none",
        },
        {
            "value": DispositionType.DISCONNECTED.value,
            "label": "Disconnected",
            "description": "Call was disconnected",
            "color": "red",
            "revenue_impact": "none",
        },
        {
            "value": DispositionType.TRANSFERRED.value,
            "label": "Transferred",
            "description": "Call transferred to another agent/department",
            "color": "purple",
            "revenue_impact": "potential",
        },
    ]

    return types


@limiter.limit(API_RATE_LIMIT)
@router.get("/stats/{company_id}", response_model=DispositionStats)
async def get_disposition_stats(request: Request, company_id: int):
    """Get disposition statistics for a company."""

    if _DB_AVAILABLE is False:
        records = [
            record
            for record in _IN_MEMORY_DISPOSITIONS.values()
            if record.get("company_id") == company_id
        ]
        total_dispositions = len(records)
        dispositions_by_type: dict[str, int] = {}
        sales_count = 0
        total_revenue = 0.0
        satisfaction_scores: list[int] = []
        follow_ups_required = 0

        for record in records:
            dtype = record.get("disposition_type", "")
            dispositions_by_type[dtype] = dispositions_by_type.get(dtype, 0) + 1

            if dtype == DispositionType.SALE.value:
                sales_count += 1
                total_revenue += float(record.get("sale_amount") or 0)

            if record.get("customer_satisfaction"):
                satisfaction_scores.append(record["customer_satisfaction"])

            if record.get("follow_up_required"):
                follow_ups_required += 1

        average_satisfaction = (
            sum(satisfaction_scores) / len(satisfaction_scores)
            if satisfaction_scores
            else None
        )
        conversion_rate = (
            (sales_count / total_dispositions) * 100 if total_dispositions else 0.0
        )

        return DispositionStats(
            company_id=company_id,
            total_dispositions=total_dispositions,
            dispositions_by_type=dispositions_by_type,
            sales_count=sales_count,
            total_revenue=total_revenue,
            average_satisfaction=average_satisfaction,
            follow_ups_required=follow_ups_required,
            conversion_rate=conversion_rate,
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_dispositions,
                SUM(CASE WHEN disposition_type = %s THEN 1 ELSE 0 END) AS sales_count,
                SUM(COALESCE(sale_amount, 0)) AS total_revenue,
                AVG(customer_satisfaction) AS average_satisfaction,
                SUM(CASE WHEN follow_up_required THEN 1 ELSE 0 END) AS follow_ups_required
            FROM call_dispositions
            WHERE company_id = %s
            """,
            (DispositionType.SALE.value, company_id),
        )
        aggregate = cursor.fetchone() or {}

        cursor.execute(
            """
            SELECT disposition_type, COUNT(*) AS count
            FROM call_dispositions
            WHERE company_id = %s
            GROUP BY disposition_type
            """,
            (company_id,),
        )
        by_type_rows = cursor.fetchall()
        dispositions_by_type = {
            row["disposition_type"]: row["count"] for row in by_type_rows
        }

        total_dispositions = aggregate.get("total_dispositions") or 0
        sales_count = aggregate.get("sales_count") or 0
        total_revenue = float(aggregate.get("total_revenue") or 0.0)
        average_satisfaction = aggregate.get("average_satisfaction")
        follow_ups_required = aggregate.get("follow_ups_required") or 0
        conversion_rate = (
            (sales_count / total_dispositions) * 100 if total_dispositions else 0.0
        )

        return DispositionStats(
            company_id=company_id,
            total_dispositions=total_dispositions,
            dispositions_by_type=dispositions_by_type,
            sales_count=sales_count,
            total_revenue=total_revenue,
            average_satisfaction=average_satisfaction,
            follow_ups_required=follow_ups_required,
            conversion_rate=conversion_rate,
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/follow-ups/{company_id}")
async def get_follow_ups(
    company_id: int,
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get follow-ups required for a company."""

    if _DB_AVAILABLE is False:
        follow_ups = [
            _row_to_disposition(record)
            for record in _IN_MEMORY_DISPOSITIONS.values()
            if record.get("company_id") == company_id
            and record.get("follow_up_required")
        ]
        follow_ups.sort(
            key=lambda d: (
                d.follow_up_date or "9999-12-31",
                d.created_at,
            )
        )
        return {
            "company_id": company_id,
            "follow_ups": follow_ups[offset : offset + limit],
            "total": len(follow_ups),
        }

    clauses = ["company_id = %s", "follow_up_required = TRUE"]
    params: list[Any] = [company_id]
    if date_from:
        clauses.append("follow_up_date >= %s")
        params.append(date_from)
    if date_to:
        clauses.append("follow_up_date <= %s")
        params.append(date_to)

    where_clause = " AND ".join(clauses)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT *
            FROM call_dispositions
            WHERE {where_clause}
            ORDER BY follow_up_date ASC NULLS LAST, created_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        rows = cursor.fetchall()

        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM call_dispositions
            WHERE {where_clause}
            """,
            params,
        )
        total_row = cursor.fetchone() or {"total": 0}

        return {
            "company_id": company_id,
            "follow_ups": [_row_to_disposition(row) for row in rows],
            "total": total_row["total"],
        }
    finally:
        cursor.close()
        conn.close()


@router.get("/revenue/{company_id}")
async def get_revenue_stats(
    company_id: int,
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    """Get revenue statistics for a company."""

    if _DB_AVAILABLE is False:
        records = [
            record
            for record in _IN_MEMORY_DISPOSITIONS.values()
            if record.get("company_id") == company_id
            and record.get("disposition_type") == DispositionType.SALE.value
        ]

        total_revenue = sum(float(record.get("sale_amount") or 0) for record in records)
        sales_count = len(records)
        average_sale = total_revenue / sales_count if sales_count else 0.0
        revenue_by_currency: dict[str, float] = {}
        for record in records:
            currency = record.get("sale_currency") or "USD"
            revenue_by_currency[currency] = revenue_by_currency.get(currency, 0.0) + float(record.get("sale_amount") or 0)

        total_dispositions = sum(
            1 for record in _IN_MEMORY_DISPOSITIONS.values() if record.get("company_id") == company_id
        )
        conversion_rate = (sales_count / total_dispositions * 100) if total_dispositions else 0.0

        return {
            "company_id": company_id,
            "total_revenue": total_revenue,
            "sales_count": sales_count,
            "average_sale": average_sale,
            "revenue_by_currency": revenue_by_currency,
            "conversion_rate": conversion_rate,
        }

    clauses = ["company_id = %s", "disposition_type = %s"]
    params: list[Any] = [company_id, DispositionType.SALE.value]
    if date_from:
        clauses.append("created_at >= %s")
        params.append(date_from)
    if date_to:
        clauses.append("created_at <= %s")
        params.append(date_to)

    where_clause = " AND ".join(clauses)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS sales_count,
                SUM(COALESCE(sale_amount, 0)) AS total_revenue,
                AVG(sale_amount) AS average_sale
            FROM call_dispositions
            WHERE {where_clause}
            """,
            params,
        )
        row = cursor.fetchone() or {}

        cursor.execute(
            f"""
            SELECT sale_currency, SUM(COALESCE(sale_amount, 0)) AS revenue
            FROM call_dispositions
            WHERE {where_clause}
            GROUP BY sale_currency
            """,
            params,
        )
        currency_rows = cursor.fetchall()
        revenue_by_currency = {
            r["sale_currency"] or "USD": float(r["revenue"] or 0.0)
            for r in currency_rows
        }

        cursor.execute(
            """
            SELECT COUNT(*) AS total_dispositions
            FROM call_dispositions
            WHERE company_id = %s
            """,
            (company_id,),
        )
        total_dispositions = cursor.fetchone().get("total_dispositions") or 0

        sales_count = row.get("sales_count") or 0
        total_revenue = float(row.get("total_revenue") or 0.0)
        average_sale = float(row.get("average_sale") or 0.0)
        conversion_rate = (
            (sales_count / total_dispositions) * 100 if total_dispositions else 0.0
        )

        return {
            "company_id": company_id,
            "total_revenue": total_revenue,
            "sales_count": sales_count,
            "average_sale": average_sale,
            "revenue_by_currency": revenue_by_currency,
            "conversion_rate": conversion_rate,
        }
    finally:
        cursor.close()
        conn.close()
