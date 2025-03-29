from sqlalchemy import (Column, Integer, String, DateTime, text, ForeignKeyConstraint, UniqueConstraint)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class WatchlistInstruments(Base):
    """Model for storing instruments in a watchlist."""
    __tablename__ = "watchlist_instruments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    watchlist = Column(String(20), nullable=False)
    account = Column(String(10), nullable=True)
    tradingsymbol = Column(String(50), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    exchange = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint("watchlist", "account", "tradingsymbol", "exchange",
                         name="uq_watchlist_instruments"),

        # Foreign key reference for (watchlist, account)
        ForeignKeyConstraint(["watchlist", "account"], ["watch_list.watchlist", "watch_list.account"],
                             ondelete="CASCADE", name="fk_watchlist_account"),

        # Foreign key reference for (tradingsymbol, instrument_token, exchange)
        ForeignKeyConstraint(["tradingsymbol", "exchange"],
                             ["stock_list.tradingsymbol", "stock_list.exchange"],
                             ondelete="CASCADE", name="fk_stock_list")
    )

    watchlist_rel = relationship("WatchList", back_populates="watchlist_instruments")

    def __repr__(self):
        return f"<WatchlistInstrument(id={self.id}, watchlist='{self.watchlist}', " \
               f"account='{self.account}', tradingsymbol='{self.tradingsymbol}', " \
               f"instrument_token='{self.instrument_token}', exchange='{self.exchange}')>"
