from sqlalchemy import Column, Integer, String, DateTime, text, Index, Enum, UniqueConstraint, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from src.utils.date_time_utils import timestamp_indian
from src.utils.logger import get_logger
from .base import Base
from src.settings.parameter_loader import Source, DEFAULT_ALGO_THREADS

logger = get_logger(__name__)

class AlgoThreads(Base):
    """Model for storing thread definitions."""
    __tablename__ = "algo_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(50), nullable=False, unique=True)  # Changed length to match ThreadStatus
    source = Column(Enum(Source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with ThreadStatus
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="algo_thread", cascade="all, delete-orphan")   # Relationship with ThreadStatus
    algo_thread_schedule_xref = relationship("AlgoThreadScheduleXref", back_populates="algo_thread", cascade="all, delete-orphan")

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
        table = AlgoThreads.__table__
        for record in DEFAULT_ALGO_THREADS:
            exists = connection.execute(select(table.c.thread).where(
                table.c.thread == record['thread'])).scalar() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Algo Threads records: {e}")
        raise


@event.listens_for(AlgoThreads.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Algo Thread records inserted after after_create event')