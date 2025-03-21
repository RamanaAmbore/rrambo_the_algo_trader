from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean, text, event, UniqueConstraint, \
    Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.settings.constants_manager import Source, DEFAULT_THREAD_SCHEDULE_XREF, Schedule, Thread
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
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


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoThreadScheduleXref.__table__
        for record in DEFAULT_THREAD_SCHEDULE_XREF:
            exists = connection.execute(
                select(table).where(
                    table.c.thread == record['thread'],
                    table.c.schedule == record['schedule']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Algo Thread Schedule Xref records: {e}")
        raise


@event.listens_for(AlgoThreadScheduleXref.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Algo Thread Schedule Xref records inserted after after_create event')
