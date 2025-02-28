from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, Float, JSON

from utils.config_loader import sc
from .base import Base


class OptionStrategies(Base):
    __tablename__ = "option_strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String, nullable=False)
    legs = Column(JSON, nullable=False)  # JSON format: [{"symbol": "NIFTY 18500 CE", "qty": -1}, {...}]
    max_profit = Column(Float, nullable=True)
    max_loss = Column(Float, nullable=True)
    breakeven_points = Column(JSON, nullable=True)  # List of breakeven points
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))
