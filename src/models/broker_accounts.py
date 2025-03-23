from sqlalchemy import Column, String, DateTime, text, event, Index, UniqueConstraint, func, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEFAULT_BROKER_ACCOUNTS
from .base import Base

logger = get_logger(__name__)


class BrokerAccounts(Base):
    """Model for storing broker account details."""
    __tablename__ = "broker_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), nullable=False)

    broker_name = Column(String(20), nullable=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    access_tokens = relationship("AccessTokens", back_populates="broker_account", cascade="all, delete")
    holdings = relationship("Holdings", back_populates="broker_account", cascade="all, delete")
    parameter_table = relationship("ParameterTable", back_populates="broker_account", cascade="all, delete")
    backtest_results = relationship("BacktestResults", back_populates="broker_account", cascade="all, delete")
    option_greeks = relationship("OptionGreeks", back_populates="broker_account", cascade="all, delete")
    report_ledger_entries = relationship("ReportLedgerEntries", back_populates="broker_account", cascade="all, delete")
    option_strategies = relationship("OptionStrategies", back_populates="broker_account", cascade="all, delete")
    orders = relationship("Orders", back_populates="broker_account", cascade="all, delete")
    refresh_flags = relationship("RefreshFlags", back_populates="broker_account", cascade="all, delete")
    strategy_config = relationship("StrategyConfig", back_populates="broker_account", cascade="all, delete")
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="broker_account", cascade="all, delete")
    report_tradebook = relationship("ReportTradebook", back_populates="broker_account", cascade="all, delete")
    positions = relationship("Positions", back_populates="broker_account", cascade="all, delete")
    option_contracts = relationship("OptionContracts", back_populates="broker_account", cascade="all, delete")
    report_profit_loss = relationship("ReportProfitLoss", back_populates="broker_account", cascade="all, delete")

    __table_args__ = (
        UniqueConstraint('account', name='uq_broker_account'),
        Index("idx_broker_account", "account"),
        Index("idx_broker_name", "broker_name"),
    )

    def __repr__(self):
        return (f"<BrokerAccounts(account='{self.account}', "
                f"broker_name='{self.broker_name}', notes='{self.notes}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = BrokerAccounts.__table__
        for record in DEFAULT_BROKER_ACCOUNTS:
            exists = connection.execute(
                select(table.c.account).where(
                    table.c.account == record['account']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Broker Account records: {e}")
        raise


@event.listens_for(BrokerAccounts.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Broker Account records inserted after after_create event')
