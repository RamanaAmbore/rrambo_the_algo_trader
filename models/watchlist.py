from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Watchlist(Base):
    """Model for user-defined watchlists."""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    instruments = relationship("WatchlistInstrument", back_populates="watchlist", cascade="all, delete")

    def __repr__(self):
        return f"<Watchlist {self.name}>"

class WatchlistInstrument(Base):
    """Mapping of instruments to watchlists."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"))
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)

    watchlist = relationship("Watchlist", back_populates="instruments")

    def __repr__(self):
        return f"<WatchlistInstrument {self.trading_symbol} ({self.exchange})>"
