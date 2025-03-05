from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from .base import Base


def timestamp_indian():
    return datetime.now()


class Holdings(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tradingsymbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    isin = Column(String, nullable=True)
    product = Column(String, nullable=False)
    price = Column(Numeric(10, 2), default=0)
    quantity = Column(Integer, default=0)
    used_quantity = Column(Integer, default=0)
    t1_quantity = Column(Integer, default=0)
    realised_quantity = Column(Integer, default=0)
    authorised_quantity = Column(Integer, default=0)
    authorised_date = Column(DateTime, nullable=True)
    authorisation = Column(JSON, nullable=True)
    opening_quantity = Column(Integer, default=0)
    short_quantity = Column(Integer, default=0)
    collateral_quantity = Column(Integer, default=0)
    collateral_type = Column(String, nullable=True)
    discrepancy = Column(Boolean, default=False)
    average_price = Column(Numeric(10, 2), default=0)
    last_price = Column(Numeric(10, 2), default=0)
    close_price = Column(Numeric(10, 2), default=0)
    pnl = Column(Numeric(12, 2), default=0)
    day_change = Column(Numeric(10, 2), default=0)
    day_change_percentage = Column(Numeric(10, 2), default=0)
    mtf = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=timestamp_indian)

    @classmethod
    async def get_all_holdings(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        return cls(**data)

    def __repr__(self):
        return f"<Holdings(tradingsymbol={self.tradingsymbol}, exchange={self.exchange}, quantity={self.quantity})>"
