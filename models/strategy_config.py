from sqlalchemy import Column, Integer, String, DateTime, JSON, text

from utils.date_time_utils import timestamp_indian
from .base import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String, unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)  # Entry, exit rules
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))