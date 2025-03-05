from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, select, text, Numeric
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from .base import Base


def timestamp_indian():
    return datetime.now()


class Positions(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tradingsymbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    product = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    overnight_quantity = Column(Integer, default=0)
    multiplier = Column(Integer, default=1)
    average_price = Column(Numeric(10, 2), default=0)
    close_price = Column(Numeric(10, 2), default=0)
    last_price = Column(Numeric(10, 2), default=0)
    value = Column(Numeric(12, 2), default=0)
    pnl = Column(Numeric(12, 2), default=0)
    m2m = Column(Numeric(12, 2), default=0)
    unrealised = Column(Numeric(12, 2), default=0)
    realised = Column(Numeric(12, 2), default=0)
    buy_quantity = Column(Integer, default=0)
    buy_price = Column(Numeric(10, 2), default=0)
    buy_value = Column(Numeric(12, 2), default=0)
    buy_m2m = Column(Numeric(12, 2), default=0)
    sell_quantity = Column(Integer, default=0)
    sell_price = Column(Numeric(10, 2), default=0)
    sell_value = Column(Numeric(12, 2), default=0)
    sell_m2m = Column(Numeric(12, 2), default=0)
    day_buy_quantity = Column(Integer, default=0)
    day_buy_price = Column(Numeric(10, 2), default=0)
    day_buy_value = Column(Numeric(12, 2), default=0)
    day_sell_quantity = Column(Integer, default=0)
    day_sell_price = Column(Numeric(10, 2), default=0)
    day_sell_value = Column(Numeric(12, 2), default=0)
    timestamp = Column(DateTime, default=timestamp_indian)

    @classmethod
    async def get_all_positions(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        return cls(**data)

    def __repr__(self):
        return f"<Positions(tradingsymbol={self.tradingsymbol}, exchange={self.exchange}, quantity={self.quantity})>"
