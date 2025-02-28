from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, Float

from utils.config_loader import sc
from .base import Base


class PortfolioHoldings(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trading_symbol = Column(String, nullable=False, index=True)  # Indexed for faster lookups
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))
