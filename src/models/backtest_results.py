from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, text, String, Boolean, Index, CheckConstraint, \
    func
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

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
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id", ondelete="CASCADE"), nullable=False, index=True)

    # Date range for backtest
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)

    # Performance metrics
    total_pnl = Column(DECIMAL(10, 2), nullable=False)  # Profit/Loss (ensured to be non-null)
    max_drawdown = Column(DECIMAL(10, 2), nullable=True)  # Maximum drawdown
    win_rate = Column(DECIMAL(6, 3), nullable=True)  # Win rate percentage (allowing up to 100.000%)

    # Metadata
    source = Column(String(50), nullable=False, server_default="CODE")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    # Error/warning tracking
    warning_error = Column(Boolean, nullable=False, default=False)  # Whether backtest encountered warnings/errors
    notes = Column(String(255), nullable=True)  # Additional messages or error details

    # Relationships for ORM
    broker_account = relationship("BrokerAccounts", back_populates="backtest_results")
    strategy_config = relationship("StrategyConfig", back_populates="backtest_results")

    # Table constraints & indexes
    __table_args__ = (CheckConstraint("total_pnl >= 0", name="check_total_pnl_non_negative"),
                      CheckConstraint("win_rate >= 0 AND win_rate <= 100", name="check_win_rate_range"),
                      Index("idx_backtest_account", "account"),)

    def __repr__(self):
        return (f"<BacktestResults(id={self.id}, account='{self.account}', strategy_id={self.strategy_id}, "
                f"start_date={self.start_date}, end_date={self.end_date}, total_pnl={self.total_pnl}, "
                f"max_drawdown={self.max_drawdown}, win_rate={self.win_rate}, source='{self.source}', "
                f"timestamp={self.timestamp}, warning_error={self.warning_error}, notes='{self.notes}')>")
