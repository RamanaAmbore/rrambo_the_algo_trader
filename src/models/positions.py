from sqlalchemy import (
    Column, String, Integer, DateTime, text, Boolean, 
    ForeignKey, Enum, Index, Numeric, CheckConstraint
)
from sqlalchemy.orm import relationship
from src.utils.date_time_utils import timestamp_indian
from src.utils.logger import get_logger
from .base import Base
from src.settings.parameter_loader import Source

logger = get_logger(__name__)

POSITION_TYPES = ["LONG", "SHORT"]
PRODUCT_TYPES = ["MIS", "CNC", "NRML"]


class Positions(Base):
    """Model to store trading positions."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    trading_symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(10), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    product = Column(String(10), nullable=False)
    position_type = Column(String(5), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    average_price = Column(Numeric(10, 2), nullable=False, default=0)
    last_price = Column(Numeric(10, 2), nullable=False, default=0)
    unrealized_pnl = Column(Numeric(12, 2), nullable=False, default=0)
    realized_pnl = Column(Numeric(12, 2), nullable=False, default=0)
    total_pnl = Column(Numeric(12, 2), nullable=False, default=0)
    multiplier = Column(Integer, nullable=False, default=1)
    margin_used = Column(Numeric(12, 2), nullable=False, default=0)
    source = Column(Enum(Source), nullable=True, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts
    broker_account = relationship("BrokerAccounts", back_populates="positions")

    __table_args__ = (
        CheckConstraint(f"position_type IN {tuple(POSITION_TYPES)}", name="check_valid_position_type"),
        CheckConstraint(f"product IN {tuple(PRODUCT_TYPES)}", name="check_valid_product"),
        CheckConstraint("multiplier > 0", name="check_multiplier_positive"),
        CheckConstraint("margin_used >= 0", name="check_margin_non_negative"),
        Index("idx_account_symbol3", "account", "trading_symbol"),
        Index("idx_instrument1", "instrument_token"),
        Index("idx_active_positions", "account", "quantity", "position_type"),
    )

    def __repr__(self):
        return (f"<Positions(id={self.id}, trading_symbol='{self.trading_symbol}', "
                f"position_type='{self.position_type}', quantity={self.quantity}, "
                f"average_price={self.average_price}, unrealized_pnl={self.unrealized_pnl}, "
                f"total_pnl={self.total_pnl}, source='{self.source}')>")