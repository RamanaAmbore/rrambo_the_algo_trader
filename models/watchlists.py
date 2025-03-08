from sqlalchemy import Column, String, ForeignKey, DateTime, text, Boolean, Index, Enum
from sqlalchemy.orm import relationship
from utils.model_utils import source
from utils.date_time_utils import timestamp_indian
from .base import Base


class Watchlists(Base):
    """Model for storing user watchlists."""
    __tablename__ = "watchlists"

    # Define columns with composite primary key
    id = Column(String(20), nullable=False, primary_key=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), 
                       nullable=True, primary_key=True)
    desc = Column(String(255), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Define indexes
    __table_args__ = (
        Index("idx_account_desc", "account_id", "desc", unique=True),
    )

    # Relationship with WatchlistInstruments
    watchlist_instruments = relationship("WatchlistInstruments", back_populates="watchlist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Watchlist(id={self.id}, account_id={self.account_id}, name={self.desc})>"