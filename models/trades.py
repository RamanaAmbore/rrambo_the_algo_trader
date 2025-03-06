from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, Numeric, Integer, select, DateTime, text, Boolean, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from utils.settings_loader import Env
from utils.date_time_utils import INDIAN_TIMEZONE
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)  # Initialize logger


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)
    trade_id = Column(BigInteger, unique=True, nullable=False, index=True)
    order_id = Column(BigInteger, nullable=False, index=True)
    trading_symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)
    exchange = Column(String, nullable=False)
    segment = Column(String, nullable=False)
    series = Column(String, nullable=False)
    trade_type = Column(String, nullable=False)
    auction = Column(Boolean, default=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    trade_date = Column(DateTime(timezone=True), nullable=False)
    order_execution_time = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    instrument_type = Column(String, nullable=False)
    source = Column(String, nullable=True, default="SCHEDULE")
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    def __repr__(self):
        return f"<Trade {self.trade_id} - {self.trading_symbol} {self.trade_type} {self.quantity} @ {self.price}>"

    @classmethod
    async def get_all_trades(cls, session: AsyncSession):
        """Fetch all trades asynchronously."""
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    async def exists(cls, session: AsyncSession, trade_id: str):
        """Check if a trade already exists."""
        result = await session.execute(select(cls).where(cls.trade_id == trade_id))
        return result.scalars().first() is not None

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing trade IDs from the table."""
        result = await session.execute(select(cls.trade_id))
        return set(result.scalars().all())

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple trade records in bulk."""
        session.add_all(records)
        await session.flush()  # Ensure IDs are assigned before commit
        await session.commit()

    def __repr__(self):
        return f"<Trade {self.trade_id} - {self.trading_symbol} {self.trade_type} {self.quantity} @ {self.price}>"