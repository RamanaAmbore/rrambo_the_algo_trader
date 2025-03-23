from sqlalchemy import Column, String, DateTime, text, Index, UniqueConstraint, event, Integer, func, \
    ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEFAULT_WATCHLISTS
from .base import Base

logger = get_logger(__name__)


class Watchlists(Base):
    """Model for storing user watchlists."""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('watchlist', 'account', name='uq_watchlist_account'),
        Index("idx_watchlist1", "watchlist"),
    )

    watchlist_instruments = relationship("WatchlistInstruments", back_populates="watchlist_rel")

    def __repr__(self):
        return f"<Watchlist(id={self.id}, watchlist='{self.watchlist}', account='{self.account}')>"


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = Watchlists.__table__
        for record in DEFAULT_WATCHLISTS:
            exists = connection.execute(
                select(table.c.watchlist, table.c.account).where(
                    (table.c.watchlist == record['watchlist']) & (table.c.account == record.get('account'))
                )
            ).scalar_one_or_none()

            if exists is None:  # Fixes the boolean check issue
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Watchlist records inserted/updated')
    except Exception as e:
        logger.error(f"Error inserting default Watchlist records: {e}", exc_info=True)
        raise


@event.listens_for(Watchlists.__table__, 'after_create')
def ensure_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    logger.info('Event after_create triggered for Watchlist table')
    initialize_default_records(connection)


