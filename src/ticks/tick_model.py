from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TickModel:
    instrument_token: int
    last_price: float
    last_traded_quantity: Optional[int] = None
    average_traded_price: Optional[float] = None
    volume_traded: Optional[int] = None
    total_buy_quantity: Optional[int] = None
    total_sell_quantity: Optional[int] = None
    ohlc_open: Optional[float] = None
    ohlc_high: Optional[float] = None
    ohlc_low: Optional[float] = None
    ohlc_close: Optional[float] = None
    change: Optional[float] = None
    exchange_timestamp: Optional[datetime] = None
    oi: Optional[int] = None
    oi_day_high: Optional[int] = None
    oi_day_low: Optional[int] = None
