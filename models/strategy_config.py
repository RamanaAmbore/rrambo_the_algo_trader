from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON

from .base import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_name = Column(String, unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)  # Entry, exit rules
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)