from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth_header(email, password):
    token = client.post("/auth/login", json={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_list_and_edit_time_entry():
    headers = auth_header("member@example.com", "member123")
    start = datetime.now(timezone.utc) - timedelta(hours=2)
    end = datetime.now(timezone.utc) - timedelta(hours=1)
    created = client.post("/time-entries", json={"project_id": 1, "task_id": 1, "start_time": start.isoformat(), "end_time": end.isoformat(), "notes": "work"}, headers=headers)
    assert created.status_code == 200
    entry_id = created.json()["id"]
    listed = client.get("/time-entries", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == entry_id for item in listed.json())
    updated = client.put(f"/time-entries/{entry_id}", json={"notes": "updated"}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["notes"] == "updated"


def test_member_cannot_edit_other_users_entry():
    admin_headers = auth_header("admin@example.com", "admin123")
    member_headers = auth_header("member@example.com", "member123")
    start = datetime.now(timezone.utc) - timedelta(hours=3)
    end = datetime.now(timezone.utc) - timedelta(hours=2)
    created = client.post("/time-entries", json={"project_id": 1, "task_id": 1, "start_time": start.isoformat(), "end_time": end.isoformat()}, headers=admin_headers)
    entry_id = created.json()["id"]
    response = client.put(f"/time-entries/{entry_id}", json={"notes": "nope"}, headers=member_headers)
    assert response.status_code == 403
