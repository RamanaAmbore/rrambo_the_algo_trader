from sqlalchemy import (Column, Integer, String, DateTime, text, Boolean, Index, ForeignKeyConstraint, ForeignKey, Enum,
                        CheckConstraint, UniqueConstraint)
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
    watchlist = Column(String(20), ForeignKey("watchlists.watchlist", ondelete="CASCADE"), nullable=False)
    trading_symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(10), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Keep only watchlist relationship
    watchlist_rel = relationship("Watchlists", back_populates="watchlist_instruments")

    __table_args__ = (
        UniqueConstraint('watchlist', 'trading_symbol', name='uq_watchlist_symbol'),
        Index("idx_watchlist1", "watchlist"),
        Index("idx_instrument", "instrument_token"),
        Index("idx_symbol_exchange", "trading_symbol", "exchange"),
    )

    def __repr__(self):
        return (f"<WatchlistInstruments(id={self.id}, watchlist='{self.watchlist}', "
                f"trading_symbol='{self.trading_symbol}', exchange='{self.exchange}', "
                f"instrument_token={self.instrument_token}, source='{self.source}', "
                f"warning_error={self.warning_error})>")
