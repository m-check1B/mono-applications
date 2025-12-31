from fastapi.testclient import TestClient
from app.module import PlanningModule


def test_platform_adapter_health_smoke():
    module = PlanningModule(platform_mode=True)
    app = module.get_app()
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "healthy"
