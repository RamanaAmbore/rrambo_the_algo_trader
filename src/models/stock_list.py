from sqlalchemy import (
    Column, String, Integer, DateTime, Date, DECIMAL, text, Index, UniqueConstraint, func
)
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

class StockList(Base):
    """Model to store stock listing information."""
    __tablename__ = "stock_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tradingsymbol = Column(String(50), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    exchange_token = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False)
    segment = Column(String(50), nullable=False)
    instrument_type = Column(String(50), nullable=False)
    exchange = Column(String(10), nullable=False)  # NSE/BSE
    lot_size = Column(Integer, nullable=False, server_default=text("1"))
    last_price = Column(DECIMAL(10, 2), nullable=True)  # For options
    tick_size = Column(DECIMAL(10, 4), nullable=False, server_default=text("0.05"))
    expiry = Column(String(10), nullable=True)  # Converted from String to Date
    strike = Column(DECIMAL(10, 2), nullable=True)  # For options
    source = Column(String(50), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("tradingsymbol", "instrument_token", "exchange", name="uq_stock_list"),
        UniqueConstraint("tradingsymbol", name="uq_tradingsymbol"),
        UniqueConstraint("instrument_token", name="uq_instrument_token"),
        Index("idx_tradingsymbol", "tradingsymbol"),
        Index("idx_instrument_token", "instrument_token"),
    )

    def __repr__(self):
        return (f"<StockList(id={self.id}, tradingsymbol='{self.tradingsymbol}', "
                f"instrument_token={self.instrument_token}, exchange='{self.exchange}', "
                f"lot_size={self.lot_size}, source='{self.source}', timestamp={self.timestamp})>")

