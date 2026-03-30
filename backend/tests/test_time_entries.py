from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


async def _get_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "timer@example.com", "password": "password123", "full_name": "Timer User"},
    )
    assert resp.status_code in (200, 201)

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "timer@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_start_and_stop_timer(client: AsyncClient):
    token = await _get_token(client)

    resp = await client.post(
        "/api/v1/time-entries/start",
        json={"description": "Working on feature"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    entry = resp.json()
    assert entry["end_time"] is None

    resp = await client.post(
        "/api/v1/time-entries/stop",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    entry = resp.json()
    assert entry["end_time"] is not None


@pytest.mark.asyncio
async def test_manual_entry_and_list(client: AsyncClient):
    token = await _get_token(client)

    start = datetime.now(timezone.utc) - timedelta(hours=2)
    end = start + timedelta(hours=1)

    resp = await client.post(
        "/api/v1/time-entries/manual",
        json={
            "description": "Manual work",
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text

    resp = await client.get(
        "/api/v1/time-entries/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    entries = resp.json()
    assert len(entries) >= 1
