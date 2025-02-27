from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, Float

from utils.config_loader import sc
from .base import Base


class Trades(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(String, unique=True, nullable=False)
    trading_symbol = Column(String, nullable=False)
    exchange = Column(String, nullable=False)  # NSE/BSE
    transaction_type = Column(String, nullable=False)  # BUY/SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.indian_timezone)))  # Keep UTC for consistency