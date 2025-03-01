from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, JSON

from utils.config_loader import sc
from .base import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String, unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)  # Entry, exit rules
    timestamp = Column(DateTime(timezone=True), default=datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))