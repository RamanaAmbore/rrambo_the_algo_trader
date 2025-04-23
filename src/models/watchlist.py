from sqlalchemy import Column, String, DateTime, text, Index, UniqueConstraint, Integer, func, \
    ForeignKey
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class Watchlist(Base):
    """Model for storing user watchlist."""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('watchlist', 'account', name='uq_watchlist_account1'),
        Index("idx_watchlist1", "watchlist"),
    )

    watchlist_symbols_rel = relationship("WatchlistSymbols", back_populates="watchlist_rel",
                                             passive_deletes=True, )

    def __repr__(self):
        return f"<Watchlist(id={self.id}, watchlist='{self.watchlist}', account='{self.account}')>"
