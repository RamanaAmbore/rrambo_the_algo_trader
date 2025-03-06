from datetime import time, datetime
from typing import Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, Date, Time, Boolean, String, select, event, DateTime, text
from sqlalchemy.orm import Session

from utils.date_time_utils import today_indian, timestamp_indian
from utils.logger import get_logger
from utils.settings_loader import sc, Env
from .base import Base

logger = get_logger(__name__)

market = 'MARKET'


class AlgoSchedule(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "algo_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)  # Defaulting to current user
    market_date = Column(Date, unique=True, nullable=True)  # Stores specific trading day market schedule
    weekday = Column(String, nullable=True)  # Stores general weekday schedule (e.g., "Monday")
    start_time = Column(Time, nullable=True)  # Market opening time
    end_time = Column(Time, nullable=True)  # Market closing time
    is_market_open = Column(Boolean, nullable=True, default=True)  # Whether the market is open
    thread_name = Column(String, nullable=False, default=market)  # Thread identifier (MARKET or batch jobs)
    source = Column(String, nullable=True, default="MANUAL")  # Origin of the schedule entry
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Auto timestamps with timezone
    warning_error = Column(Boolean, default=False)  # Flag for any warnings/errors in scheduling
    msg = Column(String, nullable=True)  # Optional message field for additional info

    @classmethod
    def get_market_hours_for_today(cls, session: Session, account_id=Env.ZERODHA_USERNAME):
        """Retrieve today's market hours with a fallback mechanism.

        Search order:
        1. Specific market_date entry for given account_id.
        2. Specific market_date entry for a global (NULL) account.
        3. Default weekday entry for given account_id.
        4. Default weekday entry for a global (NULL) account.
        5. Global default schedule.
        """

        today = datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)).date()
        weekday = today.strftime("%A")

        for acc_id in [account_id, None]:  # Try account-specific first, then global

            logger.info(f"Checking for MARKET hours for {today} with acc_id {acc_id}")
            if acc_id is None:
                query = select(cls).where(cls.market_date == today, cls.thread_name == market, cls.account_id.is_(None))
            else:
                query = select(cls).where(cls.market_date == today, cls.thread_name == market, cls.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours  # Return if found

            logger.info(f"Checking default weekday MARKET hours for {weekday} with acc_id {acc_id}")
            if acc_id is None:
                query = select(cls).where(cls.weekday == weekday, cls.thread_name == market, cls.account_id.is_(None))
            else:
                query = select(cls).where(cls.weekday == weekday, cls.thread_name == market, cls.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking for GLOBAL default MARKET hours with acc_id {acc_id}")
            if acc_id is None:
                query = select(cls).where(cls.weekday == "GLOBAL", cls.thread_name == market, cls.account_id.is_(None))
            else:
                query = select(cls).where(cls.weekday == "GLOBAL", cls.thread_name == market, cls.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

        return None  # Return None if no matching schedule is found

    @classmethod
    def get_batch_schedules(cls, session: Session, account_id=Env.ZERODHA_USERNAME, batch_type=None):
        """Retrieve today's batch processing schedules.

        - Tries fetching schedules for the specific account_id first.
        - Falls back to schedules with account_id = NULL.
        - Supports filtering by batch_type.
        """
        today = today_indian()
        if not isinstance(batch_type, Iterable):
            batch_type = (batch_type,)

        for acc_id in [account_id, None]:
            logger.info(f"Checking batch schedules of type {batch_type} for {today} with account_id {acc_id}")

            if acc_id is None:
                query = select(cls).where(cls.market_date == today, cls.thread_name != market, cls.account_id.is_(None))
            else:
                query = select(cls).where(cls.market_date == today, cls.thread_name != market, cls.account_id == acc_id)

            if batch_type:
                query = query.where(cls.thread_name.in_(batch_type))

            schedules = session.execute(query).scalars().all()
            if schedules:
                return schedules  # Return found schedules

        logger.info(f"No batch schedules found for {batch_type} on {today}")
        return None

    @classmethod
    def set_default_schedules(cls, session: Session):
        """Ensure default market hour records exist for 'GLOBAL' and weekends.

        - Creates a GLOBAL default schedule (09:00 - 15:30).
        - Marks Saturday and Sunday as closed.
        - Prevents duplicate default entries.
        """

        default_records = [("GLOBAL", "MARKET", time(9, 0), time(15, 30), True),
                           ("Saturday", "MARKET", None, None, False), ("Sunday", "MARKET", None, None, False), ]

        existing_defaults = session.execute(select(cls.weekday)).scalars().all()
        existing_records = set(existing_defaults)

        new_entries = [
            cls(account_id=None, weekday=weekday, thread_name=thread_name, start_time=start_time, end_time=end_time,
                is_market_open=is_market_open, market_date=None) for
            weekday, thread_name, start_time, end_time, is_market_open in default_records if
            weekday not in existing_records]

        if new_entries:
            session.add_all(new_entries)
            session.commit()
            logger.info(
                f"Inserted default market hours for: {', '.join([f'{entry.weekday} {entry.thread_name}' for entry in new_entries])}")


@event.listens_for(Base.metadata, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    """Event listener to initialize default market hours after table creation."""
    with Session(bind=connection) as session:
        AlgoSchedule.set_default_schedules(session)
