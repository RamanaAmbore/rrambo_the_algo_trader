import os
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from kiteconnect import KiteTicker

from db_conn import DbConnection as db
from models.market_hours import MarketHours
from utils.config_loader import sc
from utils.logger import get_logger
from zerodha_kite import ZerodhaKite

load_dotenv()

logger = get_logger(__name__)


class MarketTicker(threading.Thread):
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    instrument_tokens = set()
    MAX_RECONNECT_ATTEMPTS = int(os.getenv('MAX_SOCKET_RECONNECT_ATTEMPTS', 5))
    RECONNECT_BACKOFF = 5  # Seconds, exponential backoff can be implemented

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with self._lock:
            if not self._initialized:
                super().__init__(daemon=True)
                self.init_ticker_state()
                self.reconnect_attempts = 0
                self.start()
                self._initialized = True

    def init_ticker_state(self):
        self.kite_conn = ZerodhaKite
        self.kite_conn.get_kite_conn()
        self.socket_conn = None
        self.running = True
        self.market_hours = None
        self.last_checked_date = None
        self.reconnect_attempts = 0
        logger.info("Starting MarketTicker thread")

    def is_market_open(self):
        now = datetime.now(ZoneInfo(sc.indian_timezone))
        today = now.date()

        if self.last_checked_date != today or self.market_hours is None:
            session = db.get_session(async_mode=False)
            try:
                self.market_hours = MarketHours.get_market_hours_for_today(session)
            finally:
                session.close()
            if not self.market_hours:
                logger.error(f"No market hours record found in market hours table for {today}")
                return False
            self.last_checked_date = today

        market_open = self.market_hours.start_time
        market_close = self.market_hours.end_time
        is_open = self.market_hours.is_market_open and market_open <= now.time() < market_close

        logger.info(
            f"Market open status: {is_open}, Current time: {now.time()}, Market hours: {market_open} - {market_close}")
        return is_open

    def run(self):
        while self.running:
            if self.is_market_open():
                logger.info("Market is open. Ensuring WebSocket is running.")
                self.setup_socket_conn()
            else:
                logger.info("Market is closed. Ensuring WebSocket is stopped.")
                self.close_socket()
            time.sleep(30)

    def setup_socket_conn(self):
        if self.reconnect_attempts >= self.MAX_RECONNECT_ATTEMPTS:
            logger.error("Maximum WebSocket reconnection attempts reached. Stopping reconnect attempts.")
            return

        if self.is_market_open():
            if self.socket_conn:
                logger.info("WebSocket already running. No need to restart.")
                return
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
        self.reconnect_attempts = 0
        with self._lock:
            if self.instrument_tokens:
                ws.subscribe(list(self.instrument_tokens))
                ws.set_mode(ws.MODE_FULL, list(self.instrument_tokens))
                logger.info(f"Subscribed to tokens: {self.instrument_tokens}")

    def on_ticks(self, ws, ticks):
        logger.info(f"Received tick data: {ticks}")

    def on_close(self, ws, code, reason):
        logger.warning(f"WebSocket closed: {reason}...")
        if "TokenException" in str(reason) or "Invalid access token" in str(reason):
            logger.error("Access token may be invalid. Re-authenticating...")
            try:
                self.init_ticker_state()
                logger.info("Reinitializing WebSocket with new token...")
                self.setup_socket_conn()
            except Exception as e:
                logger.error(f"Failed to re-authenticate: {e}")
        else:
            self.reconnect_attempts += 1
            time.sleep(min(self.RECONNECT_BACKOFF * (2 ** self.reconnect_attempts), 60))
            self.setup_socket_conn()

    def on_error(self, ws, code, reason):
        logger.error(f"WebSocket error {code}: {reason}")

    def on_reconnect(self, ws, attempts):
        logger.info(f"WebSocket reconnecting, attempt {attempts}...")

    @classmethod
    def add_instruments(cls, tokens):
        with cls._lock:
            cls.instrument_tokens.update(tokens)
            if cls._instance and cls._instance.socket_conn:
                cls._instance.socket_conn.subscribe(list(tokens))
                cls._instance.socket_conn.set_mode(cls._instance.socket_conn.MODE_FULL, list(tokens))
                logger.info(f"Subscribed to new tokens: {tokens}")

    @classmethod
    def remove_instruments(cls, tokens):
        with cls._lock:
            cls.instrument_tokens.difference_update(tokens)
            if cls._instance and cls._instance.socket_conn:
                cls._instance.socket_conn.unsubscribe(list(tokens))
                logger.info(f"Unsubscribed from tokens: {tokens}")

    @classmethod
    def stop(cls):
        with cls._lock:
            if cls._instance:
                logger.info("Stopping MarketTicker thread")
                cls._instance.running = False
                cls._instance.close_socket()
                cls._instance.join()
                cls._instance = None


if __name__ == '__main__':
    market_ticker = MarketTicker()
    market_ticker.add_instruments([738561, 5633])  # Add tokens
    time.sleep(1)
    market_ticker.remove_instruments([5633])  # Remove tokens
    time.sleep(1000)
