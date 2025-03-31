from sqlalchemy import (
    Column, Integer, DateTime, DECIMAL, ForeignKey, text,
    String, CheckConstraint, Index, func
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class OptionGreeks(Base):
    """Model to store option Greeks such as Delta, Theta, Vega, Gamma, and IV."""
    __tablename__ = "option_greeks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    instrument_token = Column(Integer, ForeignKey("option_contracts.instrument_token", ondelete="CASCADE"),
                              nullable=False)
    delta = Column(DECIMAL(10, 4), nullable=True)  # Higher precision for Greeks
    theta = Column(DECIMAL(10, 4), nullable=True)
    vega = Column(DECIMAL(10, 4), nullable=True)
    gamma = Column(DECIMAL(10, 4), nullable=True)
    iv = Column(DECIMAL(10, 4), nullable=True)  # IV typically has 2 decimal places
    source = Column(String(50), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    broker_account = relationship("BrokerAccounts", back_populates="option_greeks")
    option_contract = relationship("OptionContracts", back_populates="option_greeks")

    __table_args__ = (
        CheckConstraint("delta BETWEEN -1 AND 1", name="check_delta_range"),
        CheckConstraint("gamma >= 0", name="check_gamma_positive"),
        CheckConstraint("iv >= 0", name="check_iv_positive"),
        Index("idx_instrument_timestamp", "instrument_token", "timestamp"),
    )

    def __repr__(self):
        return (f"<OptionGreeks(id={self.id}, account='{self.account}', "
                f"instrument_token={self.instrument_token}, delta={self.delta}, "
                f"theta={self.theta}, vega={self.vega}, gamma={self.gamma}, "
                f"iv={self.iv}, source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")
