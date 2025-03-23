from sqlalchemy import (Column, Integer, String, DateTime, text, Index, ForeignKey, UniqueConstraint, func)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class WatchlistInstruments(Base):
    """Model for storing instruments in a watchlist."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), ForeignKey("watchlists.watchlist", ondelete="CASCADE"), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    tradingsymbol = Column(String(50), ForeignKey("stocklists.tradingsymbol"), nullable=False)
    instrument_token = Column(Integer, ForeignKey("stocklists.instrument_token"), nullable=False)
    exchange = Column(String(20), ForeignKey("stocklists.exchange"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint('watchlist', 'account', 'trading_symbol', 'instrument_token', 'exchange',
                         name='uq_watchlist_instruments'),
    )

    watchlist_rel = relationship("Watchlists", back_populates="watchlist_instruments")

    def __repr__(self):
        return f"<WatchlistInstrument(id={self.id}, watchlist='{self.watchlist}', " \
               f"account='{self.account}', trading_symbol='{self.trading_symbol}', " \
               f"instrument_token='{self.instrument_token}', exchange='{self.exchange}')>"