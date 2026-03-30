from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_success_and_me():
    response = client.post("/auth/login", json={"username": "admin@example.com", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "admin"


def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"username": "admin@example.com", "password": "wrong"})
    assert response.status_code == 401


def test_protected_endpoint_requires_token():
    response = client.get("/auth/me")
    assert response.status_code == 401
