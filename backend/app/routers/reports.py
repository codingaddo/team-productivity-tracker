from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..deps import get_current_user, get_db
from ..models import Project, TimeEntry, User
from ..schemas import ProjectSummaryItem, UserSummaryItem

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/user-summary", response_model=list[UserSummaryItem])
def user_summary(start_date: datetime | None = None, end_date: datetime | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(func.date(TimeEntry.start_time).label("day"), func.sum(TimeEntry.duration_hours).label("hours")).filter(TimeEntry.user_id == current_user.id)
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.start_time <= end_date)
    rows = query.group_by("day").order_by("day").all()
    return [UserSummaryItem(date=str(day), hours=float(hours or 0)) for day, hours in rows]


@router.get("/project-summary", response_model=list[ProjectSummaryItem])
def project_summary(start_date: datetime | None = None, end_date: datetime | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Project.id, Project.name, User.id, User.full_name, func.sum(TimeEntry.duration_hours)).join(TimeEntry, TimeEntry.project_id == Project.id).join(User, User.id == TimeEntry.user_id)
    if current_user.role == "member":
        query = query.filter(TimeEntry.user_id == current_user.id)
    if start_date:
        query = query.filter(TimeEntry.start_time >= start_date)
    if end_date:
        query = query.filter(TimeEntry.start_time <= end_date)
    rows = query.group_by(Project.id, Project.name, User.id, User.full_name).all()
    return [ProjectSummaryItem(project_id=pid, project_name=pname, user_id=uid, user_name=uname, hours=float(hours or 0)) for pid, pname, uid, uname, hours in rows]
