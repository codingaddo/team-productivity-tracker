from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str


class ProjectOut(BaseModel):
    id: int
    name: str


class TimeEntryCreate(BaseModel):
    project_id: int
    task_id: int | None = None
    start_time: datetime
    end_time: datetime | None = None
    notes: str = ""


class TimeEntryUpdate(BaseModel):
    project_id: int | None = None
    task_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    notes: str | None = None


class TimeEntryOut(BaseModel):
    id: int
    user_id: int
    project_id: int
    task_id: int | None
    start_time: datetime
    end_time: datetime | None
    duration_hours: float
    notes: str


class UserSummaryItem(BaseModel):
    date: str
    hours: float


class ProjectSummaryItem(BaseModel):
    project_id: int
    project_name: str
    user_id: int
    user_name: str
    hours: float
