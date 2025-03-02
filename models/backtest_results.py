from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, text
from sqlalchemy.future import select

from utils.date_time_utils import timestamp_indian
from .base import Base


class BacktestResults(Base):
    """Stores backtesting results for trading strategies."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(Integer, ForeignKey("strategy_config.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    total_pnl = Column(DECIMAL(10, 2), nullable=False)  # 2 decimal places
    max_drawdown = Column(DECIMAL(10, 2), nullable=True)  # 2 decimal places
    win_rate = Column(DECIMAL(5, 2), nullable=True)  # 2 decimal places, smaller range
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    @classmethod
    async def get_all_results(cls, session):
        """Fetch all backtest results asynchronously."""
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def insert_result(cls, session, result_data):
        """Insert a new backtest result asynchronously."""
        new_result = cls(**result_data)
        session.add(new_result)
        await session.commit()
        return new_result
