"""Tests for the system/probe endpoints."""


def test_health_returns_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_root_has_version(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "docs" in data


def test_ready_returns_ready(client):
    """With a working SQLite DB the /ready probe should return READY."""
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json()["status"] == "READY"


def test_ready_returns_503_when_db_broken(client, monkeypatch):
    """When the DB is unreachable, /ready must return 503 NOT_READY.
    We monkeypatch check_db_connection (used directly by /ready) to simulate
    a broken database — this is cleaner than overriding the get_db dependency
    because /ready calls check_db_connection, not get_db.
    """
    import app.main as main_module

    monkeypatch.setattr(main_module, "check_db_connection", lambda: False)
    res = client.get("/ready")
    assert res.status_code == 503
    assert res.json()["status"] == "NOT_READY"


def test_metrics_contains_help_after_api_call(client):
    """/metrics must expose Prometheus text after at least one real request."""
    client.get("/health")  # triggers the instrumentator
    # Make a real API call so http_requests_total has data
    client.get("/api/appointments")
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "# HELP" in res.text
