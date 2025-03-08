from sqlalchemy import Column, String, DateTime, text, Boolean, Enum, event
from sqlalchemy.orm import relationship

from utils.date_time_utils import timestamp_indian
from .base import Base

from utils.model_utils import source, DEFAULT_BROKER_ACCOUNTS


class BrokerAccounts(Base):
    """Model for storing broker account details manually."""
    __tablename__ = "broker_accounts"

    account_id = Column(String(10), primary_key=True)  # Unique account identifier
    broker_name = Column(String(20), nullable=False)  # Name of the broker
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Auto timestamps with timezone
    warning_error = Column(Boolean, nullable=False, default=False)  # Flag for any warnings/errors in scheduling
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        """String representation for debugging."""
        return f"<BrokerAccounts(account_id='{self.account_id}', broker_name='{self.broker_name}', notes='{self.notes}')>"

    # Add this relationship
    # AccessToken = relationship("AccessToken", back_populates="broker_account")
    # holdings = relationship("Holdings", back_populates="broker_account")
    # # Fix relationship definitions to be consistent
    # parameters = relationship("Parameters", back_populates="broker_account")
    # algo_schedules = relationship("AlgoSchedules", back_populates="broker_account")
    # backtests = relationship("BacktestResults", back_populates="broker_account")  # Changed from "account" to "broker_account"
    # option_greeks = relationship("OptionGreeks", back_populates="broker_account")
    # # Add this relationship
    # ledger_entries = relationship("LedgerEntries", back_populates="broker_account")
    # option_strategies = relationship("OptionStrategies", back_populates="broker_account")
    # # Add this relationship
    # orders = relationship("Orders", back_populates="broker_account")
    # # Add this relationship
    # refresh_flags = relationship("RefreshFlags", back_populates="broker_account")
    # # Add this relationship
    # stock_list = relationship("StockList", back_populates="broker_account")
    # # Add this relationship
    # strategy_configs = relationship("StrategyConfig", back_populates="broker_account")
    # # Add this relationship
    # threads = relationship("Threads", back_populates="broker_account")
    # # Add this relationship
    # trades = relationship("Trades", back_populates="broker_account")
    # # Add this relationship
    # watchlist_instruments = relationship("WatchlistInstruments", back_populates="broker_account")
    # # Add this relationship
    # positions = relationship("Positions", back_populates="broker_account")


@event.listens_for(BrokerAccounts.__table__, "after_create")
def insert_default_records(target, connection, **kwargs):

    connection.execute(target.insert(), DEFAULT_BROKER_ACCOUNTS)
