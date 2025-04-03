from sqlalchemy import Column, String, DateTime, text, Integer, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_SCHEDULES
from .base import Base

logger = get_logger(__name__)


class ScheduleList(Base):
    """Stores schedule definitions that can be referenced by other tables."""
    __tablename__ = "schedule_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(10), nullable=False, unique=True)  # Unique constraint for referential integrity
    source = Column(String(50), nullable=False, default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    schedule_time_rel = relationship("ScheduleTime", back_populates="schedule_list_rel", passive_deletes=True, )
    thread_schedule_rel = relationship("ThreadSchedule", back_populates="schedule_list_rel",
                                             passive_deletes=True, )
    thread_status_tracker_rel = relationship("ThreadStatusTracker", back_populates="schedule_list_rel",
                                             passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint('schedule', name='uq_schedule1'),
        Index("idx_schedule", "schedule"),
    )

    def __repr__(self):
        return (f"<scheduleSchedule(id={self.id}, schedule='{self.schedule}', "
                f"is_active={self.is_active}, source='{self.source}', "
                f"timestamp={self.timestamp}, notes='{self.notes}')>")



