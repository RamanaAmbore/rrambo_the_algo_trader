from datetime import time, datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Integer, Date, Time, Boolean, String, select, event, DateTime
from sqlalchemy.orm import Session
from utils.config_loader import sc
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
    is_market_open = Column(Boolean, nullable=False, default=True)  # Market open flag
    thread_name = Column(String, nullable=False, default=market)  # Thread handling this market session
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))

    @classmethod
    def get_market_hours_for_today(cls, session: Session):
        """Retrieve market hours for today, checking date, weekday, then global default."""
        today = datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)).date()
        weekday = today.strftime("%A")

        # 1. Check specific date record
        logger.info(f"Checking MARKET hours for {today}")
        query = select(cls).where(cls.market_date == today, cls.thread_name == market)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            logger.info(f"Successfully fetched market hours")
            return market_hours

        # 2. Check default weekday record
        logger.info(f"Checking default day MARKET hours for {weekday}")
        query = select(cls).where(cls.weekday == weekday, cls.thread_name == market)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            return market_hours

        # 3. Check global default record
        logger.info(f"Checking default GLOBAL MARKET hours for {today}")
        query = select(cls).where(cls.weekday == "GLOBAL", cls.thread_name == market)
        result = session.execute(query)
        return result.scalars().first()

    @classmethod
    def set_default_market_hours(cls, session: Session):
        """Ensure default market hour records exist for GLOBAL and weekends."""

        # Define default records as a list of tuples
        default_records = [
            ("GLOBAL", "MARKET", time(9, 0), time(9, 0), True),  # GLOBAL entry
            ("Saturday", "MARKET", None, None, False),  # Saturday entry
            ("Sunday", "MARKET", None, None, False),  # Sunday entry
            ("GLOBAL", "BATCH", time(16, 0), None, True),  # GLOBAL entry
            ("Saturday", "BATCH", None, None, False),  # Saturday entry
            ("Sunday", "BATCH", None, None, False),  # Sunday entry

        ]

        # Fetch existing weekdays from the database
        existing_defaults = session.execute(select(cls.weekday))
        existing_records = {row[0] for row in existing_defaults.fetchall()}

        # Prepare records that need to be inserted
        new_entries = [
            cls(
                weekday=weekday, thread_name=thread_name,
                start_time=start_time, end_time=end_time,
                is_market_open=is_market_open, market_date=None
            )
            for weekday, thread_name, start_time, end_time, is_market_open in default_records
            if weekday not in existing_records
        ]

        # Insert only missing records
        if new_entries:
            session.add_all(new_entries)
            session.commit()
            logger.info(f"Inserted default market hours for: {', '.join([f'{entry.weekday} {entry.thread_name}'  for entry in new_entries])}")

        session.commit()


# Automatically populate market hours when the table is created
@event.listens_for(Base.metadata, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    with Session(bind=connection) as session:
        AlgoSchedule.set_default_market_hours(session)
