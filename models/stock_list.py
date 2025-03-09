from sqlalchemy import (
    Column, String, Integer, DateTime, text, Boolean, 
    ForeignKey, Enum, Index, Numeric
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.load_db_parms import source

logger = get_logger(__name__)


class StockList(Base):
    """Model to store stock listing information."""
    __tablename__ = "stock_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    trading_symbol = Column(String(20), nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    exchange = Column(String(10), nullable=False)  # NSE/BSE
    isin = Column(String(12), nullable=True)
    lot_size = Column(Integer, nullable=False, default=1)
    tick_size = Column(Numeric(10, 2), nullable=False, default=0.05)
    expiry = Column(DateTime(timezone=True), nullable=True)  # For F&O instruments
    strike_price = Column(Numeric(10, 2), nullable=True)  # For options
    is_tradable = Column(Boolean, nullable=False, default=True)
    source = Column(Enum(source), nullable=True, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="stock_list")

    __table_args__ = (
        Index("idx_trading_symbol6", "trading_symbol"),
        Index("idx_instrument_token", "instrument_token"),
        Index("idx_account_symbol1", "account", "trading_symbol"),
    )

    def __repr__(self):
        return (f"<StockList(id={self.id}, trading_symbol='{self.trading_symbol}', "
                f"instrument_token={self.instrument_token}, exchange='{self.exchange}', "
                f"lot_size={self.lot_size}, is_tradable={self.is_tradable}, "
                f"source='{self.source}', timestamp={self.timestamp})>")
