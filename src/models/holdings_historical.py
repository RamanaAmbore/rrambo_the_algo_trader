from sqlalchemy import (Column, Integer, String, DateTime, text, ForeignKey, CheckConstraint,
                        Index, UniqueConstraint, func, DECIMAL)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class HoldingsHistorical(Base):
    """Model to store historical portfolio holdings, structured to match Zerodha Kite API."""
    __tablename__ = "holdings_historical"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False)
    tradingsymbol = Column(String(50), nullable=False)  # Stock tradingsymbol
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    isin = Column(String(20), nullable=True)  # Unique ISIN for stock identification
    quantity = Column(Integer, nullable=False)  # Number of shares held
    t1_quantity = Column(Integer, nullable=True)  # Shares in T1 settlement (not yet delivered)
    average_price = Column(DECIMAL(10, 2), nullable=False)  # Buy average price
    last_price = Column(DECIMAL(10, 2), nullable=False)  # Latest market price
    pnl = Column(DECIMAL(10, 2), nullable=True)  # Profit/Loss
    close_price = Column(DECIMAL(10, 2), nullable=True)  # Previous day close price
    collateral_quantity = Column(Integer, nullable=True, server_default=text("0"))  # Pledged stocks
    collateral_type = Column(String(20), nullable=True)  # Pledge type (e.g., 'collateral')
    source = Column(String(50), nullable=False, server_default="REPORTS")
    date = Column(DateTime(timezone=True), nullable=False)  # Historical record date
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="holdings_historical")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("last_price >= 0", name="check_last_price_non_negative"),
        UniqueConstraint('account', 'tradingsymbol', 'date', name='uq_account_symbol_date'),
        Index("idx_account_symbol_date", "account", "tradingsymbol", "date"),
    )

    def __repr__(self):
        return (f"<HoldingsHistorical(id={self.id}, account='{self.account}', "
                f"tradingsymbol='{self.tradingsymbol}', exchange='{self.exchange}', "
                f"date={self.date}, quantity={self.quantity}, avg_price={self.average_price})>")
