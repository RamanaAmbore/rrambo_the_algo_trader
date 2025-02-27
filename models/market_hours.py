from datetime import time, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, Date, Time, Boolean, String, select, event
from sqlalchemy.orm import Session

from utils.config_loader import sc
from .base import Base


class MarketHours(Base):
    __tablename__ = "market_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_date = Column(Date, unique=True, nullable=True)  # Specific date entry
    weekday = Column(String, nullable=True)  # Default weekday entry, "GLOBAL" for global default
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    is_market_open = Column(Boolean, nullable=False, default=True)  # Market open flag

    @classmethod
    def get_market_hours_for_today(cls, session: Session):
        """Retrieve market hours for today, checking date, weekday, then global default."""
        today = datetime.now(tz=ZoneInfo(sc.indian_timezone)).date()
        weekday = today.strftime("%A")

        # 1. Check specific date record
        query = select(cls).where(cls.market_date == today)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            return market_hours

        # 2. Check default weekday record
        query = select(cls).where(cls.weekday == weekday)
        result = session.execute(query)
        market_hours = result.scalars().first()
        if market_hours:
            return market_hours

        # 3. Check global default record
        query = select(cls).where(cls.weekday == "GLOBAL")
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
            global_default = cls(market_date=None, weekday="GLOBAL", start_time=default_start,
                                 end_time=default_end, is_market_open=True)
            session.add(global_default)

        # Insert default records for each weekday if missing
        for day in weekdays:
            if day not in existing_records:
                weekday_default = cls(market_date=None, weekday=day, start_time=None,
                                      end_time=None, is_market_open=False)
                session.add(weekday_default)

        session.commit()


# Automatically populate market hours when the table is created
@event.listens_for(Base.metadata, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    with Session(bind=connection) as session:
        MarketHours.set_default_market_hours(session)
