from sqlalchemy import (Column, Integer, String, DateTime, text, ForeignKeyConstraint, UniqueConstraint, func, DECIMAL,
                        Index, ForeignKey)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.settings.constants_manager import Source
from .base import Base


class WatchlistSymbols(Base):
    """Model for storing instruments in a watchlist."""
    __tablename__ = "watchlist_symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    tradingsymbol = Column(String(50), nullable=False, index=True)  # Index added

    exchange = Column(String(20), nullable=False)

    symbol_exchange = Column(String(50), nullable=True)  # Index added

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
                         name="uq_watchlist_symbols"),

        # Foreign key reference for (watchlist, account)
        ForeignKeyConstraint(["watchlist", "account"], ["watchlist.watchlist", "watchlist.account"],
                             ondelete="CASCADE", name="fk_watchlist_account"),

        # # Foreign key reference for (tradingsymbol, instrument_token, exchange)
        # ForeignKeyConstraint(["tradingsymbol", "exchange"],
        #                      ["instrument_list.tradingsymbol", "instrument_list.exchange"],
        #                      ondelete="CASCADE", name="fk_instrument_list"),

        # Explicitly defining indexes
        Index("idx_tradingsymbol5", "tradingsymbol"),
        Index("idx_tradingsymbol4", "tradingsymbol", "exchange"),

    )

    watchlist_rel = relationship("Watchlist", back_populates="watchlist_symbols_rel", passive_deletes=True, )

    def __repr__(self):
        return f"<WatchlistInstrument(id={self.id}, watchlist='{self.watchlist}', " \
               f"account='{self.account}', tradingsymbol='{self.tradingsymbol}', " \
               f"instrument_token='{self.instrument_token}', exchange='{self.exchange}')>"
