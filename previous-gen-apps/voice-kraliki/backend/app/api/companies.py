"""
API endpoints for company management backed by PostgreSQL.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import psycopg2
from fastapi import APIRouter, HTTPException, Query, Request
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, Field

from app.middleware.rate_limit import (
    API_RATE_LIMIT,
    WRITE_OPERATION_RATE_LIMIT,
    limiter,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/companies", tags=["companies"])

_DB_AVAILABLE: bool | None = None
_IN_MEMORY_COMPANIES: dict[int, dict[str, Any]] = {}
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
        logger.info("Companies API: Non-PostgreSQL DATABASE_URL detected, using in-memory store")
        _DB_AVAILABLE = False
        raise OperationalError("Non-PostgreSQL database URL")

    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except OperationalError as exc:
        logger.warning("Companies API falling back to in-memory store: %s", exc)
        _DB_AVAILABLE = False
        raise

    _DB_AVAILABLE = True
    return conn


def ensure_table_exists() -> None:
    """Ensure the companies table exists."""

    try:
        conn = get_db_connection()
    except OperationalError:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                domain VARCHAR(255) NOT NULL,
                description TEXT,
                industry VARCHAR(100),
                size VARCHAR(50),
                phone_number VARCHAR(32),
                email VARCHAR(255),
                address VARCHAR(500),
                city VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100),
                postal_code VARCHAR(20),
                website TEXT,
                logo_url TEXT,
                settings JSONB DEFAULT '{}'::jsonb,
                is_active BOOLEAN DEFAULT TRUE,
                user_count INTEGER DEFAULT 0,
                call_count INTEGER DEFAULT 0,
                script_count INTEGER DEFAULT 0,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS companies_active_idx ON companies (is_active);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS companies_industry_idx ON companies (industry);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS companies_size_idx ON companies (size);
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
    # Ensure naive UTC iso string
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def _memory_create_company(data: dict[str, Any]) -> Company:
    global _IN_MEMORY_COUNTER

    company_id = _IN_MEMORY_COUNTER
    _IN_MEMORY_COUNTER += 1

    now = datetime.now(UTC).isoformat() + "Z"
    record = {
        "id": company_id,
        "created_at": now,
        "updated_at": now,
        "user_count": 0,
        "call_count": 0,
        "script_count": 0,
        **data,
    }
    _IN_MEMORY_COMPANIES[company_id] = record
    return _row_to_company(record)


def _memory_get_company(company_id: int) -> Company:
    record = _IN_MEMORY_COMPANIES.get(company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Company not found")
    return _row_to_company(record)


def _memory_list_companies(filters: dict[str, Any], limit: int, offset: int) -> list[Company]:
    records = list(_IN_MEMORY_COMPANIES.values())

    def matches(record: dict[str, Any]) -> bool:
        if filters.get("is_active") is not None and record.get("is_active", True) != filters["is_active"]:
            return False
        if filters.get("industry") and (record.get("industry") or "").lower() != filters["industry"].lower():
            return False
        if filters.get("size") and (record.get("size") or "").lower() != filters["size"].lower():
            return False
        if search := filters.get("search"):
            search_lower = search.lower()
            description = record.get("description") or ""
            if not (
                search_lower in record.get("name", "").lower()
                or search_lower in record.get("domain", "").lower()
                or search_lower in description.lower()
            ):
                return False
        return True

    filtered = [record for record in records if matches(record)]
    sliced = filtered[offset : offset + limit]
    return [_row_to_company(record) for record in sliced]


def _memory_update_company(company_id: int, data: dict[str, Any]) -> Company:
    record = _IN_MEMORY_COMPANIES.get(company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Company not found")

    record.update(data)
    record["updated_at"] = datetime.now(UTC).isoformat() + "Z"
    _IN_MEMORY_COMPANIES[company_id] = record
    return _row_to_company(record)


def _memory_delete_company(company_id: int) -> None:
    if company_id not in _IN_MEMORY_COMPANIES:
        raise HTTPException(status_code=404, detail="Company not found")
    del _IN_MEMORY_COMPANIES[company_id]


def _row_to_company(row: dict[str, Any]) -> Company:
    return Company(
        id=row["id"],
        name=row["name"],
        domain=row["domain"],
        description=row.get("description"),
        industry=row.get("industry"),
        size=row.get("size"),
        phone_number=row.get("phone_number"),
        email=row.get("email"),
        address=row.get("address"),
        city=row.get("city"),
        state=row.get("state"),
        country=row.get("country"),
        postal_code=row.get("postal_code"),
        website=row.get("website"),
        logo_url=row.get("logo_url"),
        settings=row.get("settings") or {},
        is_active=row.get("is_active", True),
        created_at=_isoformat(row.get("created_at")) or "",
        updated_at=_isoformat(row.get("updated_at")) or "",
        user_count=row.get("user_count") or 0,
        call_count=row.get("call_count") or 0,
        script_count=row.get("script_count") or 0,
    )


class Company(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    industry: str | None = Field(None, max_length=100)
    size: str | None = Field(None, pattern="^(small|medium|large|enterprise)$")
    phone_number: str | None = Field(None, pattern=r"^\+?[1-9][\d\-\s\(\)]{1,20}$")
    email: str | None = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    website: str | None = Field(None, pattern=r"^https?://.+")
    logo_url: str | None = Field(None, pattern=r"^https?://.+")
    settings: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)
    created_at: str
    updated_at: str
    user_count: int | None = Field(None, ge=0)
    call_count: int | None = Field(None, ge=0)
    script_count: int | None = Field(None, ge=0)


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    industry: str | None = Field(None, max_length=100)
    size: str | None = Field(
        None, pattern="^(small|medium|large|enterprise)$"
    )
    phone_number: str | None = Field(
        None, pattern=r"^\+?[1-9][\d\-\s\(\)]{1,20}$"
    )
    email: str | None = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    website: str | None = Field(None, pattern=r"^https?://.+")
    logo_url: str | None = Field(None, pattern=r"^https?://.+")
    settings: dict[str, Any] = Field(default_factory=dict)


class CompanyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    domain: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    industry: str | None = Field(None, max_length=100)
    size: str | None = Field(
        None, pattern="^(small|medium|large|enterprise)$"
    )
    phone_number: str | None = Field(
        None, pattern=r"^\+?[1-9][\d\-\s\(\)]{1,20}$"
    )
    email: str | None = Field(
        None,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    )
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    website: str | None = Field(None, pattern=r"^https?://.+")
    logo_url: str | None = Field(None, pattern=r"^https?://.+")
    settings: dict[str, Any] | None = None
    is_active: bool | None = None


class CompanyStats(BaseModel):
    company_id: int
    total_users: int
    active_users: int
    total_calls: int
    calls_this_month: int
    total_scripts: int
    active_scripts: int
    average_call_duration: float
    success_rate: float
    cost_this_month: float


def _build_filters(
    is_active: bool | None,
    industry: str | None,
    size: str | None,
    search: str | None,
) -> tuple[str, list[Any]]:
    clauses = []
    params: list[Any] = []

    if is_active is not None:
        clauses.append("is_active = %s")
        params.append(is_active)
    if industry:
        clauses.append("LOWER(industry) = LOWER(%s)")
        params.append(industry)
    if size:
        clauses.append("LOWER(size) = LOWER(%s)")
        params.append(size)
    if search:
        clauses.append(
            "(LOWER(name) LIKE %s OR LOWER(domain) LIKE %s OR LOWER(COALESCE(description, '')) LIKE %s)"
        )
        like_term = f"%{search.lower()}%"
        params.extend([like_term, like_term, like_term])

    where_clause = ""
    if clauses:
        where_clause = "WHERE " + " AND ".join(clauses)

    return where_clause, params


@router.get("/", response_model=list[Company])
async def get_companies(
    is_active: bool | None = Query(None),
    industry: str | None = Query(None),
    size: str | None = Query(None),
    search: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get companies with filtering."""

    filters = {
        "is_active": is_active,
        "industry": industry,
        "size": size,
        "search": search,
    }

    if _DB_AVAILABLE is False:
        return _memory_list_companies(filters, limit, offset)

    where_clause, params = _build_filters(is_active, industry, size, search)
    query = f"""
        SELECT *
        FROM companies
        {where_clause}
        ORDER BY id
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_company(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.get("/industries")
async def get_industries(request: Request):
    """Get list of available industries."""

    industries = [
        "Insurance",
        "Sales",
        "Healthcare",
        "Finance",
        "Education",
        "Retail",
        "Technology",
        "Real Estate",
        "Manufacturing",
        "Consulting",
        "Legal",
        "Other",
    ]

    return {"industries": industries}


@limiter.limit(API_RATE_LIMIT)
@router.get("/sizes")
async def get_company_sizes(request: Request):
    """Get list of company sizes."""

    sizes = [
        {"value": "small", "label": "Small (1-50 employees)"},
        {"value": "medium", "label": "Medium (51-500 employees)"},
        {"value": "large", "label": "Large (501-5000 employees)"},
        {"value": "enterprise", "label": "Enterprise (5000+ employees)"},
    ]

    return {"sizes": sizes}


@limiter.limit(API_RATE_LIMIT)
@router.get("/{company_id}", response_model=Company)
async def get_company(request: Request, company_id: int):
    """Get a specific company."""

    if _DB_AVAILABLE is False:
        return _memory_get_company(company_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")
        return _row_to_company(row)
    finally:
        cursor.close()
        conn.close()


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.post("/", response_model=Company)
async def create_company(request: Request, company_data: CompanyCreate):
    """Create a new company."""

    if _DB_AVAILABLE is False:
        return _memory_create_company(company_data.model_dump())

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO companies (
                name,
                domain,
                description,
                industry,
                size,
                phone_number,
                email,
                address,
                city,
                state,
                country,
                postal_code,
                website,
                logo_url,
                settings
            )
            VALUES (
                %(name)s,
                %(domain)s,
                %(description)s,
                %(industry)s,
                %(size)s,
                %(phone_number)s,
                %(email)s,
                %(address)s,
                %(city)s,
                %(state)s,
                %(country)s,
                %(postal_code)s,
                %(website)s,
                %(logo_url)s,
                %(settings)s
            )
            RETURNING *
            """,
            {
                **company_data.model_dump(exclude={"settings"}),
                "settings": json.dumps(company_data.settings),
            },
        )
        row = cursor.fetchone()
        conn.commit()
        return _row_to_company(row)
    except psycopg2.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.put("/{company_id}", response_model=Company)
async def update_company(request: Request, company_id: int, company_data: CompanyUpdate):
    """Update a company."""

    updates = []
    params: dict[str, Any] = {"company_id": company_id}
    data = company_data.model_dump(exclude_unset=True)

    if _DB_AVAILABLE is False:
        payload: dict[str, Any] = {}
        for field, value in data.items():
            if field == "settings" and value is not None:
                payload["settings"] = value
            elif value is not None:
                payload[field] = value
        return _memory_update_company(company_id, payload)

    for field, value in data.items():
        if field == "settings" and value is not None:
            updates.append("settings = %(settings)s")
            params["settings"] = json.dumps(value)
        else:
            updates.append(f"{field} = %({field})s")
            params[field] = value

    if not updates:
        return await get_company(request, company_id)

    updates.append("updated_at = CURRENT_TIMESTAMP")
    set_clause = ", ".join(updates)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            UPDATE companies
            SET {set_clause}
            WHERE id = %(company_id)s
            RETURNING *
            """,
            params,
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Company not found")
        conn.commit()
        return _row_to_company(row)
    except psycopg2.Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        cursor.close()
        conn.close()


@limiter.limit(WRITE_OPERATION_RATE_LIMIT)
@router.delete("/{company_id}")
async def delete_company(request: Request, company_id: int):
    """Delete a company."""

    if _DB_AVAILABLE is False:
        _memory_delete_company(company_id)
        return {"message": "Company deleted successfully"}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM companies WHERE id = %s RETURNING id", (company_id,))
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Company not found")
        conn.commit()
        return {"message": "Company deleted successfully"}
    finally:
        cursor.close()
        conn.close()


@limiter.limit(API_RATE_LIMIT)
@router.get("/{company_id}/stats", response_model=CompanyStats)
async def get_company_stats(request: Request, company_id: int):
    """Get statistics for a company."""

    if _DB_AVAILABLE is False:
        record = _IN_MEMORY_COMPANIES.get(company_id)
        if not record:
            raise HTTPException(status_code=404, detail="Company not found")

        total_calls = record.get("call_count") or 0
        total_scripts = record.get("script_count") or 0
        total_users = record.get("user_count") or 0

        return CompanyStats(
            company_id=company_id,
            total_users=total_users,
            active_users=int(total_users * 0.8) if total_users else 0,
            total_calls=total_calls,
            calls_this_month=int(total_calls * 0.15) if total_calls else 0,
            total_scripts=total_scripts,
            active_scripts=int(total_scripts * 0.7) if total_scripts else 0,
            average_call_duration=245.5 if total_calls else 0.0,
            success_rate=78.3 if total_calls else 0.0,
            cost_this_month=1247.89 if total_calls else 0.0,
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT user_count, call_count, script_count
            FROM companies
            WHERE id = %s
            """,
            (company_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Company not found")

        total_calls = row.get("call_count") or 0
        total_scripts = row.get("script_count") or 0
        total_users = row.get("user_count") or 0

        return CompanyStats(
            company_id=company_id,
            total_users=total_users,
            active_users=int(total_users * 0.8) if total_users else 0,
            total_calls=total_calls,
            calls_this_month=int(total_calls * 0.15) if total_calls else 0,
            total_scripts=total_scripts,
            active_scripts=int(total_scripts * 0.7) if total_scripts else 0,
            average_call_duration=245.5 if total_calls else 0.0,
            success_rate=78.3 if total_calls else 0.0,
            cost_this_month=1247.89 if total_calls else 0.0,
        )
    finally:
        cursor.close()
        conn.close()


@router.get("/{company_id}/users")
async def get_company_users(
    company_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get users for a company."""

    # Placeholder implementation until user management is persisted.
    mock_users = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@company.com",
            "role": "admin",
            "is_active": True,
            "last_login": "2025-10-11T09:30:00Z",
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane@company.com",
            "role": "agent",
            "is_active": True,
            "last_login": "2025-10-11T08:45:00Z",
        },
    ]

    return {
        "company_id": company_id,
        "users": mock_users[offset : offset + limit],
        "total": len(mock_users),
    }


@router.get("/{company_id}/scripts")
async def get_company_scripts(
    company_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get scripts for a company."""

    # Placeholder implementation until scripts are associated with companies.
    mock_scripts = [
        {
            "id": 1,
            "title": "Sales Script",
            "status": "active",
            "usage_count": 45,
        },
        {
            "id": 2,
            "title": "Support Script",
            "status": "active",
            "usage_count": 23,
        },
    ]

    return {
        "company_id": company_id,
        "scripts": mock_scripts[offset : offset + limit],
        "total": len(mock_scripts),
    }
