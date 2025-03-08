from sqlalchemy import (Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey, Enum, CheckConstraint,
                        Index, text, event, UniqueConstraint)
from sqlalchemy.orm import relationship

from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from utils.model_utils import source, WeekdayEnum, DEFAULT_SCHEDULE_TIME_RECORDS  # Combined imports from model_utils
from .base import Base

logger = get_logger(__name__)


class AlgoScheduleTime(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "algo_schedule_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(20), ForeignKey("algo_schedule.schedule", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    market_date = Column(Date, nullable=True)
    weekday = Column(Enum(WeekdayEnum), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_market_open = Column(Boolean, nullable=False, default=True)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    broker_account = relationship("BrokerAccounts", back_populates="algo_schedule_time")
    algo_schedule = relationship("AlgoSchedules", back_populates="algo_schedule_time")

    __table_args__ = (
        CheckConstraint("market_date IS NOT NULL OR weekday IS NOT NULL", name="check_at_least_one_not_null"),
        UniqueConstraint('schedule', 'account_id', 'market_date', 'weekday', name='uq_schedule_time'),
        Index('idx_schedule_time', 'schedule', 'account_id', 'market_date', 'weekday'),)

    def __repr__(self):
        return (f"<AlgoScheduleTime(id={self.id}, "
                f"schedule='{self.schedule}', account_id='{self.account_id}', "
                f"market_date={self.market_date}, weekday={self.weekday}, "
                f"start_time={self.start_time}, end_time={self.end_time}, "
                f"is_market_open={self.is_market_open}, source='{self.source}', "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")


# Remove the threads relationship as it's now in the AlgoSchedules model

@event.listens_for(AlgoScheduleTime.__table__, "after_create")
def insert_default_records(target, connection, **kwargs):
    """Ensure default market hour records exist for 'GLOBAL' and weekends."""
    try:
        connection.execute(target.insert(), DEFAULT_SCHEDULE_TIME_RECORDS)
        logger.info("Default market hours inserted successfully")
    except Exception as e:
        logger.error(f"Error inserting default records: {e}")
