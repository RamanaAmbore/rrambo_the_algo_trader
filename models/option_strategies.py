from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, JSON, Boolean, text, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class OptionStrategies(Base):
    """Model to store option trading strategies and their risk-reward parameters."""
    __tablename__ = "option_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    strategy_name = Column(String, nullable=False)
    legs = Column(JSON, nullable=False)  # JSON format: [{"symbol": "NIFTY 18500 CE", "qty": -1}, {...}]
    max_profit = Column(DECIMAL(12, 2), nullable=True)  # 2 decimal precision for money values
    max_loss = Column(DECIMAL(12, 2), nullable=True)
    breakeven_points = Column(JSON, nullable=True)  # List of breakeven points
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        return f"<OptionStrategy {self.strategy_name} | Max PnL: {self.max_profit} | Max Loss: {self.max_loss}>"
