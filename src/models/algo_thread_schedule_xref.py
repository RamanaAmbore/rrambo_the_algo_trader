from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint, \
    Index, func
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class AlgoThreadScheduleXref(Base):
    """Model for mapping threads to schedules."""
    __tablename__ = "algo_thread_schedule_xref"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(30), ForeignKey("algo_threads.thread", ondelete="CASCADE"), nullable=False)
    schedule = Column(String(10), ForeignKey("algo_schedules.schedule", ondelete="CASCADE"), nullable=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_thread = relationship("AlgoThreads", back_populates="algo_thread_schedule_xref")
    algo_schedules = relationship("AlgoSchedules", back_populates="algo_thread_schedule_xref")

    __table_args__ = (
        UniqueConstraint('thread', 'schedule', name='uq_thread_schedule'),
        Index('idx_thread_schedule', 'thread', 'schedule'),
    )

    def __repr__(self):
        return (f"<AlgoThreadScheduleXref(id={self.id}, thread='{self.thread}', "
                f"schedule='{self.schedule}', source='{self.source}')>")
