from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey

from utils.config_loader import sc
from .base import Base


class OptionGreeks(Base):
    __tablename__ = "option_greeks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(Integer, ForeignKey("option_contracts.instrument_token", ondelete="CASCADE"), nullable=False)
    delta = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    iv = Column(Float, nullable=True)  # Implied Volatility
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=ZoneInfo(sc.indian_timezone)))