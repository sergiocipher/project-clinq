"""Tests covering every Appointment endpoint."""

BASE = "/api/appointments"

SAMPLE = {
    "patient_name": "Alice Smith",
    "doctor": "Dr. Chen",
    "scheduled_at": "2025-06-01T10:00:00",
    "notes": "Annual checkup",
    "status": "scheduled",
    "priority": "normal",
}


def create_one(client, overrides=None):
    """Helper: POST one appointment and return the parsed JSON."""
    data = {**SAMPLE, **(overrides or {})}
    res = client.post(BASE, json=data)
    assert res.status_code == 201, res.text
    return res.json()


# ── Create ────────────────────────────────────────────────────────────────────


def test_create_returns_201(client):
    appt = create_one(client)
    assert appt["patient_name"] == "Alice Smith"
    assert appt["status"] == "scheduled"
    assert appt["priority"] == "normal"
    assert "id" in appt


def test_create_invalid_status_returns_422(client):
    res = client.post(BASE, json={**SAMPLE, "status": "BOGUS"})
    assert res.status_code == 422


def test_create_missing_required_field_returns_422(client):
    body = {k: v for k, v in SAMPLE.items() if k != "patient_name"}
    res = client.post(BASE, json=body)
    assert res.status_code == 422


# ── List ──────────────────────────────────────────────────────────────────────


def test_list_returns_all(client):
    create_one(client)
    create_one(client, {"patient_name": "Bob Jones"})
    res = client.get(BASE)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_status_filter(client):
    create_one(client, {"status": "scheduled"})
    create_one(client, {"status": "completed"})
    res = client.get(BASE, params={"status": "scheduled"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["status"] == "scheduled"


def test_list_search_by_patient(client):
    create_one(client, {"patient_name": "Alice Smith"})
    create_one(client, {"patient_name": "Bob Jones"})
    res = client.get(BASE, params={"q": "alice"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert "Alice" in data[0]["patient_name"]


def test_list_search_by_doctor(client):
    create_one(client, {"doctor": "Dr. Chen"})
    create_one(client, {"doctor": "Dr. Smith"})
    res = client.get(BASE, params={"q": "smith"})
    assert res.status_code == 200
    assert any("Smith" in a["doctor"] for a in res.json())


# ── Get ───────────────────────────────────────────────────────────────────────


def test_get_returns_200(client):
    appt = create_one(client)
    res = client.get(f"{BASE}/{appt['id']}")
    assert res.status_code == 200
    assert res.json()["id"] == appt["id"]


def test_get_missing_returns_404(client):
    res = client.get(f"{BASE}/99999")
    assert res.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


def test_update_returns_200(client):
    appt = create_one(client)
    res = client.put(f"{BASE}/{appt['id']}", json={"status": "completed"})
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


def test_update_missing_returns_404(client):
    res = client.put(f"{BASE}/99999", json={"status": "completed"})
    assert res.status_code == 404


# ── Delete ────────────────────────────────────────────────────────────────────


def test_delete_returns_204(client):
    appt = create_one(client)
    res = client.delete(f"{BASE}/{appt['id']}")
    assert res.status_code == 204


def test_delete_then_get_returns_404(client):
    appt = create_one(client)
    client.delete(f"{BASE}/{appt['id']}")
    res = client.get(f"{BASE}/{appt['id']}")
    assert res.status_code == 404


# ── Stats ─────────────────────────────────────────────────────────────────────


def test_stats_counts_all_statuses(client):
    create_one(client, {"status": "scheduled"})
    create_one(client, {"status": "scheduled"})
    create_one(client, {"status": "completed"})
    res = client.get(f"{BASE}/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    # Every status key must be present, including zero-count ones
    assert set(data["by_status"].keys()) == {"scheduled", "completed", "cancelled"}
    assert data["by_status"]["scheduled"] == 2
    assert data["by_status"]["completed"] == 1
    assert data["by_status"]["cancelled"] == 0
    assert data["upcoming_count"] == 2


def test_stats_empty_db(client):
    res = client.get(f"{BASE}/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert all(v == 0 for v in data["by_status"].values())
