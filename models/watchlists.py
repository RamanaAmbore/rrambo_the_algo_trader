from sqlalchemy import Column, String, ForeignKey, DateTime, text, Boolean, Index, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from utils.model_utils import source
from utils.date_time_utils import timestamp_indian
from .base import Base


class Watchlists(Base):
    """Model for storing user watchlists."""
    __tablename__ = "watchlists"

    id = Column(String(20), nullable=False, primary_key=True)
    watchlist = Column(String(20), unique=True)
    desc = Column(String(255), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('watchlist', name='uq_watchlist'),
        Index("idx_watchlist", "watchlist"),
    )

    watchlist_instruments = relationship("WatchlistInstruments", back_populates="watchlist_rel")

    def __repr__(self):
        return f"<Watchlist(id={self.id}, watchlist='{self.watchlist}', desc='{self.desc}')>"