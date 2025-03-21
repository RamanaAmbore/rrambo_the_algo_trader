from sqlalchemy import (Column, Integer, String, DateTime, text, Boolean, Index, ForeignKey, Enum,
                        UniqueConstraint, func)
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class WatchlistInstruments(Base):
    """Mapping of instruments to watchlists."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), ForeignKey("watchlists.watchlist", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(50), nullable=False)
    exchange = Column(String(10), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    watchlist_rel = relationship("Watchlists", back_populates="watchlist_instruments")

    __table_args__ = (
        UniqueConstraint('watchlist', 'symbol', 'exchange', name='uq_watchlist_instrument'),
        Index("idx_watchlist", "watchlist"),
        Index("idx_instrument", "instrument_token"),
        Index("idx_symbol", "symbol"),
        Index("idx_symbol_exchange", "symbol", "exchange"),
    )

    def __repr__(self):
        return (f"<WatchlistInstruments(id={self.id}, watchlist='{self.watchlist}', "
                f"symbol='{self.symbol}', exchange='{self.exchange}', "
                f"instrument_token={self.instrument_token})>")  # Simplified repr
