from sqlalchemy import Column, Integer, String, DateTime, text, Boolean, Index, ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class WatchlistInstruments(Base):
    """Mapping of instruments to watchlists."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier for the record
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    watchlist_id = Column(String(20), nullable=False)  # Keep consistent with Watchlists.id
    trading_symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(10), nullable=False)  # Made non-nullable for integrity
    instrument_token = Column(String(20), nullable=False)  # Converted to String
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Foreign Key referencing Watchlists (account_id + watchlist_id)
    __table_args__ = (
        ForeignKeyConstraint(["account_id", "watchlist_id"], ["watchlists.account_id", "watchlists.id"],
                             ondelete="CASCADE"),
        Index("idx_watchlist_id", "account_id", "watchlist_id")  # Optimized indexing
    )

    watchlist = relationship("Watchlists", back_populates="instruments")

    def __repr__(self):
        return f"<WatchlistInstrument {self.trading_symbol} ({self.exchange})>"

