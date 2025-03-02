from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DateTime, select, DECIMAL, text
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from .base import Base


def to_decimal(value):
    """Convert float to Decimal with 2 decimal places."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class Holdings(Base):
    """Model to store portfolio holdings matching Zerodha Kite API."""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trading_symbol = Column(String, nullable=False, index=True)  # Indexed for faster lookups
    exchange = Column(String, nullable=False)  # NSE/BSE
    quantity = Column(Integer, nullable=False)
    average_price = Column(DECIMAL(10, 2), nullable=False)  # 2 decimal places
    current_price = Column(DECIMAL(10, 2), nullable=True)  # 2 decimal places
    pnl = Column(DECIMAL(10, 2), nullable=True)  # 2 decimal places
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    def __repr__(self):
        return f"<Holding {self.trading_symbol} ({self.quantity} @ {self.average_price})>"

    @classmethod
    def from_api_data(cls, data):
        """Converts API response data into a Holdings instance with Decimal values."""
        return cls(
            trading_symbol=data["tradingsymbol"],
            exchange=data["exchange"],
            quantity=int(data["quantity"]),
            average_price=to_decimal(data["average_price"]),
            current_price=to_decimal(data.get("last_price", 0.0)),
            pnl=to_decimal(data.get("pnl", 0.0)),
        )

    @classmethod
    async def get_all_holdings(cls, session: AsyncSession):
        """Fetch all holdings from the database asynchronously."""
        result = await session.execute(select(cls))
        return result.scalars().all()
