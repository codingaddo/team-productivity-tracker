from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.schemas.report import DailyTotal, TaskTotal, UserTotal

router = APIRouter(prefix="/reports", tags=["reports"])


async def _validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be on or after start_date")


@router.get("/by-day", response_model=list[DailyTotal])
async def report_by_day(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _validate_date_range(start_date, end_date)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    duration = func.extract("epoch", TimeEntry.end_time - TimeEntry.start_time)

    stmt = (
        select(func.date(TimeEntry.start_time).label("day"), func.coalesce(func.sum(duration), 0))
        .where(
            TimeEntry.user_id == current_user.id,
            TimeEntry.start_time >= start_dt,
            TimeEntry.end_time <= end_dt,
            TimeEntry.end_time.is_not(None),
        )
        .group_by(func.date(TimeEntry.start_time))
        .order_by(func.date(TimeEntry.start_time))
    )

    result = await db.execute(stmt)
    rows = result.all()
    return [DailyTotal(date=row[0], total_seconds=int(row[1])) for row in rows]


@router.get("/by-user", response_model=list[UserTotal])
async def report_by_user(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _validate_date_range(start_date, end_date)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    duration = func.extract("epoch", TimeEntry.end_time - TimeEntry.start_time)

    stmt = (
        select(User.id, User.email, func.coalesce(func.sum(duration), 0))
        .join(TimeEntry, TimeEntry.user_id == User.id)
        .where(
            TimeEntry.start_time >= start_dt,
            TimeEntry.end_time <= end_dt,
            TimeEntry.end_time.is_not(None),
        )
        .group_by(User.id, User.email)
        .order_by(User.email)
    )

    result = await db.execute(stmt)
    rows = result.all()
    return [UserTotal(user_id=row[0], email=row[1], total_seconds=int(row[2])) for row in rows]


@router.get("/by-task", response_model=list[TaskTotal])
async def report_by_task(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _validate_date_range(start_date, end_date)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    duration = func.extract("epoch", TimeEntry.end_time - TimeEntry.start_time)

    stmt = (
        select(TimeEntry.description, func.coalesce(func.sum(duration), 0))
        .where(
            TimeEntry.user_id == current_user.id,
            TimeEntry.start_time >= start_dt,
            TimeEntry.end_time <= end_dt,
            TimeEntry.end_time.is_not(None),
        )
        .group_by(TimeEntry.description)
        .order_by(TimeEntry.description)
    )

    result = await db.execute(stmt)
    rows = result.all()
    return [TaskTotal(description=row[0], total_seconds=int(row[1])) for row in rows]
