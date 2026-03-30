from fastapi import FastAPI
from .database import Base, engine
from .models import Project, Task, TimeEntry, User
from .routers.auth import router as auth_router
from .routers.time_entries import router as time_entries_router
from .routers.reports import router as reports_router
from .deps import hash_password
from sqlalchemy.orm import Session
from .database import SessionLocal

app = FastAPI(title="Team Productivity Tracker API")
app.include_router(auth_router)
app.include_router(time_entries_router)
app.include_router(reports_router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    if not db.query(User).first():
        admin = User(email="admin@example.com", full_name="Admin User", hashed_password=hash_password("admin123"), role="admin")
        manager = User(email="manager@example.com", full_name="Manager User", hashed_password=hash_password("manager123"), role="manager")
        member = User(email="member@example.com", full_name="Member User", hashed_password=hash_password("member123"), role="member")
        project = Project(name="Internal Tracker")
        db.add_all([admin, manager, member, project])
        db.commit()
        db.refresh(project)
        db.add(Task(project_id=project.id, title="Initial task", description="Seed task"))
        db.commit()
    db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
