"""
Unit tests for Sales and Audit Router
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.models.user import User
from app.services.sales_service import SalesService

@pytest.mark.unit
class TestSalesRouter:
    """Test Sales Router API endpoints"""

    async def test_list_templates_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test listing sales templates"""
        mock_templates = ["AUDIT-REPORT-TEMPLATE", "RETAINER-PROPOSAL"]
        
        with patch.object(SalesService, 'list_templates', return_value=mock_templates):
            response = await async_client.get("/sales/templates", headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json() == mock_templates

    async def test_list_templates_unauthenticated(self, async_client: AsyncClient):
        """Test listing templates without auth"""
        response = await async_client.get("/sales/templates")
        assert response.status_code == 401

    async def test_generate_report_success(self, async_client: AsyncClient, auth_headers: dict):
        """Test generating a sales report"""
        payload = {
            "template_name": "AUDIT-REPORT-TEMPLATE",
            "client_name": "Test Client",
            "data": {"key": "value"}
        }
        
        mock_content = "# Test Audit Report"
        mock_path = "/tmp/reports/test_audit.md"
        
        with patch.object(SalesService, 'generate_report', return_value=mock_content), \
             patch.object(SalesService, 'save_generated_report', return_value=mock_path):
            
            response = await async_client.post("/sales/generate", json=payload, headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["template_name"] == payload["template_name"]
            assert data["client_name"] == payload["client_name"]
            assert data["report_content"] == mock_content
            assert data["file_path"] == mock_path

    async def test_generate_report_template_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test generating report with invalid template"""
        payload = {
            "template_name": "INVALID-TEMPLATE",
            "client_name": "Test Client",
            "data": {}
        }
        
        with patch.object(SalesService, 'generate_report', side_effect=FileNotFoundError("Template not found")):
            response = await async_client.post("/sales/generate", json=payload, headers=auth_headers)
            
            assert response.status_code == 404
            assert "Template not found" in response.json()["detail"]

    async def test_generate_automated_audit_success(self, async_client: AsyncClient, auth_headers: dict, db: Session, test_user: User):
        """Test automated audit generation for a project"""
        # Create a mock project in DB
        from app.models.task import Project
        project = Project(
            id="test-project-123",
            name="Test Business",
            userId=test_user.id
        )
        db.add(project)
        db.commit()
        
        mock_content = "# Automated AI Audit"
        mock_path = "/tmp/reports/automated_audit.md"
        
        with patch.object(SalesService, 'generate_automated_audit', return_value=mock_content), \
             patch.object(SalesService, 'save_generated_report', return_value=mock_path):
            
            response = await async_client.get(f"/sales/audit/{project.id}", headers=auth_headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["client_name"] == project.name
            assert data["report_content"] == mock_content
            assert data["file_path"] == mock_path

    async def test_generate_automated_audit_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """Test automated audit for non-existent project"""
        with patch.object(SalesService, 'generate_automated_audit', side_effect=ValueError("Project not found")):
            response = await async_client.get("/sales/audit/invalid-id", headers=auth_headers)
            
            assert response.status_code == 404
            assert "Project not found" in response.json()["detail"]

@pytest.mark.unit
class TestSalesService:
    """Test SalesService class directly"""

    def test_generate_report_logic(self):
        """Test the template replacement logic in generate_report"""
        mock_template = "Hello [Client Name], today is [Date]. Your savings are €[Amount]."
        data = {
            "Client Name": "Acme Corp",
            "Date": "2025-12-27",
            "Amount": "5,000"
        }
        
        with patch.object(SalesService, 'get_template', return_value=mock_template):
            report = SalesService.generate_report("dummy", data)
            assert report == "Hello Acme Corp, today is 2025-12-27. Your savings are €5,000."

    def test_save_generated_report(self):
        """Test saving report to disk"""
        content = "# Test Report"
        client_name = "TestClient"
        report_type = "AUDIT"
        
        # Use a mock for mkdir and open
        with patch("pathlib.Path.mkdir"), \
             patch("builtins.open", MagicMock()):
            file_path = SalesService.save_generated_report(content, client_name, report_type)
            assert "TestClient" in file_path
            assert "AUDIT" in file_path
            assert file_path.endswith(".md")

    async def test_generate_automated_audit_data_processing(self, db: Session, test_user: User):
        """Test data processing in generate_automated_audit"""
        from app.models.task import Project, Task
        
        project = Project(id="p1", name="Project 1", userId=test_user.id)
        db.add(project)
        
        # Task with audit data
        task1 = Task(
            id="t1", 
            projectId="p1", 
            title="Manual Task", 
            aiInsights={"human_cost": 100, "ai_cost": 10}
        )
        # Task without audit data
        task2 = Task(id="t2", projectId="p1", title="Normal Task")
        # Quick win task
        task3 = Task(id="t3", projectId="p1", title="Quick Win", tags=["quick-win"])
        
        db.add_all([task1, task2, task3])
        db.commit()
        
        mock_template = "Audit for [Client Name]. Savings: [Amount]. Primary: [Primary Friction Source]."
        
        with patch.object(SalesService, 'get_template', return_value=mock_template):
            # Also mock ShadowAnalyzerService to return None (testing fallback)
            with patch("app.services.sales_service.ShadowAnalyzerService.get_profile", return_value=None):
                report = await SalesService.generate_automated_audit(db, test_user.id, "p1")
                
                assert "Project 1" in report
                assert "90.0" in report # Savings: 100 - 10
                assert "Manual Data Entry" in report # Fallback friction source
