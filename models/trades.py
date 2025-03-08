from sqlalchemy import (
    Column, String, Numeric, Integer, DateTime, text, Boolean, 
    BigInteger, ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)

# Enums for trade fields
TRADE_TYPES = ["BUY", "SELL"]
SEGMENTS = ["EQUITY", "FO", "CD", "CO"]
INSTRUMENT_TYPES = ["EQ", "FUT", "CE", "PE", "CD"]


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    trade_id = Column(BigInteger, unique=True, nullable=False, index=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    trading_symbol = Column(String(20), nullable=False, index=True)
    isin = Column(String(12), nullable=True, index=True)
    exchange = Column(String(10), nullable=False)
    segment = Column(String(10), nullable=False)
    series = Column(String(5), nullable=False)
    trade_type = Column(String(4), nullable=False)
    auction = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    order_execution_time = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    instrument_type = Column(String(5), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="trades")

    __table_args__ = (
        CheckConstraint(f"trade_type IN {tuple(TRADE_TYPES)}", name="check_valid_trade_type"),
        CheckConstraint(f"segment IN {tuple(SEGMENTS)}", name="check_valid_segment"),
        CheckConstraint(f"instrument_type IN {tuple(INSTRUMENT_TYPES)}", name="check_valid_instrument_type"),
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        Index("idx_account_date2", "account_id", "trade_date"),
        Index("idx_symbol_date", "trading_symbol", "trade_date"),
    )

    def __repr__(self):
        return (f"<Trades(id={self.id}, trade_id={self.trade_id}, "
                f"trading_symbol='{self.trading_symbol}', trade_type='{self.trade_type}', "
                f"quantity={self.quantity}, price={self.price}, "
                f"trade_date={self.trade_date}, source='{self.source}', "
                f"warning_error={self.warning_error})>")
