from sqlalchemy import Column, Integer, String, DateTime, text, Index, UniqueConstraint, func, Boolean, select
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_THREAD_LIST
from .base import Base

logger = get_logger(__name__)


class ThreadList(Base):
    """Model for storing thread definitions."""
    __tablename__ = "thread_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(30), nullable=False, unique=True)  # Changed length to match ThreadStatus
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with ThreadStatus
    thread_status_tracker_rel = relationship("ThreadStatusTracker", back_populates="thread_list_rel",
                                       passive_deletes=True, )  # Relationship with ThreadStatus
    thread_schedule_rel = relationship("ThreadSchedule", back_populates="thread_list_rel",
                                             passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint('thread', name='uq_algo_thread'),
        Index("idx_thread", "thread"),
    )

    def __repr__(self):
        return (f"<Thread(id={self.id}, thread='{self.thread}', "
                f"source='{self.source}', notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ThreadList.__table__
        for record in DEF_THREAD_LIST:
            exists = connection.execute(select(table.c.thread).where(
                table.c.thread == record['thread'])).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Thread List records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Thread List records: {e}")
        raise
