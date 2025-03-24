from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, CheckConstraint,
    Index, UniqueConstraint, func, DECIMAL, text, ForeignKeyConstraint
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class Holdings(Base):
    """Model to store portfolio holdings, structured to match Zerodha Kite API."""

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ForeignKey relationships
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50),  nullable=False)
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    instrument_token = Column(Integer, nullable=False)  # Part of composite FK

    isin = Column(String(20), nullable=True)  # Unique ISIN for stock identification
    quantity = Column(Integer, nullable=False)  # Number of shares held
    t1_quantity = Column(Integer, nullable=True, default=0)  # T1 settlement shares
    average_price = Column(DECIMAL(10, 2), nullable=False)  # Buy average price
    last_price = Column(DECIMAL(10, 2), nullable=False)  # Latest market price
    pnl = Column(DECIMAL(10, 2), nullable=True)  # Profit/Loss
    close_price = Column(DECIMAL(10, 2), nullable=True)  # Previous day close price
    collateral_quantity = Column(Integer, nullable=True, default=0)  # Pledged stocks
    collateral_type = Column(String(20), nullable=True)  # Pledge type (e.g., 'collateral')
    source = Column(String(50), nullable=False, server_default="REPORTS")

    # Timestamp fields
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))

    notes = Column(String(255), nullable=True)

    # Relationships
    broker_account = relationship("BrokerAccounts", back_populates="holdings")
    stock = relationship("StockList", back_populates="holdings")

    __table_args__ = (
        ForeignKeyConstraint(
            ["tradingsymbol", "exchange"],
            ["stock_list.tradingsymbol", "stock_list.exchange"],
            ondelete="CASCADE"
        ),
        # Constraints for data integrity
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("last_price >= 0", name="check_last_price_non_negative"),

        # Uniqueness constraints
        UniqueConstraint( "tradingsymbol", "exchange", "account", name="uq_account_tradingsymbol"),

        # Indexes for faster lookups
        Index("idx_account_tradingsymbol1", "account", "tradingsymbol"),
        Index("idx_tradingsymbol_exchange1", "tradingsymbol", "exchange"),
        Index("idx_tradingsymbol1", "tradingsymbol"),
        Index("idx_instrument_token2", "instrument_token"),
    )

    def __repr__(self):
        return (f"<Holdings(id={self.id}, account='{self.account}', "
                f"tradingsymbol='{self.tradingsymbol}', exchange='{self.exchange}', "
                f"quantity={self.quantity}, avg_price={self.average_price})>")
