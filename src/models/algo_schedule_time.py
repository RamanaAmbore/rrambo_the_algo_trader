from sqlalchemy import (Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey, Enum, CheckConstraint,
                        Index, text, event, UniqueConstraint, func)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.settings.parameter_loader import Source, Weekday, DEFAULT_ALGO_SCHEDULE_TIME_RECORDS
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class AlgoScheduleTime(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "algo_schedule_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(20), ForeignKey("algo_schedules.schedule", ondelete="CASCADE"), nullable=False)
    market_date = Column(Date, nullable=True)
    weekday = Column(Enum(Weekday), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_market_open = Column(Boolean, nullable=False, default=True)
    source = Column(Enum(Source), nullable=False, server_default=Source.MANUAL.name)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_schedules = relationship("AlgoSchedules", back_populates="algo_schedule_time")

    __table_args__ = (
        CheckConstraint("market_date IS NOT NULL OR weekday IS NOT NULL", name="check_at_least_one_not_null"),
        UniqueConstraint('schedule', 'market_date', 'weekday', 'start_time', name='uq_schedule_time'),
        Index('idx_schedule_time', 'schedule', 'market_date', 'weekday'),)

    def __repr__(self):
        return (f"<AlgoScheduleTime(id={self.id}, "
                f"schedule='{self.schedule}', "
                f"market_date={self.market_date}, weekday={self.weekday}, "
                f"start_time={self.start_time}, end_time={self.end_time}, "
                f"is_market_open={self.is_market_open}, source='{self.source}', "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoScheduleTime.__table__
        for record in DEFAULT_ALGO_SCHEDULE_TIME_RECORDS:
            exists = connection.execute(
                select(table).where(
                    table.c.schedule == record['schedule'],
                    table.c.weekday == record['weekday']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except SQLAlchemyError as e:
        logger.error(f"Error managing default Algo Schedule Time records: {e}")
        raise


@event.listens_for(AlgoScheduleTime.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Schedule Time records inserted after after_create event')
