def test_health_ok_when_all_dependencies_up(client):
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "ok", "redis": "ok"}


def test_health_503_when_redis_down(client, monkeypatch):
    monkeypatch.setattr("app.api.health._check_redis", lambda: False)
    resp = client.get("/health")

    assert resp.status_code == 503
    assert resp.json() == {"status": "unhealthy", "database": "ok", "redis": "down"}


def test_health_503_when_database_down(client, monkeypatch):
    monkeypatch.setattr("app.api.health._check_database", lambda db: False)
    resp = client.get("/health")

    assert resp.status_code == 503
    assert resp.json() == {"status": "unhealthy", "database": "down", "redis": "ok"}


def test_health_needs_no_auth(client):
    assert client.get("/health").status_code != 401