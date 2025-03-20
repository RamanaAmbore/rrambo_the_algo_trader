from sqlalchemy import (
    Column, String, Numeric, Integer, DateTime, text, Boolean,
    BigInteger, ForeignKey, Enum, CheckConstraint, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

TRADE_TYPES = ["buy", "sell"]
SEGMENTS = ["EQ", "FO", "CD", "CO"]


class ReportTradebook(Base):
    """Model for storing trade execution records."""
    __tablename__ = "report_tradebook"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    trade_id = Column(BigInteger, nullable=False)
    order_id = Column(BigInteger, nullable=False)
    symbol = Column(String(20), nullable=False)
    isin = Column(String(12), nullable=True)
    exchange = Column(String(10), nullable=False)
    segment = Column(String(10), nullable=False)
    series = Column(String(5), nullable=True)
    trade_type = Column(String(4), nullable=False)
    auction = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    order_execution_time = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    source = Column(Enum(Source), nullable=False, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="report_tradebook")

    __table_args__ = (
        CheckConstraint(f"trade_type IN {tuple(TRADE_TYPES)}", name="check_valid_trade_type"),
        CheckConstraint(f"segment IN {tuple(SEGMENTS)}", name="check_valid_segment"),
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        UniqueConstraint('account', 'trade_id', name='uq_trade_id1'),
        Index("idx_trade_id", "account", "trade_id"),
        Index("idx_order_id", "order_id"),
        Index("idx_symbol3", "symbol"),
        Index("idx_isin2", "isin"),
        Index("idx_account_date", "account", "trade_date"),
        Index("idx_symbol_date", "symbol", "trade_date"),
    )

    def __repr__(self):
        return (f"<ReportTradebook(id={self.id}, trade_id={self.trade_id}, "
                f"symbol='{self.symbol}', trade_type='{self.trade_type}', "
                f"quantity={self.quantity}, price={self.price})>")
