from datetime import time, datetime
from typing import Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, Date, Time, Boolean, String, select, event, DateTime, text
from sqlalchemy.orm import Session

from utils.config_loader import sc
from utils.date_time_utils import today_indian, timestamp_indian
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)

market = 'MARKET'


class AlgoSchedule(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "algo_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_date = Column(Date, unique=True, nullable=True)  # Specific date entry
    weekday = Column(String, nullable=True)  # Default weekday entry, "GLOBAL" for global default
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_market_open = Column(Boolean, nullable=True, default=True)  # Market open flag
    thread_name = Column(String, nullable=False, default=market)  # Thread handling this market session
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    def get_market_hours_for_today(cls, session: Session):
        """Retrieve market hours for today, checking date, weekday, then global default."""
        today = datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)).date()
        weekday = today.strftime("%A")

        # 1. Check specific date record
        logger.info(f"Checking for MARKET hours for {today}")
        query = select(cls).where(cls.market_date == today, cls.thread_name == market)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            logger.info(f"Successfully fetched market hours")
            return market_hours

        # 2. Check default weekday record
        logger.info(f"Checking for default day MARKET hours for {weekday}")
        query = select(cls).where(cls.weekday == weekday, cls.thread_name == market)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            return market_hours

        # 3. Check global default record
        logger.info(f"Checking for default GLOBAL MARKET hours")
        query = select(cls).where(cls.weekday == "GLOBAL", cls.thread_name == market)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            return market_hours
        logger.info(f"No record exists for default GLOBAL MARKET hours")

        return None

    @classmethod
    def get_batch_schedules(cls, session: Session, batch_type=None):
        """Retrieve market hours for today, checking date, weekday, then global default."""
        today = today_indian()

        if not isinstance(batch_type, Iterable):
            batch_type = (batch_type,)

        logger.info(f"Checking batch schedules of type {batch_type} for {today}")
        if batch_type is None:
            query = select(cls).where(cls.market_date == today, cls.thread_name != market)
        else:
            query = select(cls).where(cls.market_date == today, cls.thread_name.in_(batch_type))

        result = session.execute(query)
        schedules = result.scalars()
        if schedules:
            logger.info(f"Successfully fetched schedules of {batch_type} for {today}")
            return schedules
        logger.info(f"No batch schedules exist of {batch_type} for {today}")
        return None

    @classmethod
    def set_default_schedules(cls, session: Session):
        """Ensure default market hour records exist for GLOBAL and weekends."""

        # Define default records as a list of tuples
        default_records = [("GLOBAL", "MARKET", time(9, 0), time(9, 0), True),  # GLOBAL entry
                           ("Saturday", "MARKET", None, None, False),  # Saturday entry
                           ("Sunday", "MARKET", None, None, False),  # Sunday entry
                           ]

        # Fetch existing weekdays from the database
        existing_defaults = session.execute(select(cls.weekday)).scalars().all()  # FIX: Use scalars().all()
        existing_records = set(existing_defaults)

        # Prepare records that need to be inserted
        new_entries = [cls(weekday=weekday, thread_name=thread_name, start_time=start_time, end_time=end_time,
                           is_market_open=is_market_open, market_date=None) for
                       weekday, thread_name, start_time, end_time, is_market_open in default_records if
                       weekday not in existing_records]

        # Insert only missing records
        if new_entries:
            session.add_all(new_entries)
            session.commit()
            logger.info(
                f"Inserted default market hours for: {', '.join([f'{entry.weekday} {entry.thread_name}' for entry in new_entries])}")


# Automatically populate market hours when the table is created
@event.listens_for(Base.metadata, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    with Session(bind=connection) as session:
        AlgoSchedule.set_default_schedules(session)
