from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, Date, Numeric, Integer, select, DateTime, text, Boolean, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from utils.config_loader import Env
from utils.date_time_utils import timestamp_indian
from .base import Base
from utils.date_time_utils import INDIAN_TIMEZONE

from utils.logger import get_logger

logger = get_logger(__name__)  # Initialize logger


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
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
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))
    source = Column(String, nullable=True, default="BATCH")
    warning = Column(Boolean, default=False)
    msg = Column(String, nullable=True)

    def __repr__(self):
        return f"<Trade {self.trade_id} - {self.trading_symbol} {self.trade_type} {self.quantity} @ {self.price}>"

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing trade IDs from the table."""
        result = await session.execute(select(cls.trade_id))
        return set(result.scalars().all())

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple trade records in bulk."""
        for record in records:
            warning_messages = []

            # Validate and clean data
            if record.quantity <= 0:
                warning_messages.append("Quantity should be greater than 0")
            if record.price <= 0:
                warning_messages.append("Price should be greater than 0")
            if not record.trade_date:
                warning_messages.append("Trade date is missing")
            if not record.order_execution_time:
                warning_messages.append("Order execution time is missing")

            if warning_messages:
                record.warning = True
                record.msg = "; ".join(warning_messages)

        session.add_all(records)
        await session.commit()

    @classmethod
    def from_api_data(cls, trade_data):
        """Creates a Trades object from API data safely."""
        try:
            exchange_timestamp = trade_data.get("exchange_timestamp")

            # Handle timestamp parsing properly
            if isinstance(exchange_timestamp, str):
                timestamp = datetime.strptime(exchange_timestamp, "%Y-%m-%d %H:%M:%S")
                timestamp = timestamp.replace(tzinfo=ZoneInfo(INDIAN_TIMEZONE))  # Convert to timezone-aware
            elif isinstance(exchange_timestamp, datetime):
                if exchange_timestamp.tzinfo is None:
                    timestamp = exchange_timestamp.replace(tzinfo=ZoneInfo(INDIAN_TIMEZONE))  # Make it timezone-aware
                else:
                    timestamp = exchange_timestamp.astimezone(ZoneInfo(INDIAN_TIMEZONE))  # Convert to desired timezone
            else:
                timestamp = datetime(1970, 1, 1, 0, 0, 0, tzinfo=ZoneInfo(INDIAN_TIMEZONE))  # Fallback default

            return cls(
                trade_id=trade_data.get("trade_id"),
                order_id=trade_data.get("order_id"),
                trading_symbol=trade_data.get("tradingsymbol"),
                exchange=trade_data.get("exchange"),
                transaction_type=trade_data.get("transaction_type"),
                quantity=int(trade_data.get("quantity", 0)),
                price=float(trade_data.get("average_price", 0.0)),
                timestamp=timestamp,  # Corrected timestamp handling
                source="API",
                warning=False,
                msg=None
            )

        except Exception as e:
            logger.error(f"Error processing trade data: {e}")
            return cls(
                trade_id=None,
                order_id=None,
                trading_symbol=None,
                exchange=None,
                transaction_type=None,
                quantity=0,
                price=0.0,
                timestamp=datetime.now().astimezone(ZoneInfo(INDIAN_TIMEZONE)),  # Correct timezone-aware timestamp
                source="API",
                warning=True,
                msg=f"Failed to parse trade data: {e}"
            )