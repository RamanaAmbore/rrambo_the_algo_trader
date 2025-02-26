from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Position(Base):
    """Model to store open positions matching Zerodha Kite API."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trading_symbol = Column(String, nullable=False, index=True)
    exchange = Column(String, nullable=False)
    instrument_token = Column(Integer, nullable=False, unique=True)
    quantity = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    last_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True, comment="Profit and Loss")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Position {self.trading_symbol} ({self.quantity} @ {self.avg_price})>"

