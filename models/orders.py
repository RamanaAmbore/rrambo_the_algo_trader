from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DECIMAL, SmallInteger, DateTime, Index, func

from utils.config_loader import sc  # Import settings
from .base import Base


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, nullable=False, index=True)  # Indexed for fast lookups
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)  # NSE/BSE
    status = Column(String, nullable=False)  # OPEN, COMPLETED, CANCELED
    order_type = Column(String, nullable=False)  # MARKET/LIMIT
    quantity = Column(SmallInteger, nullable=False)  # Memory-efficient if range is small
    price = Column(DECIMAL(10, 2), nullable=True)  # Precise storage instead of Float
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))

    # Composite index for faster queries on symbol, exchange, and time
    __table_args__ = (
        Index("idx_order_trading_symbol_exchange_time", "trading_symbol", "exchange", "timestamp"),
    )

    @classmethod
    def from_api_data(cls, order_data):
        """Creates an Orders object from API data."""
        return cls(
            order_id=order_data["order_id"],
            trading_symbol=order_data["tradingsymbol"],
            exchange=order_data["exchange"],
            status=order_data["status"],
            order_type=order_data["order_type"],
            quantity=order_data["quantity"],
            price=order_data.get("average_price", None),  # Handle missing price gracefully
            timestamp=datetime.strptime(order_data["order_timestamp"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE))
        )

    @classmethod
    async def get_all_orders(cls, session):
        """Fetch all orders asynchronously."""
        return await session.execute(cls.__table__.select())

