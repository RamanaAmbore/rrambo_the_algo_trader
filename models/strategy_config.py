from sqlalchemy import Column, Integer, String, DateTime, JSON, text, Boolean

from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=True, default=Env.ZERODHA_USERNAME)
    strategy_name = Column(String, unique=True, nullable=False)
    parameters = Column(JSON, nullable=False)  # Entry, exit rules
    source = Column(String, nullable=True, default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    msg = Column(String, nullable=True)
