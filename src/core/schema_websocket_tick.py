from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SchemaWebsocketTick(BaseModel):
    instrument_token: int
    last_price: Optional[float]
    last_traded_quantity: Optional[int]
    average_price: Optional[float]
    volume_traded: Optional[int]
    total_buy_quantity: Optional[int]
    total_sell_quantity: Optional[int]

    ohlc_open: Optional[float]
    ohlc_high: Optional[float]
    ohlc_low: Optional[float]
    ohlc_close: Optional[float]

    change: Optional[float]

    last_trade_time: Optional[datetime]
    exchange_timestamp: Optional[datetime]

    oi: Optional[int]
    oi_day_high: Optional[int]
    oi_day_low: Optional[int]

    depth: Optional[str]
    tradable: Optional[bool]
    mode: Optional[str]
