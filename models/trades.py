from sqlalchemy import Column, String, Numeric, Integer, DateTime, text, Boolean, BigInteger, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from model_utils import source
logger = get_logger(__name__)  # Initialize logger


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    trade_id = Column(BigInteger, unique=True, nullable=False, index=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    exchange = Column(String, nullable=False)
    segment = Column(String, nullable=False)
    series = Column(String, nullable=False)
    trade_type = Column(String, nullable=False)
    auction = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    order_execution_time = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    instrument_type = Column(String, nullable=False)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String, nullable=True)

    def __repr__(self):
        return f"<Trade {self.trade_id} - {self.trading_symbol} {self.trade_type} {self.quantity} @ {self.price}>"
