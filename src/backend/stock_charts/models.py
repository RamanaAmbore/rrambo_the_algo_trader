# src/stock_charts/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class HistoricalCandle:
    """Represents an OHLC candle from historical data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: Optional[int] = None  # Open Interest for derivatives


@dataclass
class IntradayCandle:
    """Represents an OHLC candle for intraday data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass
class IntradayTick:
    """Represents a tick data point for intraday charts"""
    timestamp: datetime
    price: float
    volume: Optional[int] = None


@dataclass
class ChartDataPoint:
    """Generic data point for chart rendering that can represent either candle or tick"""
    timestamp: datetime

    # OHLC values for candles (may be None for ticks)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None

    # Single price value for ticks
    price: Optional[float] = None

    # Common fields
    volume: Optional[int] = None
    is_tick: bool = False  # Flag to identify if this is a tick or a candle

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)