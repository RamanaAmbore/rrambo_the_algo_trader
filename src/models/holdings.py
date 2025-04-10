from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Index, UniqueConstraint, func, DECIMAL, text, ForeignKeyConstraint,
    Boolean, CheckConstraint, event
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.parameter_manager import parms
from .base import Base

logger = get_logger(__name__)


class Holdings(Base):
    """Model to store portfolio holdings, structured to match Zerodha Kite API."""

    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key relationships
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False,
                     default=parms.DEF_ACCOUNT)
    tradingsymbol = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)  # NSE/BSE
    instrument_token = Column(Integer, nullable=False)  # Part of composite FK

    symbol_exchange = Column(String(50), nullable=True)

    isin = Column(String(20), nullable=True, unique=True)  # Unique ISIN for stock identification

    quantity = Column(Integer, nullable=False, default=0)  # Number of shares held
    t1_quantity = Column(Integer, nullable=False, default=0)  # T1 settlement shares
    average_price = Column(DECIMAL(10, 4), nullable=False, default=0)  # Buy average price
    last_price = Column(DECIMAL(10, 4), nullable=False, default=0)  # Latest market price
    pnl = Column(DECIMAL(10, 4), nullable=True)  # Profit/Loss
    close_price = Column(DECIMAL(10, 4), nullable=True)  # Previous day close price
    collateral_quantity = Column(Integer, nullable=False, default=0)  # Pledged stocks
    collateral_type = Column(String(20), nullable=False)  # Pledge type (e.g., 'collateral')

    # New fields from API
    authorised_date = Column(String(23), nullable=True)  # Date when collateral was approved
    authorised_quantity = Column(Integer, nullable=False, default=0)  # Authorized pledge quantity
    day_change = Column(DECIMAL(10, 4), nullable=False, default=0)  # Change in price today
    day_change_percentage = Column(DECIMAL(10, 6), nullable=False, default=0)  # % change today
    discrepancy = Column(Boolean, nullable=False, default=False)  # If there’s a mismatch
    opening_quantity = Column(Integer, nullable=False, default=0)  # Quantity at the start of the day
    realised_quantity = Column(Integer, nullable=False, default=0)  # Realized quantity
    short_quantity = Column(Integer, nullable=False, default=0)  # Shorted stocks
    used_quantity = Column(Integer, nullable=False, default=0)  # Used collateral quantity
    product = Column(String(10), nullable=False, default="CNC")  # Holding type (e.g., CNC)
    price = Column(DECIMAL(10, 4), nullable=False, default=0)  # Trade price

    # Margin Trading Facility (MTF) Fields
    mtf_average_price = Column(DECIMAL(10, 4), nullable=False, default=0)
    mtf_initial_margin = Column(DECIMAL(10, 4), nullable=False, default=0)
    mtf_quantity = Column(Integer, nullable=False, default=0)
    mtf_used_quantity = Column(Integer, nullable=False, default=0)
    mtf_value = Column(DECIMAL(10, 4), nullable=False, default=0)

    source = Column(String(50), nullable=False, server_default="REPORTS")

    # Timestamp fields
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))

    notes = Column(String(255), nullable=True)

    # Relationships
    broker_accounts_rel = relationship("BrokerAccounts", back_populates="holdings_rel", passive_deletes=True, )
    instrument_list_rel = relationship("InstrumentList", back_populates="holdings_rel", passive_deletes=True, )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tradingsymbol", "exchange"],
            ["instrument_list.tradingsymbol", "instrument_list.exchange"],
            ondelete="CASCADE"
        ),
        # Constraints for data integrity
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("used_quantity >= 0", name="check_used_quantity_non_negative"),
        CheckConstraint("t1_quantity >= 0", name="check_t1_quantity_non_negative"),
        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("last_price >= 0", name="check_last_price_non_negative"),
        CheckConstraint("short_quantity <= quantity", name="check_short_quantity_consistency"),

        # Allowing positive and negative price changes
        CheckConstraint("day_change_percentage >= -100.0 AND day_change_percentage <= 100.0",
                        name="check_day_change_pct_range"),

        # Uniqueness constraints
        UniqueConstraint("tradingsymbol", "exchange", "account", name="uq_account_tradingsymbol5"),
        UniqueConstraint("isin", name="uq_isin"),

        # Indexes for faster lookups
        Index(", 4)", "account", "tradingsymbol"),
        Index("idx_tradingsymbol_exchange2", "tradingsymbol", "exchange"),
        Index("idx_tradingsymbol", "tradingsymbol"),
        Index("idx_instrument_token2", "instrument_token"),
    )

    def __repr__(self):
        return (f"<Holdings(id={self.id}, account='{self.account}', tradingsymbol='{self.tradingsymbol}', "
                f"exchange='{self.exchange}', quantity={self.quantity}, avg_price={self.average_price}, "
                f"pnl={self.pnl}, day_change={self.day_change}, day_change_pct={self.day_change_percentage})>")

