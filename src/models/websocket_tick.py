from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WebsocketTick(Base):
    __tablename__ = 'websocket_tick.py'

    id = Column(Integer, primary_key=True, autoincrement=True)

    instrument_token = Column(Integer, nullable=False)
    last_price = Column(Float)
    last_traded_quantity = Column(Integer)
    average_price = Column(Float)
    volume_traded = Column(BigInteger)
    total_buy_quantity = Column(BigInteger)
    total_sell_quantity = Column(BigInteger)

    ohlc_open = Column(Float)
    ohlc_high = Column(Float)
    ohlc_low = Column(Float)
    ohlc_close = Column(Float)

    change = Column(Float)

    last_trade_time = Column(DateTime)
    exchange_timestamp = Column(DateTime)

    oi = Column(BigInteger)
    oi_day_high = Column(BigInteger)
    oi_day_low = Column(BigInteger)

    depth = Column(String)  # You can store as JSON string if needed
    tradable = Column(Boolean)
    mode = Column(String)

    created_at = Column(DateTime, default=timestamp_indian)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    notes = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<WebSocketTick(token={self.instrument_token}, last_price={self.last_price})>"
