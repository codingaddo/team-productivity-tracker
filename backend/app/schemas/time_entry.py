from datetime import datetime

from pydantic import BaseModel, Field


class TimeEntryBase(BaseModel):
    description: str | None = Field(default=None, max_length=500)


class TimeEntryCreateManual(TimeEntryBase):
    start_time: datetime
    end_time: datetime


class TimeEntryStart(TimeEntryBase):
    start_time: datetime | None = None


class TimeEntryStop(BaseModel):
    end_time: datetime | None = None


class TimeEntryRead(TimeEntryBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: datetime | None

    class Config:
        from_attributes = True
