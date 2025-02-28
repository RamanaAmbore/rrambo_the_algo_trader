from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, Float

from utils.config_loader import sc
from .base import Base


class Orders(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, nullable=False)
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    status = Column(String, nullable=False)  # OPEN, COMPLETED, CANCELED
    order_type = Column(String, nullable=False)  # MARKET/LIMIT
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))  # Keep UTC for consistency
