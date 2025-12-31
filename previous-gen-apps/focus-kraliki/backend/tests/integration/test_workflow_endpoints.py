"""
Integration tests for workflow endpoints
"""


class TestWorkflowEndpoints:
    """Test workflow template endpoints"""

    def test_list_workflow_templates(self, client, auth_headers):
        """Test listing workflow templates"""
        response = client.get("/workflow/templates", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert "total" in data
        assert isinstance(data["templates"], list)

    def test_create_workflow_template(self, client, auth_headers):
        """Test creating a workflow template"""
        payload = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "category": "testing",
            "steps": [
                {
                    "step": 1,
                    "action": "First step",
                    "estimatedMinutes": 15,
                    "dependencies": [],
                    "type": "manual"
                },
                {
                    "step": 2,
                    "action": "Second step",
                    "estimatedMinutes": 20,
                    "dependencies": [1],
                    "type": "manual"
                }
            ],
            "tags": ["test"],
            "isPublic": False,
            "isSystem": False
        }

        response = client.post("/workflow/templates", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert len(data["steps"]) == 2
        assert data["totalEstimatedMinutes"] == 35

        # Cleanup - delete the created template
        template_id = data["id"]
        client.delete(f"/workflow/templates/{template_id}", headers=auth_headers)

    def test_get_workflow_categories(self, client, auth_headers):
        """Test getting workflow categories"""
        response = client.get("/workflow/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "default_categories" in data
        assert isinstance(data["default_categories"], list)
