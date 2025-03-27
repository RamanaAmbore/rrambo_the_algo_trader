from sqlalchemy import (
    Column, Integer, String, DateTime, text, CheckConstraint,
    Index, UniqueConstraint, func, DECIMAL, ForeignKey
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class HistoricalDataDaily(Base):
    """Model to store portfolio holdings, structured to match Zerodha Kite API."""
    __tablename__ = "historical_data_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(Integer, nullable=False, index=True)  # Stock identifier
    account = Column(String, nullable=False)  # Required for unique constraint
    tradingsymbol = Column(String, nullable=False, index=True)  # Stock symbol
    exchange = Column(String, nullable=False)  # NSE, BSE, etc.
    interval = Column(String, nullable=False)  # 'minute', 'day', etc.

    open = Column(DECIMAL(10, 4), nullable=False)
    high = Column(DECIMAL(10, 4), nullable=False)
    low = Column(DECIMAL(10, 4), nullable=False)
    close = Column(DECIMAL(10, 4), nullable=False)
    volume = Column(Integer, nullable=False)

    source = Column(String(50), nullable=False, server_default="REPORTS")
    broker_account_id = Column(Integer, ForeignKey("broker_accounts.id"), nullable=False)

    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="holdings")

    __table_args__ = (
        CheckConstraint("volume >= 0", name="check_volume_non_negative"),
        CheckConstraint("open >= 0", name="check_open_non_negative"),
        CheckConstraint("high >= 0", name="check_high_non_negative"),
        CheckConstraint("low >= 0", name="check_low_non_negative"),
        CheckConstraint("close >= 0", name="check_close_non_negative"),
        CheckConstraint("source IN ('REPORTS', 'API', 'MANUAL')", name="check_source_valid"),
        UniqueConstraint('account', 'tradingsymbol', name='uq_account_symbol1'),
        Index("idx_account_symbol1", "account", "tradingsymbol"),
        Index("idx_symbol1", "tradingsymbol"),
    )

    def __repr__(self):
        return (f"<Holdings(id={self.id}, account='{self.account}', "
                f"tradingsymbol='{self.tradingsymbol}', exchange='{self.exchange}', "
                f"open={self.open}, high={self.high}, low={self.low}, close={self.close}, "
                f"volume={self.volume})>")
