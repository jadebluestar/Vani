def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_health_reports_dependency_status(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["cache"] == "ok"


def test_health_sets_request_id_header(client):
    resp = client.get("/health")
    assert "X-Request-ID" in resp.headers
