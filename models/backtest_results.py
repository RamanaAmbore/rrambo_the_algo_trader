from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey

from utils.config_loader import sc
from .base import Base


class BacktestResults(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    total_pnl = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))
