import asyncio
from datetime import datetime, timedelta

import httpx
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import create_app
from app.db.session import AsyncSessionLocal, engine
from app.db import base  # noqa: F401


app = create_app()
client = TestClient(app)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.drop_all)
        await conn.run_sync(base.Base.metadata.create_all)


def setup_module(module):  # noqa: ARG001
    asyncio.run(init_db())


def register_and_login(email: str = "user@example.com", password: str = "strongpassword") -> str:
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert resp.status_code == status.HTTP_201_CREATED

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    return data["access_token"]


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"


def test_register_login_and_me():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/auth/me", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["email"] == "user@example.com"


def test_time_entry_flow():
    token = register_and_login("timer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Start timer
    resp = client.post("/api/v1/time-entries/start", json={"description": "Task A"}, headers=headers)
    assert resp.status_code == status.HTTP_201_CREATED
    entry = resp.json()
    assert entry["description"] == "Task A"

    # Stop timer
    resp = client.post("/api/v1/time-entries/stop", json={}, headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    entry = resp.json()
    assert entry["end_time"] is not None

    # Manual entry
    start = datetime.utcnow() - timedelta(hours=2)
    end = datetime.utcnow() - timedelta(hours=1)
    resp = client.post(
        "/api/v1/time-entries/manual",
        json={
            "description": "Task B",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    # List entries
    resp = client.get("/api/v1/time-entries/", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    entries = resp.json()
    assert len(entries) >= 2


def test_reporting_endpoints():
    token = register_and_login("report@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a manual entry for today
    start = datetime.utcnow() - timedelta(hours=1)
    end = datetime.utcnow()
    resp = client.post(
        "/api/v1/time-entries/manual",
        json={
            "description": "Reporting Task",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers=headers,
    )
    assert resp.status_code == status.HTTP_201_CREATED

    today = datetime.utcnow().date().isoformat()

    # By day
    resp = client.get(
        f"/api/v1/reports/by-day?start_date={today}&end_date={today}",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) >= 1

    # By user
    resp = client.get(
        f"/api/v1/reports/by-user?start_date={today}&end_date={today}",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert any(row["total_seconds"] > 0 for row in data)

    # By task
    resp = client.get(
        f"/api/v1/reports/by-task?start_date={today}&end_date={today}",
        headers=headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert any(row["total_seconds"] > 0 for row in data)
