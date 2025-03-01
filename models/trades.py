from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, SmallInteger, Index, func

from utils.config_loader import sc  # Import settings
from .base import Base


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String, unique=True, nullable=False, index=True)  # Indexed for fast lookups
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)  # NSE/BSE
    transaction_type = Column(String, nullable=False)  # BUY/SELL
    quantity = Column(SmallInteger, nullable=False)  # Memory-efficient if range is small
    price = Column(DECIMAL(10, 2), nullable=False)  # Precise storage instead of Float
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))   # Database-managed timestamp

    # Composite index for faster queries on symbol, exchange, and time
    __table_args__ = (
        Index("idx_trading_symbol_exchange_time", "trading_symbol", "exchange", "timestamp"),
    )

    @classmethod
    def from_api_data(cls, trade_data):
        """Creates a Trades object from API data."""
        return cls(
            trade_id=trade_data["order_id"],
            trading_symbol=trade_data["tradingsymbol"],
            exchange=trade_data["exchange"],
            transaction_type=trade_data["transaction_type"],
            quantity=trade_data["quantity"],
            price=trade_data["average_price"],
            timestamp=datetime.strptime(trade_data["exchange_timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE))
        )

    @classmethod
    async def get_all_trades(cls, session):
        """Fetch all trades asynchronously."""
        return await session.execute(cls.__table__.select())
