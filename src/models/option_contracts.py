from decimal import Decimal, ROUND_DOWN

from sqlalchemy import (Column, Integer, String, DateTime, DECIMAL, text, ForeignKey, CheckConstraint,
                        Index, func)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


def to_decimal(value):
    """Convert float to Decimal with 2 decimal places."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class OptionContracts(Base):
    """Model to store available option contracts."""
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    instrument_token = Column(Integer, unique=True, nullable=False)
    tradingsymbol = Column(String(50), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    strike_price = Column(DECIMAL(10, 4), nullable=False)
    option_type = Column(String(10), nullable=False)
    lot_size = Column(Integer, nullable=False)
    tick_size = Column(DECIMAL(10, 4), nullable=False)
    source = Column(String(50), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    broker_accounts_rel = relationship("BrokerAccounts", back_populates="option_contracts_rel", passive_deletes=True, )

    __table_args__ = (CheckConstraint("strike_price > 0", name="check_strike_price_positive"),
                      CheckConstraint("lot_size > 0", name="check_lot_size_positive"),
                      CheckConstraint("tick_size > 0", name="check_tick_size_positive"),
                      CheckConstraint("option_type IN ('CE', 'PE')", name="check_option_type_valid"),
                      Index("idx_expiry_strike", "expiry_date", "strike_price"),
                      Index("idx_symbol2", "tradingsymbol"),)

    def __repr__(self):
        return (f"<OptionContract(id={self.id}, account='{self.account}', "
                f"instrument_token={self.instrument_token}, tradingsymbol='{self.tradingsymbol}', "
                f"expiry_date={self.expiry_date}, strike_price={self.strike_price}, "
                f"option_type='{self.option_type}', lot_size={self.lot_size}, "
                f"tick_size={self.tick_size}, source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")
