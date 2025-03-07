from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, text, Boolean, ForeignKey, Enum
from model_utils import source
from utils.date_time_utils import timestamp_indian
from .base import Base


def to_decimal(value):
    """Convert float to Decimal with 2 decimal places."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class OptionContracts(Base):
    """Model to store available option contracts."""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    instrument_token = Column(Integer, unique=True, nullable=False)
    trading_symbol = Column(String(20), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    strike_price = Column(DECIMAL(10, 2), nullable=False)  # 2 decimal places for precision
    option_type = Column(String(10), nullable=False)  # CE (Call) / PE (Put)
    lot_size = Column(Integer, nullable=False)
    tick_size = Column(DECIMAL(10, 2), nullable=False)  # Tick size needs exact precision
    source = Column(Enum(source), nullable=True, server_default="API")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        return f"<OptionContract {self.trading_symbol} | {self.option_type} | Strike {self.strike_price}>"
