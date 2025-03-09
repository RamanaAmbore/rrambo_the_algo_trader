from decimal import Decimal, ROUND_DOWN
from sqlalchemy import (Column, Integer, String, DateTime, DECIMAL, text, Boolean, ForeignKey, Enum, CheckConstraint,
                        Index)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.load_db_parms import source

logger = get_logger(__name__)


def to_decimal(value):
    """Convert float to Decimal with 2 decimal places."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class OptionContracts(Base):
    """Model to store available option contracts."""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    instrument_token = Column(Integer, unique=True, nullable=False)
    trading_symbol = Column(String(20), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    strike_price = Column(DECIMAL(10, 2), nullable=False)
    option_type = Column(String(10), nullable=False)
    lot_size = Column(Integer, nullable=False)
    tick_size = Column(DECIMAL(10, 2), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    option_greeks = relationship("OptionGreeks", back_populates="option_contract")
    broker_account = relationship("BrokerAccounts", back_populates="option_contracts")

    __table_args__ = (CheckConstraint("strike_price > 0", name="check_strike_price_positive"),
                      CheckConstraint("lot_size > 0", name="check_lot_size_positive"),
                      CheckConstraint("tick_size > 0", name="check_tick_size_positive"),
                      CheckConstraint("option_type IN ('CE', 'PE')", name="check_option_type_valid"),
                      Index("idx_expiry_strike", "expiry_date", "strike_price"),
                      Index("idx_trading_symbol2", "trading_symbol"),)

    def __repr__(self):
        return (f"<OptionContract(id={self.id}, account='{self.account}', "
                f"instrument_token={self.instrument_token}, trading_symbol='{self.trading_symbol}', "
                f"expiry_date={self.expiry_date}, strike_price={self.strike_price}, "
                f"option_type='{self.option_type}', lot_size={self.lot_size}, "
                f"tick_size={self.tick_size}, source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")
