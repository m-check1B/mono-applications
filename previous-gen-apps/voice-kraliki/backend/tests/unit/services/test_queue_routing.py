
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.queue_routing import QueueRoutingService
from app.models.call_state import CallState, CallStatus

@pytest.mark.asyncio
async def test_get_average_handle_time_fallback():
    """Test fallback when no data is available."""
    db = MagicMock(spec=AsyncSession)
    # Mock result.scalar() returning None
    mock_result = MagicMock()
    mock_result.scalar.return_value = None
    db.execute = AsyncMock(return_value=mock_result)
    
    service = QueueRoutingService()
    avg_time = await service._get_average_handle_time(db)
    
    assert avg_time == 180.0

@pytest.mark.asyncio
async def test_get_average_handle_time_with_data():
    """Test calculation with data."""
    db = MagicMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar.return_value = 240.5
    db.execute = AsyncMock(return_value=mock_result)
    
    service = QueueRoutingService()
    avg_time = await service._get_average_handle_time(db, team_id=1)
    
    assert avg_time == 240.5
    # Check if query was built correctly
    args, kwargs = db.execute.call_args
    query = args[0]
    # Verify the query contains the filters
    query_str = str(query.compile())
    assert "call_states" in query_str
    assert "completed" in query_str
