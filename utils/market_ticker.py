import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from kiteconnect import KiteTicker
from db_conn import DbConnection as db
from models.market_hours import MarketHours
from utils.config_loader import sc
from utils.logger import get_logger
from zerodha_kite import ZerodhaKite

logger = get_logger(__name__)

class MarketTicker(threading.Thread):
    _instance = None
    _lock = threading.Lock()  # Lock to ensure thread safety
    instrument_tokens = set()

    def __new__(cls):
        """Ensure only one instance of MarketMonitor is created."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the thread (only once)."""
        with self._lock:
            if not hasattr(self, "_initialized") or not self._initialized:
                super().__init__(daemon=True)
                self.kite_conn = ZerodhaKite
                self.socket_conn = None
                self.running = True
                self.market_hours = None
                self.last_checked_date = None
                self.is_market_open = False
                self._initialized = True
                logger.info("Starting MarketMonitor thread")
                self.start()  # Start the thread

    def fetch_market_hours(self):
        """Fetch market hours once per day to reduce DB queries."""
        now = datetime.now(ZoneInfo(sc.indian_timezone))
        today = now.date()

        if self.last_checked_date != today or self.market_hours is None:
            session = db.get_session(async_mode=False)
            self.market_hours = MarketHours.get_market_hours_for_today(session)
            if not self.market_hours:
                msg = f"No market hours record found in market hours table for {today}"
                logger.error(msg)
                raise Exception(msg)

            self.last_checked_date = today

    def run(self):
        """Thread function that runs continuously until stopped."""
        while self.running:
            now = datetime.now(ZoneInfo(sc.indian_timezone))
            self.fetch_market_hours()
            if self.market_hours:
                market_open = self.market_hours.start_time
                market_close = self.market_hours.end_time
                is_market_open = self.market_hours.is_market_open and market_open <= now.time() < market_close
                if is_market_open and not self.socket_conn:
                    logger.info("Market is open. Starting WebSocket connection.")
                    self.setup_socket_conn()
                elif not is_market_open and self.socket_conn:
                    logger.info("Market is closed. Closing WebSocket connection.")
                    self.close_socket()
            time.sleep(30)

    def setup_socket_conn(self):
        """Initializes WebSocket connection."""
        logger.info("Starting new WebSocket connection...")
        self.socket_conn = KiteTicker(self.kite_conn.api_key, self.kite_conn._access_token)
        self.socket_conn.on_ticks = self.on_ticks
        self.socket_conn.on_connect = self.on_connect
        self.socket_conn.on_close = self.on_close
        self.socket_conn.on_error = self.on_error
        self.socket_conn.on_reconnect = self.on_reconnect
        self.socket_conn.connect(threaded=True)

    def close_socket(self):
        if self.socket_conn:
            logger.info("Closing WebSocket connection...")
            self.socket_conn.close()
            self.socket_conn = None

    def on_connect(self, ws, response):
        """Subscribes to instrument tokens when WebSocket connects."""
        if self.instrument_tokens:
            ws.subscribe(list(self.instrument_tokens))
            ws.set_mode(ws.MODE_FULL, list(self.instrument_tokens))
            logger.info(f"Subscribed to tokens: {self.instrument_tokens}")

    def on_ticks(self, ws, ticks):
        """Handles incoming market data."""
        logger.info(f"Received tick data: {ticks}")

    def on_close(self, ws, code, reason):
        """Handles WebSocket connection closure and re-authenticates if needed."""
        logger.warning(f"WebSocket closed: {reason}. Reconnecting...")

        if "TokenException" in str(reason) or "Invalid access token" in str(reason):
            logger.error("Access token may be invalid. Re-authenticating...")
            try:
                # Refresh Zerodha connection
                self.kite_conn.get_kite_conn()

                # Reinitialize WebSocket like a fresh start
                logger.info("Reinitializing WebSocket with new token...")
                self.setup_socket_conn()
            except Exception as e:
                logger.error(f"Failed to re-authenticate: {e}")
        else:
            # Reconnect WebSocket normally
            self.setup_socket_conn()

    def on_error(self, ws, code, reason):
        """Handles WebSocket errors."""
        logger.error(f"WebSocket error {code}: {reason}")

    def on_reconnect(self, ws, attempts):
        """Handles WebSocket reconnection attempts."""
        logger.info(f"WebSocket reconnecting, attempt {attempts}...")

    @classmethod
    def add_instruments(cls, tokens):
        """Adds instrument tokens to subscribe to."""
        with cls._lock:
            cls.instrument_tokens.update(tokens)
            if cls._instance and cls._instance.socket_conn:
                cls._instance.socket_conn.subscribe(list(cls.instrument_tokens))
                cls._instance.socket_conn.set_mode(cls._instance.socket_conn.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to new tokens: {cls.instrument_tokens}")

    @classmethod
    def remove_instruments(cls, tokens):
        """Removes instrument tokens from subscription."""
        with cls._lock:
            cls.instrument_tokens.difference_update(tokens)
            if cls._instance and cls._instance.socket_conn:
                cls._instance.socket_conn.unsubscribe(list(tokens))
                logger.info(f"Unsubscribed from tokens: {tokens}")

    @classmethod
    def stop(cls):
        """Stop the MarketMonitor thread safely."""
        with cls._lock:
            if cls._instance:
                logger.info("Stopping MarketMonitor thread")
                cls._instance.running = False
                cls._instance.join()
                cls._instance = None

if __name__ == '__main__':
    market_monitor = MarketTicker()
    market_monitor.add_instruments([738561, 5633])  # Add tokens
    market_monitor.remove_instruments([5633])  # Remove tokens
    time.sleep(1000)

