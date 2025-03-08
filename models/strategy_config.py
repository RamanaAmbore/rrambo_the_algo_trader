from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, text, Boolean, 
    ForeignKey, Enum, Index
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    strategy_name = Column(String(50), unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    # backtests = relationship("BacktestResults", back_populates="strategy")
    # broker_account = relationship("BrokerAccounts", back_populates="strategy_configs")

    __table_args__ = (
        Index("idx_account_strategy2", "account_id", "strategy_name"),
        Index("idx_timestamp4", "timestamp"),
    )

    def __repr__(self):
        return (f"<StrategyConfig(id={self.id}, account_id='{self.account_id}', "
                f"strategy_name='{self.strategy_name}', source='{self.source}', "
                f"timestamp={self.timestamp}, warning_error={self.warning_error})>")
