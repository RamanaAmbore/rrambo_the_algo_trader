from sqlalchemy import Column, String, DateTime, text, Boolean, Index, Enum, UniqueConstraint, event, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from settings.load_db_parms import source, DEFAULT_WATCHLISTS
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class Watchlists(Base):
    """Model for storing user watchlists."""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True,  autoincrement=True)
    watchlist = Column(String(20), unique=True)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint('watchlist', name='uq_watchlist'), Index("idx_watchlist1", "watchlist"),)

    watchlist_instruments = relationship("WatchlistInstruments", back_populates="watchlist_rel")

    def __repr__(self):
        return f"<Watchlist(id={self.id}, watchlist='{self.watchlist}')>"


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = Watchlists.__table__
        for record in DEFAULT_WATCHLISTS:
            exists = connection.execute(
                select(table.c.watchlist).where(table.c.watchlist == record['watchlist'])).scalar() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Watchlist records: {e}")


@event.listens_for(Watchlists.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Watchlist records inserted after after_create event')
