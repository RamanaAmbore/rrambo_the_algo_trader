# src/stock_charts/services.py
"""
Convenience imports for stock chart services

This module provides easy access to the main services used for stock charts.
"""

from src.backend.stock_charts.base_data_service import BaseDataService
from src.backend.stock_charts.historical_data_service import HistoricalDataService
from src.backend.stock_charts.intraday_data_service import IntradayDataService

# Import analysis functions if you've moved them to their own file
try:
    from src.backend.stock_charts.analysis_utils import (
        calculate_sma, calculate_ema, calculate_rsi, calculate_macd,
        calculate_bollinger_bands, calculate_atr, detect_support_resistance,
        calculate_fibonacci_levels, identify_patterns, enhance_dataframe,
        generate_trading_signals, get_daily_recommendation,
        perform_portfolio_simulation, generate_market_analysis_report
    )
except ImportError:
    # Analysis utilities might be imported from elsewhere
    pass

__all__ = [
    'BaseDataService',
    'HistoricalDataService',
    'IntradayDataService',
    # Add analysis functions to __all__ if imported above
]