from sqlalchemy import (Column, Integer, String, DateTime, text, ForeignKeyConstraint, UniqueConstraint, func, DECIMAL,
                        Index, select, ForeignKey)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base
from ..settings.constants_manager import Source, DEF_WATCHLIST_INSTRUMENTS

logger = get_logger(__name__)


class WatchListInstruments(Base):
    """Model for storing instruments in a watchlist."""
    __tablename__ = "watch_list_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    tradingsymbol = Column(String(50), nullable=False, index=True)  # Index added
    instrument_token = Column(Integer, nullable=True, index=True)  # Index added
    exchange = Column(String(20), nullable=False)

    
    prev_close_price = Column(DECIMAL(12, 4), nullable=True, default=0)
    last_price = Column(DECIMAL(12, 4), nullable=True, default=0)
    change = Column(DECIMAL(12, 4), nullable=True, default=0)
    change_percent = Column(DECIMAL(5, 2), nullable=True, default=0)

    buy_price = Column(DECIMAL(12, 4), nullable=True, default=0)
    buy_quantity = Column(Integer, nullable=True, default=0)
    sell_price = Column(DECIMAL(12, 4), nullable=True, default=0)
    sell_quantity = Column(Integer, nullable=True, default=0)
    multiplier = Column(Integer, nullable=True, default=1)
    profit = Column(DECIMAL(12, 4), nullable=True, default=0)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("watchlist", "account", "tradingsymbol", "exchange",
                         name="uq_watchlist_instruments"),

        # Foreign key reference for (watchlist, account)
        ForeignKeyConstraint(["watchlist", "account"], ["watch_list.watchlist", "watch_list.account"],
                             ondelete="CASCADE", name="fk_watchlist_account"),

        # # Foreign key reference for (tradingsymbol, instrument_token, exchange)
        # ForeignKeyConstraint(["tradingsymbol", "exchange"],
        #                      ["instrument_list.tradingsymbol", "instrument_list.exchange"],
        #                      ondelete="CASCADE", name="fk_instrument_list"),

        # Explicitly defining indexes
        Index("idx_tradingsymbol2", "tradingsymbol"),
        Index("idx_tradingsymbol4", "tradingsymbol", "exchange"),
        Index("idx_instrument_token3", "instrument_token"),
    )

    watch_list_rel = relationship("WatchList", back_populates="watchlist_instruments_rel", passive_deletes=True, )

    def __repr__(self):
        return f"<WatchlistInstrument(id={self.id}, watchlist='{self.watchlist}', " \
               f"account='{self.account}', tradingsymbol='{self.tradingsymbol}', " \
               f"instrument_token='{self.instrument_token}', exchange='{self.exchange}')>"





def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = WatchListInstruments.__table__
        for record in DEF_WATCHLIST_INSTRUMENTS:
            stmt = select(table.c.watchlist).where(
                (table.c.watchlist == record['watchlist']) &
                (table.c.tradingsymbol == record['tradingsymbol']) &
                (table.c.exchange == record['exchange']) &
                (table.c.account == record.get('account','*'))  # Default to None if not present
            )
            exists = connection.execute(stmt).scalar_one_or_none()

            if exists is None:  # Fixes the boolean check issue
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Watch List records inserted/updated')
    except Exception as e:
        logger.error(f"Error inserting default Watch List records: {e}", exc_info=True)
        raise
