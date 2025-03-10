from sqlalchemy import Column, String, DateTime, text, Boolean, Enum, event, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from settings.parm_values import source, DEFAULT_BROKER_ACCOUNTS

logger = get_logger(__name__)


class BrokerAccounts(Base):
    """Model for storing broker account details."""
    __tablename__ = "broker_accounts"

    account = Column(String(10), primary_key=True)
    broker_name = Column(String(20), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    access_tokens = relationship("AccessTokens", back_populates="broker_account")
    holdings = relationship("Holdings", back_populates="broker_account")
    parameter = relationship("Parameters", back_populates="broker_account")
    backtest_results = relationship("BacktestResults", back_populates="broker_account")
    option_greeks = relationship("OptionGreeks", back_populates="broker_account")
    report_ledger_entries = relationship("ReportLedgerEntries", back_populates="broker_account")
    option_strategies = relationship("OptionStrategies", back_populates="broker_account")
    orders = relationship("Orders", back_populates="broker_account")
    refresh_flags = relationship("RefreshFlags", back_populates="broker_account")
    stock_list = relationship("StockList", back_populates="broker_account")
    strategy_config = relationship("StrategyConfig", back_populates="broker_account")
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="broker_account")
    report_tradebook = relationship("ReportTradebook", back_populates="broker_account")
    positions = relationship("Positions", back_populates="broker_account")
    option_contracts = relationship("OptionContracts", back_populates="broker_account")
    report_profit_loss = relationship("ReportProfitLoss", back_populates="broker_account")

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
            ).scalar() is not None

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
