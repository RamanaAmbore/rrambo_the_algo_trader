from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, text, Boolean,
    ForeignKey, Enum, Index, func
)
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    strategy_name = Column(String(50), unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    backtest_results = relationship("BacktestResults", back_populates="strategy_config")
    broker_account = relationship("BrokerAccounts", back_populates="strategy_config")

    __table_args__ = (
        Index("idx_account_strategy2", "account", "strategy_name"),
        Index("idx_timestamp4", "timestamp"),
    )

    def __repr__(self):
        return (f"<StrategyConfig(id={self.id}, account='{self.account}', "
                f"strategy_name='{self.strategy_name}', source='{self.source}', "
                f"timestamp={self.timestamp}, warning_error={self.warning_error})>")
