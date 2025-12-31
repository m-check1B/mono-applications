from fastapi.testclient import TestClient
from app.module import PlanningModule


def test_planning_module_metrics_counts():
    module = PlanningModule(platform_mode=False)
    app = module.get_app()
    client = TestClient(app)

    client.get("/health")
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["requests"] >= 1
    assert body["errors"] >= 0
