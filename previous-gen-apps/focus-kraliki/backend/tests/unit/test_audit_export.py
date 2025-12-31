import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.routers.exports import AuditExportRequest, generate_audit_report
from app.models.shadow_profile import ShadowProfile
from app.models.task import Task

@pytest.mark.asyncio
async def test_generate_audit_report_logic():
    # Setup mocks
    mock_db = MagicMock()
    mock_user = Mock()
    mock_user.id = "user-123"
    mock_user.username = "testuser"
    mock_user.email = "test@example.com"
    
    # Mock Shadow Profile
    mock_shadow = ShadowProfile(
        id="shadow-1",
        user_id="user-123",
        archetype="sage"
    )
    
    # Mock Tasks
    mock_tasks = [
        Task(id="task-1", title="Manual Data Entry", userId="user-123", estimatedMinutes=60, createdAt=datetime.now()),
        Task(id="task-2", title="Manual Data Entry", userId="user-123", estimatedMinutes=60, createdAt=datetime.now()),
        Task(id="task-3", title="Research AI", userId="user-123", estimatedMinutes=30, createdAt=datetime.now())
    ]
    
    # Configure DB query mock
    def mock_query(model):
        query = MagicMock()
        if model == ShadowProfile:
            query.filter.return_value.first.return_value = mock_shadow
        elif model == Task:
            query.filter.return_value.all.return_value = mock_tasks
        return query
        
    mock_db.query.side_effect = mock_query
    
    # Create request
    request = AuditExportRequest(
        client_name="Acme Corp",
        format="md",
        hourly_rate=100.0
    )
    
    # Call endpoint function
    response = await generate_audit_report(request, current_user=mock_user, db=mock_db)
    
    # Verify response is a StreamingResponse (since format is md)
    assert response.media_type == "text/markdown"
    assert "attachment; filename=audit-report-Acme-Corp.md" in response.headers["Content-Disposition"]
    
    # Extract report content from iterator
    report_content = ""
    async for chunk in response.body_iterator:
        report_content += chunk
        
    # Verify content
    assert "# Reality Check Audit Report: Acme Corp" in report_content
    assert "Overthinking and Analysis Paralysis" in report_content  # Sage friction
    assert "Manual Data Entry" in report_content
    assert "€" in report_content
