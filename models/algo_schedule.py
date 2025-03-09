from sqlalchemy import Column, String, DateTime, text, Boolean, Enum, Integer, event, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.default_db_values import source, DEFAULT_SCHEDULE_RECORDS

logger = get_logger(__name__)


class AlgoSchedule(Base):
    """Stores schedule definitions that can be referenced by other tables."""
    __tablename__ = "algo_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(20), nullable=False, unique=True)  # Unique constraint for referential integrity
    is_active = Column(Boolean, nullable=False, default=True)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_schedule_time = relationship("AlgoScheduleTime", back_populates="algo_schedule")
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="algo_schedule")
    algo_thread_schedule_xref = relationship("AlgoThreadScheduleXref", back_populates="algo_schedule", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('schedule', name='uq_schedule'),
        Index("idx_schedule", "schedule"),
    )

    def __repr__(self):
        return (f"<AlgoSchedule(id={self.id}, schedule='{self.schedule}', "
                f"is_active={self.is_active}, source='{self.source}', "
                f"timestamp={self.timestamp}, notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoSchedule.__table__
        for record in DEFAULT_SCHEDULE_RECORDS:
            exists = connection.execute(select(table.c.schedule).where(
                table.c.schedule == record['schedule'])).scalar() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default records: {e}")


@event.listens_for(AlgoSchedule.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Algo Schedule records inserted after after_create event')
