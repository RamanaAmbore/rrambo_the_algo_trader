from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DateTime, ForeignKey, Enum, CheckConstraint, Index, \
    text
from sqlalchemy.orm import relationship

from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from .model_utils import WeekdayEnum
from model_utils import source
logger = get_logger(__name__)

market = "MARKET"


# Define Weekday Enum


class AlgoSchedule(Base):
    """Stores market hours for specific dates, weekdays, and default global settings."""
    __tablename__ = "algo_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    market_date = Column(Date, unique=True, nullable=True)  # Stores specific trading day market schedule
    weekday = Column(Enum(WeekdayEnum), nullable=True)  # Enum for weekdays
    start_time = Column(Time, nullable=True)  # Market opening time
    end_time = Column(Time, nullable=True)  # Market closing time
    is_market_open = Column(Boolean, nullable=False, default=True)  # Whether the market is open
    thread_name = Column(Enum("MARKET", "BATCH", name="thread_type_enum"), nullable=False,
                         default="MARKET")  # Thread identifier
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Auto timestamps with timezone
    warning_error = Column(Boolean, nullable=False, default=False)  # Flag for any warnings/errors in scheduling
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="schedules")

    __table_args__ = (
        CheckConstraint("market_date IS NOT NULL OR weekday IS NOT NULL", name="check_at_least_one_not_null"),
        Index("idx_market_date", "market_date", unique=True),)

    def __repr__(self):
        return (f"<AlgoSchedule(id={self.id}, account_id={self.account_id}, market_date={self.market_date}, "
                f"weekday={self.weekday}, start_time={self.start_time}, end_time={self.end_time}, "
                f"is_market_open={self.is_market_open}, thread_name={self.thread_name}, source={self.source}, "
                f"warning_error={self.warning_error}, notes={self.notes})>")
