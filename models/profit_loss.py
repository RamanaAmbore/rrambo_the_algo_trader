from sqlalchemy import Column, String, Numeric, Integer, DateTime, text, Boolean, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    buy_value = Column(Numeric(12, 2), nullable=False)
    sell_value = Column(Numeric(12, 2), nullable=False)
    realized_pnl = Column(Numeric(12, 2), nullable=False)
    realized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    previous_closing_price = Column(Numeric(10, 2), nullable=True)
    open_quantity = Column(Integer, nullable=False, default=0)
    open_quantity_type = Column(String, nullable=False)
    open_value = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
