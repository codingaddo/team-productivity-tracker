from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..deps import get_current_user, get_db, require_manager_or_admin
from ..models import Project, Task, TimeEntry, User
from ..schemas import TimeEntryCreate, TimeEntryOut, TimeEntryUpdate

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


def _serialize(entry: TimeEntry) -> TimeEntryOut:
    return TimeEntryOut(id=entry.id, user_id=entry.user_id, project_id=entry.project_id, task_id=entry.task_id, start_time=entry.start_time, end_time=entry.end_time, duration_hours=entry.duration_hours, notes=entry.notes)


@router.post("", response_model=TimeEntryOut)
def create_time_entry(payload: TimeEntryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.end_time and payload.end_time <= payload.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_time must be after start_time")
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.task_id and not db.query(Task).filter(Task.id == payload.task_id).first():
        raise HTTPException(status_code=404, detail="Task not found")
    duration = 0.0
    if payload.end_time:
        duration = (payload.end_time - payload.start_time).total_seconds() / 3600
    entry = TimeEntry(user_id=current_user.id, project_id=payload.project_id, task_id=payload.task_id, start_time=payload.start_time, end_time=payload.end_time, duration_hours=duration, notes=payload.notes)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _serialize(entry)


@router.get("", response_model=list[TimeEntryOut])
def list_time_entries(user_id: int | None = None, project_id: int | None = None, start_date: datetime | None = None, end_date: datetime | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(TimeEntry)
    if current_user.role == "member":
        query = query.filter(TimeEntry.user_id == current_user.id)
    elif user_id:
        query = query.filter(TimeEntry.user_id == user_id)
    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.start_time <= end_date)
    return [_serialize(entry) for entry in query.order_by(TimeEntry.start_time.desc()).all()]


@router.put("/{entry_id}", response_model=TimeEntryOut)
def update_time_entry(entry_id: int, payload: TimeEntryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entry = db.query(TimeEntry).filter(TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if current_user.role == "member" and entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if payload.project_id is not None:
        entry.project_id = payload.project_id
    if payload.task_id is not None:
        entry.task_id = payload.task_id
    if payload.start_time is not None:
        entry.start_time = payload.start_time
    if payload.end_time is not None:
        entry.end_time = payload.end_time
    if entry.end_time and entry.end_time <= entry.start_time:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")
    if payload.notes is not None:
        entry.notes = payload.notes
    entry.duration_hours = ((entry.end_time - entry.start_time).total_seconds() / 3600) if entry.end_time else 0.0
    db.commit()
    db.refresh(entry)
    return _serialize(entry)
