from sqlalchemy import (
    Column, String, Numeric, Integer, DateTime, text, Boolean, 
    ForeignKey, Enum, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.parm_values import source

logger = get_logger(__name__)

QUANTITY_TYPES = ["LONG", "SHORT"]


class ReportProfitLoss(Base):
    """Model for tracking trading profit and loss records."""
    __tablename__ = "report_profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    symbol = Column(String(20), nullable=False)
    isin = Column(String(12), nullable=True)
    quantity = Column(Integer, nullable=False)
    buy_value = Column(Numeric(12, 2), nullable=False)
    sell_value = Column(Numeric(12, 2), nullable=False)
    realized_pnl = Column(Numeric(12, 2), nullable=False)
    realized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    previous_closing_price = Column(Numeric(10, 2), nullable=True)
    open_quantity = Column(Integer, nullable=False, default=0)
    open_quantity_type = Column(String(5), nullable=False)
    open_value = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="report_profit_loss")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("buy_value >= 0", name="check_buy_value_non_negative"),
        CheckConstraint("sell_value >= 0", name="check_sell_value_non_negative"),
        CheckConstraint("open_quantity >= 0", name="check_open_quantity_non_negative"),
        CheckConstraint(f"open_quantity_type IN {tuple(QUANTITY_TYPES)}", name="check_quantity_type_valid"),
        UniqueConstraint('account', 'symbol', name='uq_account_symbol'),
        Index("idx_account_symbol7", "account", "symbol"),
        Index("idx_symbol2", "symbol"),
        Index("idx_isin1", "isin"),
        Index("idx_timestamp", "timestamp"),
    )

    def __repr__(self):
        return (f"<ReportProfitLoss(id={self.id}, account='{self.account}', "
                f"symbol='{self.symbol}', quantity={self.quantity}, "
                f"realized_pnl={self.realized_pnl}, unrealized_pnl={self.unrealized_pnl})>")
