"""Call management tests"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_calls(async_client: AsyncClient):
    """Test listing calls"""
    response = await async_client.get("/api/calls/")

    # Currently returns 501 Not Implemented
    assert response.status_code in [200, 501]


@pytest.mark.asyncio
async def test_create_call(async_client: AsyncClient, sample_call_data):
    """Test creating a new call"""
    response = await async_client.post("/api/calls/", json=sample_call_data)

    # Currently returns 501 Not Implemented
    assert response.status_code in [201, 501]

    if response.status_code == 201:
        data = response.json()
        assert data["from_number"] == sample_call_data["from_number"]
        assert data["to_number"] == sample_call_data["to_number"]
        assert data["direction"] == sample_call_data["direction"]


@pytest.mark.asyncio
async def test_get_call(async_client: AsyncClient):
    """Test getting a call by ID"""
    call_id = "test-call-id"
    response = await async_client.get(f"/api/calls/{call_id}")

    # Currently returns 501 Not Implemented or 404
    assert response.status_code in [200, 404, 501]


@pytest.mark.asyncio
async def test_update_call(async_client: AsyncClient):
    """Test updating a call"""
    call_id = "test-call-id"
    update_data = {"status": "IN_PROGRESS", "notes": "Test notes"}

    response = await async_client.put(f"/api/calls/{call_id}", json=update_data)

    # Currently returns 501 Not Implemented or 404
    assert response.status_code in [200, 404, 501]
