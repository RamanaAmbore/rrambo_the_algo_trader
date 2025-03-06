from sqlalchemy import Column, String, Numeric, Integer, select, DateTime, text, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    buy_value = Column(Numeric(12, 2), nullable=False)
    sell_value = Column(Numeric(12, 2), nullable=False)
    realized_pnl = Column(Numeric(12, 2), nullable=False)
    realized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    previous_closing_price = Column(Numeric(10, 2), nullable=True)
    open_quantity = Column(Integer, nullable=False, default=0)
    open_quantity_type = Column(String, nullable=False)
    open_value = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl = Column(Numeric(12, 2), nullable=False)
    unrealized_pnl_pct = Column(Numeric(12, 2), nullable=False)
    source = Column(String, nullable=True, default="SCHEDULE")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    @classmethod
    async def exists(cls, session: AsyncSession, symbol: str, isin: str):
        """Check if a profit-loss record exists for a symbol & ISIN."""
        result = await session.execute(select(cls).where(cls.symbol == symbol, cls.isin == isin))
        return result.scalars().first() is not None

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing (symbol, ISIN) pairs from the table."""
        result = await session.execute(select(cls.symbol, cls.isin))
        return {(row[0], row[1]) for row in result.fetchall()}


    @classmethod
    async def get_all_results(cls, session, account_id=Env.ZERODHA_USERNAME):
        """Fetch all backtest results asynchronously."""
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()


    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple profit/loss records in bulk."""
        for record in records:
            warning_messages = []

            # Validate and clean data
            if record.buy_value == "":
                record.buy_value = 0.0
                warning_messages.append("Buy value was empty, set to 0.0")
            if record.sell_value == "":
                record.sell_value = 0.0
                warning_messages.append("Sell value was empty, set to 0.0")
            if record.realized_pnl == "":
                record.realized_pnl = 0.0
                warning_messages.append("Realized P&L was empty, set to 0.0")
            if record.timestamp == "":
                record.timestamp = None
                warning_messages.append("Timestamp was empty, set to None")

            if warning_messages:
                record.warning = True
                record.msg = "; ".join(warning_messages)

        session.add_all(records)
        await session.commit()
