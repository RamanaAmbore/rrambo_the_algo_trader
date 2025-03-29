from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint, \
    Index, func, select
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_THREAD_SCHEDULE_XREF
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
    algo_thread = relationship("AlgoThreads", back_populates="thread_schedule")
    schedule_list = relationship("Schedules", back_populates="thread_schedule")

    __table_args__ = (
        UniqueConstraint('thread', 'schedule', name='uq_thread_schedule'),
        Index('idx_thread_schedule', 'thread', 'schedule'),
    )

    def __repr__(self):
        return (f"<ThreadSchedule(id={self.id}, thread='{self.thread}', "
                f"schedule='{self.schedule}', source='{self.source}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ThreadSchedule.__table__
        for record in DEF_THREAD_SCHEDULE_XREF:
            exists = connection.execute(
                select(table).where(
                    table.c.thread == record['thread'],
                    table.c.schedule == record['schedule']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Algo Thread Schedule Xref records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Algo Thread Schedule Xref records: {e}")
        raise
