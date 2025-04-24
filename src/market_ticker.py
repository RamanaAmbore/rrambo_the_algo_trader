import threading
import time

from kiteconnect import KiteTicker

from src.core.decorators import retry_kite_conn
from src.core.singleton_base import SingletonBase
from src.helpers.date_time_utils import today_indian, current_time_indian
from src.helpers.logger import get_logger
from src.settings.parameter_manager import parms

logger = get_logger(__name__)


class MarketTicker(SingletonBase, threading.Thread):
    _instance = None
    _lock = threading.Lock()
    instrument_tokens = set()
    MAX_RECONNECT_ATTEMPTS = int(parms.MAX_SOCKET_RECONNECT_ATTEMPTS)
    RECONNECT_BACKOFF = 5  # Seconds, optional exponential backoff

    def __init__(self, kite_obj, start_time, end_time):
        with MarketTicker._lock:
            if getattr(self, '_singleton_initialized', False):
                logger.debug(f"{self.__class__.__name__} already initialized.")
                return
            self._singleton_initialized = True

        super().__init__(daemon=True)

        # Setup internal state
        self.kite = kite_obj
        self.socket_conn = None
        self.running = True
        self.last_checked_date = None
        self.start_time = start_time
        self.end_time = end_time

        logger.info("MarketTicker thread initialized.")

    @retry_kite_conn(parms.MAX_KITE_CONN_RETRY_COUNT)
    def setup_socket_conn(self):
        if self.is_market_open():
            if self.socket_conn:
                return

            self.socket_conn = KiteTicker(self.kite.api_key, self.kite.get_access_token())
            self.socket_conn.on_ticks = self.on_ticks
            self.socket_conn.on_connect = self.on_connect
            self.socket_conn.on_close = self.on_close
            self.socket_conn.on_error = self.on_error
            self.socket_conn.on_reconnect = self.on_reconnect
            self.socket_conn.connect(threaded=True)

    def is_market_open(self):
        today = today_indian()
        current_time = current_time_indian()

        if self.last_checked_date != today:
            self.last_checked_date = today

        # return self.start_time <= current_time <= self.end_time
        return True
    def run(self):
        logger.info("MarketTicker started.")
        while self.running:
            try:
                if self.is_market_open():
                    logger.debug("Market is open. Ensuring WebSocket is active.")
                    self.setup_socket_conn()
                else:
                    logger.debug("Market is closed. WebSocket not required.")
                    self.close_socket()
                    return

                time.sleep(parms.KITE_SOCKET_SLEEP)  # Tune this as needed for responsiveness vs. CPU

            except Exception as e:
                logger.error(f"Error in MarketTicker loop: {e}")
                raise

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
        logger.warning(f"WebSocket connection closed: {reason}...")
        if "TokenException" in str(reason) or "Invalid access token" in str({"" if reason is None else reason}):
            logger.error("Access token may be invalid. Re-authenticating...")
            try:
                logger.info("Reinitializing WebSocket with new token...")
                self.setup_socket_conn()
            except Exception as e:
                logger.error(f"Failed to re-authenticate: {e}")
        else:
            self.reconnect_attempts += 1
            time.sleep(min(self.RECONNECT_BACKOFF * (2 ** self.reconnect_attempts), 60))
            self.setup_socket_conn()

    @classmethod
    def on_error(cls, ws, code, reason):
        logger.error(f"WebSocket error {code}: {reason}")

    @classmethod
    def on_reconnect(cls, ws, attempts):
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
