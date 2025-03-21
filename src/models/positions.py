from sqlalchemy import (
    Column, String, Integer, DateTime, text, Boolean,
    ForeignKey, Index, Decimal, CheckConstraint, func
)
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

PRODUCT_TYPES = ["MIS", "CNC", "NRML"]


class Positions(Base):
    """Model to store trading positions."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50), nullable=False)  # Stock symbol
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    instrument_token = Column(Integer, nullable=False)  # Unique instrument identifier
    quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Current net position quantity
    overnight_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Previous day position
    buy_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Total buy quantity
    sell_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Total sell quantity
    buy_price = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Average buy price
    sell_price = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Average sell price
    buy_value = Column(Decimal(15, 2), nullable=False, default=0.00, server_default="0.00")  # Total buy value
    sell_value = Column(Decimal(15, 2), nullable=False, default=0.00, server_default="0.00")  # Total sell value
    pnl = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Profit/Loss
    realised = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Realized profit/loss
    unrealised = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Unrealized profit/loss
    last_price = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Last market price
    close_price = Column(Decimal(10, 2), nullable=False, default=0.00, server_default="0.00")  # Previous close price
    product = Column(String(20), nullable=False)  # CNC/MIS/NRML (cash, intraday, margin)
    overnight = Column(Boolean, nullable=False, default=False, server_default="false")  # True if carry forward position
    multiplier = Column(Decimal(10, 2), nullable=False, default=1.00, server_default="1.00")  # Leverage multiplier
    source = Column(String(50), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts
    broker_account = relationship("BrokerAccounts", back_populates="positions")

    __table_args__ = (
        CheckConstraint(f"product IN {tuple(PRODUCT_TYPES)}", name="check_valid_product"),
        CheckConstraint("multiplier > 0", name="check_multiplier_positive"),
        Index("idx_account_symbol", "account", "tradingsymbol"),
        Index("idx_instrument", "instrument_token"),
    )

    def __repr__(self):
        return (f"<Positions(id={self.id}, tradingsymbol='{self.tradingsymbol}', "
                f"quantity={self.quantity}, pnl={self.pnl}, "
                f"realised={self.realised}, unrealised={self.unrealised}, source='{self.source}')>")
