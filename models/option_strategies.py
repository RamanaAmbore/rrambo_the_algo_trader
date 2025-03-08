from sqlalchemy import (Column, Integer, String, DateTime, DECIMAL, JSON, Boolean, text, ForeignKey, Enum,
                        CheckConstraint, Index)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class OptionStrategies(Base):
    """Model to store option trading strategies and their risk-reward parameters."""
    __tablename__ = "option_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    strategy_name = Column(String(50), nullable=False)
    legs = Column(JSON, nullable=False)
    max_profit = Column(DECIMAL(12, 2), nullable=True)
    max_loss = Column(DECIMAL(12, 2), nullable=True)
    breakeven_points = Column(JSON, nullable=True)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="option_strategies")

    __table_args__ = (CheckConstraint("max_loss <= 0", name="check_max_loss_negative"),
                      CheckConstraint("max_profit >= 0", name="check_max_profit_positive"),
                      Index("idx_account_strategy1", "account_id", "strategy_name"),
                      Index("idx_timestamp2", "timestamp"),)

    def __repr__(self):
        return (f"<OptionStrategy(id={self.id}, account_id='{self.account_id}', "
                f"strategy_name='{self.strategy_name}', legs={self.legs}, "
                f"max_profit={self.max_profit}, max_loss={self.max_loss}, "
                f"breakeven_points={self.breakeven_points}, source='{self.source}', "
                f"timestamp={self.timestamp}, warning_error={self.warning_error}, "
                f"notes='{self.notes}')>")
