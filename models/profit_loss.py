from sqlalchemy import Column, Integer, String, DECIMAL, Enum, Index, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from utils.date_time_utils import timestamp_indian

Base = declarative_base()

class ProfitLoss(Base):
    """Model for profit and loss data."""

    __tablename__ = "profit_loss"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    quantity = Column(Integer, nullable=False)
    buy_value = Column(DECIMAL(12, 2), nullable=False)
    sell_value = Column(DECIMAL(12, 2), nullable=False)
    realized_pnl = Column(DECIMAL(12, 2), nullable=False)
    realized_pnl_pct = Column(DECIMAL(6, 2), nullable=False)
    previous_closing_price = Column(DECIMAL(10, 2), nullable=True)
    open_quantity = Column(Integer, nullable=False, default=0)
    open_quantity_type = Column(Enum("BUY", "SELL", name="open_quantity_type_enum"), nullable=False)
    open_value = Column(DECIMAL(12, 2), nullable=False)
    unrealized_pnl = Column(DECIMAL(12, 2), nullable=False)
    unrealized_pnl_pct = Column(DECIMAL(6, 2), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (Index("idx_symbol_timestamp", "symbol", "timestamp"),)

    @classmethod
    async def exists(cls, session, symbol, isin):
        """Check if a profit-loss record exists for a symbol & ISIN."""
        result = await session.execute(select(cls).where(cls.symbol == symbol, cls.isin == isin))
        return result.scalars().first() is not None

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing (symbol, ISIN) pairs from the table."""
        result = await session.execute(select(cls.symbol, cls.isin))
        return {(row[0], row[1]) for row in result.fetchall()}

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple profit/loss records in bulk."""
        session.add_all(records)
        await session.commit()

