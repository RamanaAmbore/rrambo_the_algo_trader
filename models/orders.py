from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, select, JSON
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
from .base import Base


def timestamp_indian():
    return datetime.now()


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=False)
    placed_by = Column(String, nullable=False)
    order_id = Column(String, nullable=False, unique=True)
    exchange_order_id = Column(String, nullable=True)
    parent_order_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    status_message = Column(String, nullable=True)
    status_message_raw = Column(String, nullable=True)
    order_timestamp = Column(DateTime, nullable=False)
    exchange_update_timestamp = Column(DateTime, nullable=True)
    exchange_timestamp = Column(DateTime, nullable=True)
    variety = Column(String, nullable=False)
    modified = Column(Boolean, default=False)
    exchange = Column(String, nullable=False)
    tradingsymbol = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    validity = Column(String, nullable=False)
    validity_ttl = Column(Integer, default=0)
    product = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    disclosed_quantity = Column(Integer, default=0)
    price = Column(Numeric(10, 2), default=0)
    trigger_price = Column(Numeric(10, 2), default=0)
    average_price = Column(Numeric(10, 2), default=0)
    filled_quantity = Column(Integer, default=0)
    pending_quantity = Column(Integer, default=0)
    cancelled_quantity = Column(Integer, default=0)
    market_protection = Column(Integer, default=0)
    meta = Column(JSON, nullable=True)
    tag = Column(String, nullable=True)
    guid = Column(String, nullable=True)
    timestamp = Column(DateTime, default=timestamp_indian)

    @classmethod
    async def get_all_orders(cls, session: AsyncSession):
        result = await session.execute(select(cls))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        return cls(**data)

    def __repr__(self):
        return f"<Orders(order_id={self.order_id}, tradingsymbol={self.tradingsymbol}, status={self.status})>"
