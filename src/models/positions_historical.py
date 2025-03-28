from sqlalchemy import (Column, Integer, String, DateTime, Boolean, ForeignKey, Index, DECIMAL, text)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

PRODUCT_TYPES = ("MIS", "CNC", "NRML")


class PositionsHistorical(Base):
    """Model to store historical trading positions."""
    __tablename__ = "positions_historical"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False)
    tradingsymbol = Column(String(50), nullable=False)  # Stock symbol
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    instrument_token = Column(Integer, nullable=False)  # Unique instrument identifier
    quantity = Column(Integer, nullable=False, default=0, server_default="0")
    overnight_quantity = Column(Integer, nullable=False, default=0, server_default="0")
    buy_quantity = Column(Integer, nullable=False, default=0, server_default="0")
    sell_quantity = Column(Integer, nullable=False, default=0, server_default="0")
    buy_price = Column(DECIMAL(10, 4), nullable=False, default=0, server_default="0.00")
    sell_price = Column(DECIMAL(10, 4), nullable=False, default=0, server_default="0.00")
    buy_value = Column(DECIMAL(15, 4), nullable=False, default=0, server_default="0.00")
    sell_value = Column(DECIMAL(15, 4), nullable=False, default=0, server_default="0.00")
    pnl = Column(DECIMAL(12, 4), nullable=False, default=0, server_default="0.00")
    realised = Column(DECIMAL(12, 4), nullable=False, default=0, server_default="0.00")
    unrealised = Column(DECIMAL(12, 4), nullable=False, default=0, server_default="0.00")
    last_price = Column(DECIMAL(10, 4), nullable=False, default=0, server_default="0.00")
    close_price = Column(DECIMAL(10, 4), nullable=False, default=0, server_default="0.00")
    product = Column(String(10), nullable=False)
    overnight = Column(Boolean, nullable=False, default=False, server_default="false")
    multiplier = Column(DECIMAL(5, 4), nullable=False, default=1, server_default="1.00")
    source = Column(String(50), nullable=False, server_default="API")
    date = Column(DateTime(timezone=True), nullable=False)  # Historical record date
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    broker_account = relationship("BrokerAccounts", back_populates="positions_historical")

    __table_args__ = (
        Index("idx_account_symbol_date", "account", "tradingsymbol", "date"),
    )

    def __repr__(self):
        return (f"<PositionsHistorical(id={self.id}, tradingsymbol='{self.tradingsymbol}', "
                f"quantity={self.quantity}, date={self.date}, pnl={self.pnl}, source='{self.source}')>")
