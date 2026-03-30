from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.schemas.time_entry import (
    TimeEntryCreateManual,
    TimeEntryRead,
    TimeEntryStart,
    TimeEntryStop,
)

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


@router.post("/start", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
async def start_timer(
    payload: TimeEntryStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ensure there is no active timer
    active_stmt = select(TimeEntry).where(
        and_(TimeEntry.user_id == current_user.id, TimeEntry.end_time.is_(None))
    )
    active_result = await db.execute(active_stmt)
    if active_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Active timer already exists")

    start_time = payload.start_time or datetime.utcnow()
    entry = TimeEntry(
        user_id=current_user.id,
        description=payload.description,
        start_time=start_time,
        end_time=None,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/stop", response_model=TimeEntryRead)
async def stop_timer(
    payload: TimeEntryStop,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(TimeEntry).where(
        and_(TimeEntry.user_id == current_user.id, TimeEntry.end_time.is_(None))
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active timer found")

    entry.end_time = payload.end_time or datetime.utcnow()
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/manual", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
async def create_manual_entry(
    payload: TimeEntryCreateManual,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be after start_time")

    entry = TimeEntry(
        user_id=current_user.id,
        description=payload.description,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/", response_model=list[TimeEntryRead])
async def list_entries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(default=100, le=500),
):
    stmt = (
        select(TimeEntry)
        .where(TimeEntry.user_id == current_user.id)
        .order_by(TimeEntry.start_time.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()
    return list(entries)
