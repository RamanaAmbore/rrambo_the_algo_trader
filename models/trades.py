from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import (Column, Integer, String, SmallInteger, DECIMAL, DateTime, Boolean, Enum, Index, text, select,
                        BigInteger)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from utils.config_loader import sc  # Import settings
from utils.date_time_utils import timestamp_indian
from .base import Base
class TradeTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class Trades(Base):
    """Unified model for trades from API, Equity Tradebook, and Options Tradebook."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers
    trade_id = Column(BigInteger, unique=True, nullable=False, index=True)  # Changed to BigInteger
    order_id = Column(BigInteger, nullable=False, index=True)  # Changed to BigInteger
    trading_symbol = Column(String, nullable=False, index=True)
    isin = Column(String, nullable=True, index=True)  # Not always available
    exchange = Column(String, nullable=False)  # NSE/BSE
    segment = Column(String, nullable=False)  # e.g., EQ, F&O, CDS
    series = Column(String, nullable=False)  # e.g., EQ for stocks, CE/PE for options
    trade_type = Column(String, nullable=False)  # BUY/SELL
    auction = Column(Boolean, default=False)  # True if auction trade

    # Trade Details
    quantity = Column(SmallInteger, nullable=False)  # Memory-efficient for small range
    price = Column(DECIMAL(10, 2), nullable=False)  # Precise storage

    # DateTime Fields
    trade_date = Column(DateTime(timezone=True), nullable=False)
    order_execution_time = Column(DateTime(timezone=True), nullable=False)

    # Options-Specific Field
    expiry_date = Column(DateTime(timezone=True), nullable=True)  # Only for Options

    # Equity / Options Indicator
    instrument_type = Column(String, nullable=False)

    # Timestamp (replacing created_at)
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    # Composite index for fast queries on symbol & time
    __table_args__ = (Index("idx_trades_symbol_exchange_date", "trading_symbol", "exchange", "trade_date"),)

    @classmethod
    def from_api_data(cls, trade_data):
        """Creates a Trades object from API data."""
        return cls(trade_id=trade_data["trade_id"], order_id=trade_data["order_id"],
            trading_symbol=trade_data["symbol"], isin=trade_data.get("isin"), exchange=trade_data["exchange"],
            segment=trade_data["segment"], series=trade_data["series"], trade_type=trade_data["trade_type"],
            auction=trade_data.get("auction", False), quantity=trade_data["quantity"], price=trade_data["price"],
            trade_date=datetime.strptime(trade_data["trade_date"], "%Y-%m-%d").replace(
                tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE)),
            order_execution_time=datetime.strptime(trade_data["order_execution_time"], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE)),
            expiry_date=datetime.strptime(trade_data["expiry_date"], "%Y-%m-%d").replace(
                tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE)) if trade_data.get("expiry_date") else None,
            instrument_type="Options" if trade_data.get("expiry_date") else "Equity", )

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
