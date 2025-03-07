from sqlalchemy import Column, String, DateTime, text, Boolean, ForeignKey, Enum
from sqlalchemy import Date

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

# Define Stock List Table
class StockList(Base):
    __tablename__ = "stock_list"
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    symbol = Column(String, primary_key=True)
    name = Column(String)
    yahoo_ticker = Column(String)
    exchange = Column(String)
    last_updated = Column(Date)
    source = Column(Enum(source), nullable=True, server_default="API")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
