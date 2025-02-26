import time
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models.market_hours import MarketHours
from utils.logger import get_logger

logger = get_logger(__name__)

class MarketMonitor(threading.Thread):
    """Thread to monitor market hours and manage WebSocket connection."""

    def __init__(self, kite_instance):
        super().__init__()
        self.kite = kite_instance
        self.running = True

    def run(self):
        """Continuously monitor market hours and open/close WebSocket accordingly."""
        while self.running:
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            market_hours = MarketHours.get_market_hours_for_today()

            if not market_hours:
                weekday = now.weekday()  # 0 = Monday, 6 = Sunday
                logger.warning(f"No market hours found for today. Using default for weekday {weekday}.")
                market_hours = MarketHours.get_default_hours_for_weekday(weekday)

            market_open = market_hours.open_time
            market_close = market_hours.close_time

            if market_open <= now < market_close:
                if not self.kite.socket_conn:
                    logger.info("Market is open. Starting WebSocket connection.")
                    self.kite._setup_socket_conn()
            else:
                if self.kite.socket_conn:
                    logger.info("Market is closed. Closing WebSocket connection.")
                    self.kite.socket_conn.close()
                    self.kite.socket_conn = None

            time.sleep(30)  # Check every 30 seconds
