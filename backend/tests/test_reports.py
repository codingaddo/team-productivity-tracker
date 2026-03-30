from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def auth_header(email, password):
    token = client.post("/auth/login", json={"username": email, "password": password}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_summary_returns_current_user_data():
    headers = auth_header("member@example.com", "member123")
    start = datetime.now(timezone.utc) - timedelta(days=1)
    end = datetime.now(timezone.utc)
    response = client.get("/reports/user-summary", params={"start_date": start.isoformat(), "end_date": end.isoformat()}, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_project_summary_role_visibility():
    headers = auth_header("member@example.com", "member123")
    response = client.get("/reports/project-summary", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
