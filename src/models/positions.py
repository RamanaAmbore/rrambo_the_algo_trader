from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, ForeignKeyConstraint,
    CheckConstraint, Index, DECIMAL, func, text, UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

PRODUCT_TYPES = ("MIS", "CNC", "NRML")


class Positions(Base):
    """Model to store trading positions."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ForeignKey relationships
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50), nullable=False)  # Part of composite FK
    exchange = Column(String(20), nullable=False)  # Part of composite FK
    instrument_token = Column(Integer, nullable=False)  # Part of composite FK

    quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Current net position quantity
    overnight_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Previous day position
    buy_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Total buy quantity
    sell_quantity = Column(Integer, nullable=False, default=0, server_default="0")  # Total sell quantity
    buy_price = Column(DECIMAL(10, 2), nullable=False, default=0, server_default="0.00")  # Average buy price
    sell_price = Column(DECIMAL(10, 2), nullable=False, default=0, server_default="0.00")  # Average sell price
    buy_value = Column(DECIMAL(15, 2), nullable=False, default=0, server_default="0.00")  # Total buy value
    sell_value = Column(DECIMAL(15, 2), nullable=False, default=0, server_default="0.00")  # Total sell value
    pnl = Column(DECIMAL(12, 2), nullable=False, default=0, server_default="0.00")  # Profit/Loss
    realised = Column(DECIMAL(12, 2), nullable=False, default=0, server_default="0.00")  # Realized profit/loss
    unrealised = Column(DECIMAL(12, 2), nullable=False, default=0, server_default="0.00")  # Unrealized profit/loss
    last_price = Column(DECIMAL(10, 2), nullable=False, default=0, server_default="0.00")  # Last market price
    close_price = Column(DECIMAL(10, 2), nullable=False, default=0, server_default="0.00")  # Previous close price
    product = Column(String(10), nullable=False)  # CNC/MIS/NRML (cash, intraday, margin)
    overnight = Column(Boolean, nullable=False, default=False, server_default="false")  # True if carry forward position
    multiplier = Column(DECIMAL(5, 2), nullable=False, default=1, server_default="1.00")  # Leverage multiplier
    source = Column(String(50), nullable=False, server_default="API")

    # Timestamp fields
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))

    notes = Column(String(255), nullable=True)

    # Relationships
    broker_account = relationship("BrokerAccounts", back_populates="positions")
    stock = relationship("StockList", back_populates="positions")

    __table_args__ = (
        # Composite Foreign Key Constraint to stocklist
        ForeignKeyConstraint(
            ["tradingsymbol", "exchange"],
            ["stock_list.tradingsymbol", "stock_list.exchange"],
            ondelete="CASCADE"
        ),

        # Constraints for data integrity
        CheckConstraint(f"product IN {PRODUCT_TYPES}", name="check_valid_product"),
        CheckConstraint("multiplier > 0", name="check_multiplier_positive"),
        CheckConstraint("buy_quantity >= 0", name="check_buy_quantity_non_negative"),
        CheckConstraint("sell_quantity >= 0", name="check_sell_quantity_non_negative"),
        CheckConstraint("buy_price >= 0", name="check_buy_price_non_negative"),
        CheckConstraint("sell_price >= 0", name="check_sell_price_non_negative"),
        CheckConstraint("buy_value >= 0", name="check_buy_value_non_negative"),
        CheckConstraint("sell_value >= 0", name="check_sell_value_non_negative"),

        # Uniqueness constraints
        UniqueConstraint("tradingsymbol", "exchange", "account", name="uq_tradingsymbol_exchange_token"),


        # Indexes for faster lookups
        Index("idx_account_tradingsymbol2", "account", "tradingsymbol"),
        Index("idx_tradingsymbol_exchange2", "tradingsymbol", "exchange"),
        Index("idx_tradingsymbol2", "tradingsymbol"),
        Index("idx_instrument_token3", "instrument_token"),

    )

    def __repr__(self):
        return (f"<Positions(id={self.id}, tradingsymbol='{self.tradingsymbol}', "
                f"exchange='{self.exchange}', instrument_token={self.instrument_token}, "
                f"quantity={self.quantity}, pnl={self.pnl}, realised={self.realised}, "
                f"unrealised={self.unrealised}, source='{self.source}')>")

