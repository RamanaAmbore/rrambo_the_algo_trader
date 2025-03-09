from sqlalchemy import (Column, Integer, String, DateTime, DECIMAL, text, Boolean, ForeignKey, Enum, CheckConstraint, 
                       Index, UniqueConstraint)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.load_db_parms import source

logger = get_logger(__name__)


class Holdings(Base):
    """Model to store portfolio holdings, structured to match Zerodha Kite API."""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    trading_symbol = Column(String(20), nullable=False)
    exchange = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(DECIMAL(10, 2), nullable=False)
    current_price = Column(DECIMAL(10, 2), nullable=True)
    pnl = Column(DECIMAL(10, 2), nullable=True)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="holdings")

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("average_price >= 0", name="check_avg_price_non_negative"),
        CheckConstraint("current_price >= 0", name="check_current_price_non_negative"),
        UniqueConstraint('account', 'trading_symbol', name='uq_account_symbol1'),
        Index("idx_account_symbol", "account", "trading_symbol"),
        Index("idx_trading_symbol1", "trading_symbol"),
    )

    def __repr__(self):
        return (f"<Holdings(id={self.id}, account='{self.account}', "
                f"trading_symbol='{self.trading_symbol}', exchange='{self.exchange}', "
                f"quantity={self.quantity}, avg_price={self.average_price})>")
