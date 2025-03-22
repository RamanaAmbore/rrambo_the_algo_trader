from sqlalchemy import (Column, Integer, String, DateTime, text, ForeignKey, CheckConstraint,
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
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50), nullable=False)  # Stock tradingsymbol
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    isin = Column(String(20), nullable=True)  # Unique ISIN for stock identification
    quantity = Column(Integer, nullable=False)  # Number of shares held
    t1_quantity = Column(Integer, nullable=True)  # Shares in T1 settlement (not yet delivered)
    average_price = Column(Decimal(10, 2), nullable=False)  # Buy average price
    last_price = Column(Decimal(10, 2), nullable=False)  # Latest market price
    pnl = Column(Decimal(10, 2), nullable=True)  # Profit/Loss
    close_price = Column(Decimal(10, 2), nullable=True)  # Previous day close price
    collateral_quantity = Column(Integer, nullable=True, default=0)  # Pledged stocks
    collateral_type = Column(String(20), nullable=True)  # Pledge type (e.g., 'collateral')
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
