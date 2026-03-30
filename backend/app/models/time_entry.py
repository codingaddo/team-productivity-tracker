from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    user = relationship("User", back_populates="time_entries")
