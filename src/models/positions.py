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
    tradingsymbol = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)  # NSE/BSE/MCX
    instrument_token = Column(Integer, nullable=False)  # Part of composite FK

    product = Column(String(10), nullable=False, default="NRML")  # NRML/MIS/CNC

    quantity = Column(Integer, nullable=False, default=0)  # Net position
    average_price = Column(DECIMAL(10, 2), nullable=False)  # Average buy price
    last_price = Column(DECIMAL(10, 2), nullable=False)  # Current market price
    close_price = Column(DECIMAL(10, 2), nullable=False)  # Previous close price
    pnl = Column(DECIMAL(10, 2), nullable=True)  # Total profit/loss
    m2m = Column(DECIMAL(10, 2), nullable=False, default=0)  # Mark-to-market P&L
    realised = Column(DECIMAL(10, 2), nullable=False, default=0)  # Realized P&L
    unrealised = Column(DECIMAL(10, 2), nullable=False, default=0)  # Unrealized P&L
    multiplier = Column(Integer, nullable=False, default=1)  # Lot size multiplier

    # Buy-related fields
    buy_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Average buy price
    buy_quantity = Column(Integer, nullable=False, default=0)  # Total buy quantity
    buy_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Total buy value
    buy_m2m = Column(DECIMAL(10, 2), nullable=False, default=0)  # Buy M2M P&L

    # Sell-related fields
    sell_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Average sell price
    sell_quantity = Column(Integer, nullable=False, default=0)  # Total sell quantity
    sell_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Total sell value
    sell_m2m = Column(DECIMAL(10, 2), nullable=False, default=0)  # Sell M2M P&L

    # Intraday trade details
    day_buy_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Today's buy price
    day_buy_quantity = Column(Integer, nullable=False, default=0)  # Today's buy quantity
    day_buy_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Today's buy value
    day_sell_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Today's sell price
    day_sell_quantity = Column(Integer, nullable=False, default=0)  # Today's sell quantity
    day_sell_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Today's sell value

    # Carry forward position details
    overnight_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Yesterday's price
    overnight_quantity = Column(Integer, nullable=False, default=0)  # Yesterday's quantity
    overnight_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Yesterday's value

    # Total value
    value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Total position value
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

