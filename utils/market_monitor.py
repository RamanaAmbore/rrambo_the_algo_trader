import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from models.market_hours import MarketHours
from utils.config_loader import sc
from utils.logger import get_logger
from db_conn import DbConnection as db

logger = get_logger(__name__)

class MarketMonitor(threading.Thread):
    """Thread to monitor market hours and manage WebSocket connection (Singleton)."""

    _instance = None
    _lock = threading.Lock()  # Lock to ensure thread safety

    def __new__(cls, socket_conn):
        """Ensure only one instance of MarketMonitor is created."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False  # Mark instance as not initialized
        return cls._instance

    def __init__(self, socket_conn):
        """Initialize MarketMonitor thread."""
        with self._lock:
            if not self._initialized:  # Ensure init runs only once
                super().__init__(daemon=True)
                self.socket_conn = socket_conn
                self.running = True
                self.market_hours = None
                self.last_checked_date = None
                self.is_market_open = False
                self._initialized = True  # Mark as initialized

    def fetch_market_hours(self):
        """Fetch market hours once per day to reduce DB queries."""
        now = datetime.now(ZoneInfo(sc.indian_timezone))
        today = now.date()

        if self.last_checked_date != today or self.market_hours is None:
            session = db.get_session(async_mode=False)  # Ensure session is retrieved
            self.market_hours = MarketHours.get_market_hours_for_today(session)
            if not self.market_hours:
                msg = f"No market hours record found in market hours table for {today}"
                logger.error(msg)
                raise Exception(msg)

            self.last_checked_date = today  # Update last checked date

    def run(self):
        """Continuously monitor market hours and open/close WebSocket accordingly."""
        while self.running:
            now = datetime.now(ZoneInfo(sc.indian_timezone))
            self.fetch_market_hours()  # Fetch only if date changes

            if self.market_hours:
                market_open = self.market_hours.start_time
                market_close = self.market_hours.end_time
                is_market_open = self.market_hours.is_market_open and market_open <= now.time() < market_close

                if is_market_open and not self.socket_conn.socket_conn:
                    logger.info("Market is open. Starting WebSocket connection.")
                    self.socket_conn._setup_socket_conn()
                elif not is_market_open and self.socket_conn.socket_conn:
                    logger.info("Market is closed. Closing WebSocket connection.")
                    self.socket_conn.socket_conn.close()
                    self.socket_conn.socket_conn = None

            time.sleep(30)  # Check every 30 seconds

    @classmethod
    def stop(cls):
        """Stop the MarketMonitor thread safely."""
        with cls._lock:
            if cls._instance:
                cls._instance.running = False
                cls._instance.join()  # Ensure thread exits cleanly
                cls._instance = None
