from sqlalchemy import (Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey, CheckConstraint,
                        Index, text, UniqueConstraint, func, select)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEFAULT_ALGO_SCHEDULE_TIME_RECORDS
from .base import Base

logger = get_logger(__name__)


class ScheduleTime(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "schedule_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(10), ForeignKey("schedules.schedule", ondelete="CASCADE"), nullable=False)
    market_date = Column(Date, nullable=True)
    weekday = Column(String(10), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_market_open = Column(Boolean, nullable=False, default=True)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    schedules = relationship("Schedules", back_populates="schedule_time")

    __table_args__ = (
        CheckConstraint("market_date IS NOT NULL OR weekday IS NOT NULL", name="check_at_least_one_not_null"),
        UniqueConstraint('schedule', 'market_date', 'weekday', 'start_time', name='uq_schedule_time'),
        Index('idx_schedule_time', 'schedule', 'market_date', 'weekday'),)

    def __repr__(self):
        return (f"<ScheduleTime(id={self.id}, "
                f"schedule='{self.schedule}', "
                f"market_date={self.market_date}, weekday={self.weekday}, "
                f"start_time={self.start_time}, end_time={self.end_time}, "
                f"is_market_open={self.is_market_open}, source='{self.source}', "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ScheduleTime.__table__
        for record in DEFAULT_ALGO_SCHEDULE_TIME_RECORDS:
            exists = connection.execute(
                select(table).where(
                    table.c.schedule == record['schedule'],
                    table.c.weekday == record['weekday']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Schedule Time records inserted/updated')
    except SQLAlchemyError as e:
        logger.error(f"Error managing default Algo Schedule Time records: {e}")
        raise
