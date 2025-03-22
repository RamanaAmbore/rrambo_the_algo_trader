from sqlalchemy import (
    Column, String, Decimal, Integer, DateTime, text, ForeignKey, CheckConstraint, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

QUANTITY_TYPES = ["LONG", "SHORT"]


class ReportProfitLoss(Base):
    """Model for tracking trading profit and loss records."""
    __tablename__ = "report_profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50), nullable=False)
    isin = Column(String(12), nullable=True)
    quantity = Column(Integer, nullable=False)
    buy_value = Column(Decimal(12, 2), nullable=False)
    sell_value = Column(Decimal(12, 2), nullable=False)
    realized_pnl = Column(Decimal(12, 2), nullable=False)
    realized_pnl_pct = Column(Decimal(12, 2), nullable=False)
    previous_closing_price = Column(Decimal(10, 2), nullable=True)
    open_quantity = Column(Integer, nullable=True, default=0)
    open_quantity_type = Column(String(5), nullable=True)
    open_value = Column(Decimal(12, 2), nullable=False)
    unrealized_pnl = Column(Decimal(12, 2), nullable=False)
    unrealized_pnl_pct = Column(Decimal(12, 2), nullable=False)
    source = Column(String(50), nullable=False, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="report_profit_loss")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("buy_value >= 0", name="check_buy_value_non_negative"),
        CheckConstraint("sell_value >= 0", name="check_sell_value_non_negative"),
        CheckConstraint("open_quantity >= 0", name="check_open_quantity_non_negative"),
        CheckConstraint(f"open_quantity_type IN {tuple(QUANTITY_TYPES)}", name="check_quantity_type_valid"),
        UniqueConstraint("account", "tradingsymbol", 'isin', 'quantity', 'buy_value', 'sell_value', name='uq_account_symbol'),
        Index("idx_account_symbol7", "account", "tradingsymbol", 'isin', 'quantity', 'buy_value', 'sell_value'),
        Index("idx_symbol4", "tradingsymbol"),
        Index("idx_isin1", "isin"),
        Index("idx_timestamp", "timestamp"),
    )

    def __repr__(self):
        return (f"<ReportProfitLoss(id={self.id}, account='{self.account}', "
                f"tradingsymbol='{self.tradingsymbol}', quantity={self.quantity}, "
                f"realized_pnl={self.realized_pnl}, unrealized_pnl={self.unrealized_pnl})>")
