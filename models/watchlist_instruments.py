from sqlalchemy import (
    Column, Integer, String, DateTime, text, Boolean, Index, 
    ForeignKeyConstraint, ForeignKey, Enum, CheckConstraint
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class WatchlistInstruments(Base):
    """Mapping of instruments to watchlists."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    watchlist_id = Column(String(20), nullable=False)
    trading_symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(10), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    # watchlist = relationship("Watchlists", back_populates="instruments")
    # broker_account = relationship("BrokerAccounts", back_populates="watchlist_instruments")

    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "watchlist_id"],
            ["watchlists.account_id", "watchlists.id"],
            ondelete="CASCADE"
        ),
        Index("idx_watchlist_id", "account_id", "watchlist_id"),
        Index("idx_instrument3", "instrument_token"),
        Index("idx_symbol_exchange", "trading_symbol", "exchange"),
        CheckConstraint("instrument_token > 0", name="check_token_positive")
    )

    def __repr__(self):
        return (f"<WatchlistInstruments(id={self.id}, watchlist_id='{self.watchlist_id}', "
                f"trading_symbol='{self.trading_symbol}', exchange='{self.exchange}', "
                f"instrument_token={self.instrument_token}, source='{self.source}', "
                f"warning_error={self.warning_error})>")

