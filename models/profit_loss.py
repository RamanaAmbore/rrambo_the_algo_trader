from sqlalchemy import (
    Column, String, Numeric, Integer, DateTime, text, Boolean, 
    ForeignKey, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)

# Enum values for open quantity type
QUANTITY_TYPES = ["LONG", "SHORT"]


class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    isin = Column(String(12), nullable=True, index=True)
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
    broker_account= relationship("BrokerAccounts", back_populates="profit_loss")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("buy_value >= 0", name="check_buy_value_non_negative"),
        CheckConstraint("sell_value >= 0", name="check_sell_value_non_negative"),
        CheckConstraint("open_quantity >= 0", name="check_open_quantity_non_negative"),
        CheckConstraint(f"open_quantity_type IN {tuple(QUANTITY_TYPES)}", name="check_quantity_type_valid"),
        Index("idx_account_symbol4", "account_id", "symbol"),
        Index("idx_timestamp3", "timestamp"),
    )

    def __repr__(self):
        return (f"<ProfitLoss(id={self.id}, account_id='{self.account_id}', "
                f"symbol='{self.symbol}', quantity={self.quantity}, "
                f"realized_pnl={self.realized_pnl}, unrealized_pnl={self.unrealized_pnl}, "
                f"open_quantity={self.open_quantity}, open_quantity_type='{self.open_quantity_type}', "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error})>")
