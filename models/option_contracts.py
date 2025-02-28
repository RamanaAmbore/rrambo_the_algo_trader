from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, Integer, String, DateTime, Float

from utils.config_loader import sc
from .base import Base


class OptionContracts(Base):
    __tablename__ = "option_contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_token = Column(Integer, unique=True, nullable=False)
    trading_symbol = Column(String, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    strike_price = Column(Float, nullable=False)
    option_type = Column(String, nullable=False)  # CE (Call) / PE (Put)
    lot_size = Column(Integer, nullable=False)
    tick_size = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)))
