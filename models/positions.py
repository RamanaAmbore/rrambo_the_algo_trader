from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from .base import Base


def to_decimal(value, precision="0.01"):
    """Convert float to Decimal with given precision (default: 2 decimal places)."""
    return Decimal(value).quantize(Decimal(precision), rounding=ROUND_DOWN)


class Positions(Base):
    """Model to store open positions matching Zerodha Kite API."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(DECIMAL(12, 2), nullable=False)  # Decimal for accuracy
    last_price = Column(DECIMAL(12, 2), nullable=True)
    pnl = Column(DECIMAL(12, 2), nullable=True, comment="Profit and Loss")
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    def __repr__(self):
        return f"<Position {self.trading_symbol} ({self.quantity} @ {self.avg_price})>"

    @classmethod
    def from_api_data(cls, data):
        """Converts API response data into a Positions instance."""
        return cls(
            trading_symbol=data["tradingsymbol"],
            exchange=data["exchange"],
            instrument_token=data["instrument_token"],
            quantity=data["quantity"],
            avg_price=to_decimal(data["average_price"]),
            last_price=to_decimal(data.get("last_price", 0.0)),  # Default to 0.0 if missing
            pnl=to_decimal(data.get("unrealised_pnl", 0.0)),
            timestamp=timestamp_indian()  # Correctly assigning timestamp
        )

    @classmethod
    async def get_all_positions(cls, session: AsyncSession):
        """Fetch all positions asynchronously."""
        result = await session.execute(select(cls))
        return result.scalars().all()

