from sqlalchemy import Column, String, DateTime, text, Index, UniqueConstraint, Integer, func, \
    ForeignKey, select
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_WATCHLISTS
from .base import Base

logger = get_logger(__name__)


class WatchList(Base):
    """Model for storing user watch_list."""
    __tablename__ = "watch_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False,default='*')
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

    watchlist_instruments_rel = relationship("WatchListInstruments", back_populates="watch_list_rel", passive_deletes=True, )

    def __repr__(self):
        return f"<Watchlist(id={self.id}, watchlist='{self.watchlist}', account='{self.account}')>"

def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = WatchList.__table__
        for record in DEF_WATCHLISTS:
            exists = connection.execute(
                select(table.c.watchlist, table.c.account).where(
                    (table.c.watchlist == record['watchlist']) & (table.c.account == record.get('account','*'))
                )
            ).scalar_one_or_none()

            if exists is None:  # Fixes the boolean check issue
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Watch List records inserted/updated')
    except Exception as e:
        logger.error(f"Error inserting default Watch List records: {e}", exc_info=True)
        raise



