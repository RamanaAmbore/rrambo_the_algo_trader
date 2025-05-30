from sqlalchemy import (Column, Integer, String, Boolean, DateTime, ForeignKey, Index, text, UniqueConstraint, func,
                        select)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_SCHEDULE_TIME
from .base import Base

logger = get_logger(__name__)


class ScheduleTime(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "schedule_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(10), ForeignKey("schedule_list.schedule", ondelete="CASCADE"), nullable=False)
    exchange = Column(String(10), ForeignKey("exchange_list.exchange", ondelete="CASCADE"), nullable=False,default='*')
    market_day = Column(String(10), nullable=False,default='*')
    start_time = Column(String(5), nullable=False,default='*')
    end_time = Column(String(5), nullable=False,default='*')
    is_market_open = Column(Boolean, nullable=False, default=True)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    schedule_list_rel = relationship("ScheduleList", back_populates="schedule_time_rel", passive_deletes=True, )
    exchange_rel = relationship("ExchangeList", back_populates="schedule_time_rel", passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint('schedule', 'market_day', 'exchange', 'start_time', name='uq_schedule_time'),
        Index('idx_schedule_time', 'schedule', 'market_day', 'exchange'),)

    def __repr__(self):
        return (f"<ScheduleTime(id={self.id}, "
                f"schedule='{self.schedule}', "
                f"market_day={self.market_day}, "
                f"start_time={self.start_time}, end_time={self.end_time}, "
                f"is_market_open={self.is_market_open}, source='{self.source}', "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ScheduleTime.__table__
        for record in DEF_SCHEDULE_TIME:
            exists = connection.execute(
                select(table).where(
                    table.c.schedule == record['schedule'],
                    table.c.weekday == record['weekday'],
                    table.c.exchange == record['exchange']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Schedule Time records inserted/updated')
    except SQLAlchemyError as e:
        logger.error(f"Error managing default Schedule Time records: {e}")
        raise
