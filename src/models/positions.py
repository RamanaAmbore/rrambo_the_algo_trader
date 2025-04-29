from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, ForeignKeyConstraint,
    CheckConstraint, Index, DECIMAL, func, text
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.parameter_manager import parms
from .base import Base
from src.settings.constants_manager import Source

logger = get_logger(__name__)


class Positions(Base):
    """Model to store trading positions."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False,
                     default=parms.DEF_ACCOUNT)
    tradingsymbol = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)
    instrument_token = Column(Integer, nullable=False)

    symbol_exchange = Column(String(50), nullable=True)

    product = Column(String(10), nullable=False, default="NRML")

    quantity = Column(Integer, nullable=False, default=0)
    average_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    last_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    close_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    pnl = Column(DECIMAL(12, 4), nullable=False, default=0)
    m2m = Column(DECIMAL(12, 4), nullable=False, default=0)
    realised = Column(DECIMAL(12, 4), nullable=False, default=0)
    unrealised = Column(DECIMAL(12, 4), nullable=False, default=0)
    multiplier = Column(Integer, nullable=False, default=1)

    buy_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    buy_quantity = Column(Integer, nullable=False, default=0)
    buy_value = Column(DECIMAL(12, 4), nullable=False, default=0)
    buy_m2m = Column(DECIMAL(12, 4), nullable=False, default=0)

    sell_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    sell_quantity = Column(Integer, nullable=False, default=0)
    sell_value = Column(DECIMAL(12, 4), nullable=False, default=0)
    sell_m2m = Column(DECIMAL(12, 4), nullable=False, default=0)

    day_buy_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    day_buy_quantity = Column(Integer, nullable=False, default=0)
    day_buy_value = Column(DECIMAL(12, 4), nullable=False, default=0)
    day_sell_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    day_sell_quantity = Column(Integer, nullable=False, default=0)
    day_sell_value = Column(DECIMAL(12, 4), nullable=False, default=0)

    value = Column(DECIMAL(12, 4), nullable=False, default=0)

    # Carry forward position details
    overnight_price = Column(DECIMAL(10, 2), nullable=False, default=0)  # Yesterday's price
    overnight_quantity = Column(Integer, nullable=False, default=0)  # Yesterday's quantity
    overnight_value = Column(DECIMAL(10, 2), nullable=False, default=0)  # Yesterday's value

    source = Column(String(50), nullable=False, server_default=Source.API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    broker_accounts_rel = relationship("BrokerAccounts", back_populates="positions_rel", passive_deletes=True)
    instrument_list_rel = relationship("InstrumentList", back_populates="positions_rel", passive_deletes=True)

    __table_args__ = (
        # Composite Foreign Key Constraint to stocklist
        ForeignKeyConstraint(
            ["tradingsymbol", "exchange"],
            ["instrument_list.tradingsymbol", "instrument_list.exchange"],
            ondelete="CASCADE"
        ),
        # UniqueConstraint("type", "tradingsymbol", "exchange", "account", "quantity", name="uq_account_tradingsymbol4"),

        Index("idx_account_tradingsymbol3", "account", "tradingsymbol"),
        Index("idx_tradingsymbol_exchange1", "tradingsymbol", "exchange"),

        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("last_price >= 0", name="check_last_price_non_negative"),
        CheckConstraint("pnl >= -99999999.9999", name="check_pnl_range"),
        CheckConstraint("buy_quantity >= 0", name="check_buy_quantity_non_negative"),
        CheckConstraint("sell_quantity >= 0", name="check_sell_quantity_non_negative"),
        CheckConstraint("realised >= -99999999.9999", name="check_realised_range"),
        CheckConstraint("unrealised >= -99999999.9999", name="check_unrealised_range"),
    )

    def __repr__(self):
        return f"<Positions(account={self.account}, tradingsymbol={self.tradingsymbol}, quantity={self.quantity}, pnl={self.pnl})>"
