def test_health_endpoint_returns_200(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "healthy"
    assert "database" in body

def test_health_reports_actual_database_backend(client):
    res = client.get("/health")
    body = res.json()
    # The test harness runs on SQLite (see conftest.py) — the health check
    # must say so, not hardcode Postgres.
    assert "sqlite" in body["database"].lower()

