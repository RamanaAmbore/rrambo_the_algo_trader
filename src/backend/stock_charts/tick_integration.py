# src/stock_charts/tick_integration.py
from flask import current_app
from datetime import datetime

from src.helpers.logger import get_logger

logger = get_logger(__name__)


def update_intraday_data_with_ticks(ticks):
    """
    Helper function to update intraday data with ticks from TickService

    Args:
        ticks: List of ticks from WebSocket

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        app = current_app._get_current_object() if current_app else None

        if not app or not hasattr(app, 'intraday_data_service') or not app.intraday_data_service:
            logger.warning("Cannot update intraday data - service not initialized")
            return False

        for tick in ticks:
            instrument_token = tick.get('instrument_token')
            price = tick.get('last_price')
            timestamp = tick.get('exchange_timestamp', datetime.now())
            volume = tick.get('last_traded_quantity')

            if price and instrument_token:
                app.intraday_data_service.append_tick_data(
                    instrument_token=instrument_token,
                    price=price,
                    timestamp=timestamp,
                    volume=volume
                )

        return True

    except Exception as e:
        logger.error(f"Error updating intraday data with ticks: {e}", exc_info=True)
        return False