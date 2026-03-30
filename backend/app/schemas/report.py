from datetime import date

from pydantic import BaseModel


class DateRange(BaseModel):
    start_date: date
    end_date: date


class DailyTotal(BaseModel):
    date: date
    total_seconds: int


class UserTotal(BaseModel):
    user_id: int
    email: str
    total_seconds: int


class TaskTotal(BaseModel):
    description: str | None
    total_seconds: int
