from datetime import time, datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Integer, Date, Time, Boolean, String, select, event, DateTime
from sqlalchemy.orm import Session
from utils.config_loader import sc
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)

market = 'MARKET'
class MarketHours(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "market_hours"

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
        """Ensure default market hour records exist for global and weekdays."""
        default_start = time(9, 15)
        default_end = time(15, 30)
        weekdays = ["Saturday", "Sunday"]

        existing_defaults = session.execute(select(cls))
        existing_records = {row.weekday for row in existing_defaults.scalars().all()}

        # Insert global default if not exists
        if "GLOBAL" not in existing_records:
            logger.info("Successfully fetched default (GLOBAL) market hours")
            global_default = cls(
                market_date=None, weekday="GLOBAL", start_time=default_start,
                end_time=default_end, is_market_open=True, thread_name=market
            )
            session.add(global_default)

        # Insert default records for each weekday if missing
        for day in weekdays:
            if day not in existing_records:
                weekday_default = cls(
                    market_date=None, weekday=day, start_time=None,
                    end_time=None, is_market_open=False, thread_name=market
                )
                session.add(weekday_default)
                logger.info(f"Fetching default market hours for {day}")
                break

        session.commit()


# Automatically populate market hours when the table is created
@event.listens_for(Base.metadata, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    with Session(bind=connection) as session:
        MarketHours.set_default_market_hours(session)
