from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, text, String, Boolean, Index, CheckConstraint, \
    Enum
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class BacktestResults(Base):
    """
    Stores backtesting results for trading strategies.

    This table records the performance of different trading strategies
    over a specified period, storing key metrics such as profit/loss,
    drawdown, and win rate.
    """
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id", ondelete="CASCADE"), nullable=False, index=True)

    # Date range for backtest
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Performance metrics
    total_pnl = Column(DECIMAL(10, 2), nullable=False)  # Profit/Loss (ensured to be non-null)
    max_drawdown = Column(DECIMAL(10, 2), nullable=True)  # Maximum drawdown
    win_rate = Column(DECIMAL(6, 3), nullable=True)  # Win rate percentage (allowing up to 100.000%)

    # Metadata
    source = Column(Enum(source), nullable=True, server_default="CODE")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))

    # Error/warning tracking
    warning_error = Column(Boolean, nullable=False, default=False)  # Whether backtest encountered warnings/errors
    notes = Column(String(255), nullable=True)  # Additional messages or error details

    # Relationships for ORM
    # account = relationship("BrokerAccounts", back_populates="backtest_results")
    # strategy = relationship("StrategyConfig", back_populates="backtest_results")

    # Table constraints & indexes
    __table_args__ = (CheckConstraint("total_pnl >= 0", name="check_total_pnl_non_negative"),
                      CheckConstraint("win_rate >= 0 AND win_rate <= 100", name="check_win_rate_range"),
                      Index("idx_backtest_account_id", "account_id"),)

    def __repr__(self):
        return (f"<BacktestResults(id={self.id}, account_id='{self.account_id}', strategy_id={self.strategy_id}, "
                f"start_date={self.start_date}, end_date={self.end_date}, total_pnl={self.total_pnl}, "
                f"max_drawdown={self.max_drawdown}, win_rate={self.win_rate}, source='{self.source}', "
                f"timestamp={self.timestamp}, warning_error={self.warning_error}, notes='{self.notes}')>")
