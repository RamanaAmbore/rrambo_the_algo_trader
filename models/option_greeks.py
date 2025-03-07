from sqlalchemy import Column, Integer, DateTime, DECIMAL, ForeignKey, text, String, Boolean, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class OptionGreeks(Base):
    """Model to store option Greeks such as Delta, Theta, Vega, Gamma, and IV."""
    __tablename__ = "option_greeks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    instrument_token = Column(Integer, ForeignKey("option_contracts.instrument_token", ondelete="CASCADE"),
                              nullable=False)
    delta = Column(DECIMAL(10, 4), nullable=True)  # Higher precision for Greeks
    theta = Column(DECIMAL(10, 4), nullable=True)
    vega = Column(DECIMAL(10, 4), nullable=True)
    gamma = Column(DECIMAL(10, 4), nullable=True)
    iv = Column(DECIMAL(10, 2), nullable=True)  # IV typically has 2 decimal places
    source = Column(Enum(source), nullable=True, server_default="API")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        return f"<OptionGreek Token: {self.instrument_token} | Δ: {self.delta} | IV: {self.iv}>"
