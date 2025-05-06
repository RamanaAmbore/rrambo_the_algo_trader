# src/backend/ticks/tick_service.py
from datetime import datetime
from flask import current_app

from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.backend.ticks.tick_model import TickModel
from src.backend.ticks.tick_queue_manager import TickQueueManager

logger = get_logger(__name__)


class TickService(SingletonBase):
    """Service to process and distribute ticks from WebSocket"""

    def __init__(self):
        self.queue_manager = TickQueueManager()

    def process_ticks(self, ticks):
        """Process incoming ticks and update services"""
        processed_models = []

        for tick in ticks:
            # Original tick processing
            model = self._convert_to_model(tick)
            processed_models.append(model)
            self.queue_manager.enqueue(model)

        # Update intraday data for charts
        try:
            self._update_intraday_charts(ticks)
        except Exception as e:
            logger.error(f"Error updating intraday chart data: {e}", exc_info=True)

        return processed_models

    def _update_intraday_charts(self, ticks):
        """Update intraday chart data with ticks"""
        try:
            # Try different approaches to find the app context
            app = None

            # First try current_app
            if current_app:
                try:
                    app = current_app._get_current_object()
                except Exception:
                    pass

            # If app context found and has intraday service
            if app and hasattr(app, 'intraday_data_service') and app.intraday_data_service:
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
            else:
                # Alternative: Use the module directly
                from src.backend.stock_charts.tick_integration import update_intraday_data_with_ticks
                update_intraday_data_with_ticks(ticks)

        except Exception as e:
            logger.error(f"Error updating intraday chart data: {e}", exc_info=True)

    def _convert_to_model(self, tick_dict):
        """Convert a tick dictionary to a TickModel"""
        # Your existing implementation...
        model = TickModel(
            instrument_token=tick_dict.get('instrument_token'),
            last_price=tick_dict.get('last_price'),
            # Add other fields as needed
        )
        return model