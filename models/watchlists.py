from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, text, Boolean
from sqlalchemy.orm import relationship

from utils.settings_loader import Env
from utils.date_time_utils import timestamp_indian
from .base import Base


class Watchlists(Base):
    """Model for user-defined watchlists."""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    name = Column(String, nullable=False, unique=True)
    source = Column(String, nullable=True, default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    instruments = relationship("WatchlistInstruments", back_populates="watchlist", cascade="all, delete")

    def __repr__(self):
        return f"<Watchlist {self.name}>"


class WatchlistInstruments(Base):
    """Mapping of instruments to watchlists."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"))
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    source = Column(String, nullable=True, default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    watchlist = relationship("Watchlists", back_populates="instruments")

    def __repr__(self):
        return f"<WatchlistInstrument {self.trading_symbol} ({self.exchange})>"
