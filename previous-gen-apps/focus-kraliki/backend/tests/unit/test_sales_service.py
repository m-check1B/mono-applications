import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from app.services.sales_service import SalesService
from app.models.task import Task, Project
from app.models.shadow_profile import ShadowProfile

@pytest.fixture
def mock_db():
    return MagicMock()

class TestSalesService:
    @patch("app.services.sales_service.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="Template [Name] content")
    def test_get_template_success(self, mock_file, mock_exists):
        mock_exists.return_value = True
        content = SalesService.get_template("test_template")
        assert content == "Template [Name] content"
        mock_file.assert_called_once()

    @patch("app.services.sales_service.Path.exists")
    def test_get_template_not_found(self, mock_exists):
        mock_exists.return_value = False
        with pytest.raises(FileNotFoundError):
            SalesService.get_template("non_existent")

    @patch("app.services.sales_service.SalesService.TEMPLATES_DIR")
    def test_list_templates(self, mock_dir):
        mock_dir.exists.return_value = True
        mock_file1 = MagicMock()
        mock_file1.stem = "template1"
        mock_file1.suffix = ".md"
        mock_file2 = MagicMock()
        mock_file2.stem = "template2"
        mock_file2.suffix = ".md"
        mock_dir.glob.return_value = [mock_file1, mock_file2]
        
        templates = SalesService.list_templates()
        assert "template1" in templates
        assert "template2" in templates

    def test_generate_report(self):
        with patch.object(SalesService, 'get_template', return_value="Hello [Name], welcome to [App]!"):
            data = {"Name": "Alice", "App": "Focus by Kraliki"}
            report = SalesService.generate_report("test", data)
            assert report == "Hello Alice, welcome to Focus by Kraliki!"

    @pytest.mark.asyncio
    @patch("app.services.sales_service.ShadowAnalyzerService")
    async def test_generate_automated_audit_success(self, mock_shadow_service_class, mock_db):
        # Setup mocks
        mock_project = Project(id="p1", name="Test Project", userId="u1")
        mock_task = Task(id="t1", title="Task 1", projectId="p1", aiInsights={"human_cost": 100, "ai_cost": 10})
        mock_task.tags = ["quick-win"]
        mock_task.description = "A quick win task"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_task]
        
        mock_shadow_service = mock_shadow_service_class.return_value
        mock_shadow_profile = MagicMock(spec=ShadowProfile)
        mock_shadow_profile.archetype = "The Perfectionist"
        # Use AsyncMock for the async method
        from unittest.mock import AsyncMock
        mock_shadow_service.get_profile = AsyncMock(return_value=mock_shadow_profile)
        
        with patch.object(SalesService, 'get_template', return_value="Report for [Client Name] on [Date]. Savings: [Amount]. Wins: [Quick Win 1]"), \
             patch.object(SalesService, 'generate_report', side_effect=lambda t, d: f"Report for {d['Client Name']} on {d['Date']}. Savings: {d['Amount']}. Wins: {d['Quick Win 1']}"):
            
            report = await SalesService.generate_automated_audit(mock_db, "u1", "p1")
            
            assert "Test Project" in report
            assert "Savings: 90.0" in report
            assert "Wins: Task 1" in report

    @pytest.mark.asyncio
    async def test_generate_automated_audit_project_not_found(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Project p1 not found for user u1"):
            await SalesService.generate_automated_audit(mock_db, "u1", "p1")

    @patch("app.services.sales_service.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="content")
    def test_get_template_with_extension_logic(self, mock_file, mock_exists):
        # Case 1: No extension provided
        mock_exists.return_value = True
        content = SalesService.get_template("test")
        assert content == "content"
        
        # Case 2: Extension provided
        content = SalesService.get_template("test.md")
        assert content == "content"

    @patch("app.services.sales_service.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_generated_report_dir_exists(self, mock_file, mock_mkdir):
        # Test with mkdir being called
        SalesService.save_generated_report("Content", "Client", "Type")
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)

    @pytest.mark.asyncio
    @patch("app.services.sales_service.ShadowAnalyzerService")
    async def test_generate_automated_audit_no_shadow_profile(self, mock_shadow_service_class, mock_db):
        mock_project = Project(id="p1", name="Test", userId="u1")
        mock_db.query.return_value.filter.return_value.first.return_value = mock_project
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        mock_shadow_service = mock_shadow_service_class.return_value
        from unittest.mock import AsyncMock
        mock_shadow_service.get_profile = AsyncMock(return_value=None)
        
        with patch.object(SalesService, 'get_template', return_value="[Primary Friction Source]"), \
             patch.object(SalesService, 'generate_report', side_effect=lambda t, d: d["Primary Friction Source"]):
            report = await SalesService.generate_automated_audit(mock_db, "u1", "p1")
            assert report == "Manual Data Entry / Task Fragmentation"
