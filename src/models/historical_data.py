from sqlalchemy import (Column, Integer, String, DateTime, text, CheckConstraint,
                        Index, UniqueConstraint, func, Decimal)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class Holdings(Base):
    """Model to store portfolio holdings, structured to match Zerodha Kite API."""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(Integer, nullable=False, index=True)  # Stock identifier
    timestamp = Column(DateTime, nullable=False, index=True)  # Candle timestamp
    interval = Column(String, nullable=False)  # 'minute', 'day', etc.
    open = Column(Decimal(10, 2), nullable=False)
    high = Column(Decimal(10, 2), nullable=False)
    low = Column(Decimal(10, 2), nullable=False)
    close = Column(Decimal(10, 2), nullable=False)
    volume = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="holdings")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("current_price >= 0", name="check_current_price_non_negative"),
        UniqueConstraint('account', 'tradingsymbol', name='uq_account_symbol1'),
        Index("idx_account_symbol", "account", "tradingsymbol"),
        Index("idx_symbol1", "tradingsymbol"),
    )

    def __repr__(self):
        return (f"<Holdings(id={self.id}, account='{self.account}', "
                f"tradingsymbol='{self.tradingsymbol}', exchange='{self.exchange}', "
                f"quantity={self.quantity}, avg_price={self.average_price})>")