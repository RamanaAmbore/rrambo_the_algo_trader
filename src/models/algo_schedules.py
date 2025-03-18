from sqlalchemy import Column, String, DateTime, text, Enum, Integer, event, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.settings.parameter_loader import Source, DEFAULT_ALGO_SCHEDULES
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class AlgoSchedules(Base):
    """Stores schedule definitions that can be referenced by other tables."""
    __tablename__ = "algo_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(20), nullable=False, unique=True)  # Unique constraint for referential integrity
    source = Column(Enum(Source), nullable=False, server_default=Source.MANUAL.name)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_schedule_time = relationship("AlgoScheduleTime", back_populates="algo_schedules", cascade="all, delete-orphan")
    algo_thread_schedule_xref = relationship("AlgoThreadScheduleXref", back_populates="algo_schedules",
                                             cascade="all, delete-orphan")
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="algo_schedules",
                                             cascade="all, delete-orphan")

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
        table = AlgoSchedules.__table__
        for record in DEFAULT_ALGO_SCHEDULES:
            exists = connection.execute(select(table.c.schedule).where(
                table.c.schedule == record['schedule'])).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Alog Schedule records: {e}")
        raise


@event.listens_for(AlgoSchedules.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Algo Schedule records inserted after after_create event')
