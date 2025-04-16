from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint, \
    Index, func
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class ThreadSchedule(Base):
    """Model for mapping threads to schedule_list."""
    __tablename__ = "thread_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(30), ForeignKey("thread_list.thread", ondelete="CASCADE"), nullable=False)
    schedule = Column(String(10), ForeignKey("schedule_list.schedule", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    thread_list_rel = relationship("ThreadList", back_populates="thread_schedule_rel", passive_deletes=True, )
    schedule_list_rel = relationship("ScheduleList", back_populates="thread_schedule_rel", passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint('thread', 'schedule', name='uq_thread_schedule'),
        Index('idx_thread_schedule', 'thread', 'schedule'),
    )

    def __repr__(self):
        return (f"<ThreadSchedule(id={self.id}, thread='{self.thread}', "
                f"schedule='{self.schedule}', source='{self.source}')>")
