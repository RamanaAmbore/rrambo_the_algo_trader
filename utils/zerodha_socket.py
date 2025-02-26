import os
import threading
from kiteconnect import KiteTicker, TokenException
from utils.logger import get_logger
from kite_conn import ZerodhaKite
from utils.market_monitor import MarketMonitor

logger = get_logger(__name__)

class ZerodhaSocket:
    """Handles WebSocket connection for live market data."""

    _ticker_lock = threading.Lock()
    socket_conn = None
    instrument_tokens = set()
    kite_conn = ZerodhaKite
    market_monitor = None

    @classmethod
    def get_socket_conn(cls, test_conn=False):
        """Returns WebSocket connection for live market data."""
        cls._setup_socket_conn(test_conn=test_conn)
        return cls.socket_conn

    @classmethod
    def _setup_socket_conn(cls, test_conn=False):
        """Initializes WebSocket connection for real-time market data based on market hours."""
        if cls.market_monitor is None:
            cls.market_monitor = MarketMonitor(cls)
            cls.market_monitor.daemon = True
            cls.market_monitor.start()

        if not cls.market_monitor.is_market_open():
            logger.info("Market is closed. WebSocket will not connect.")
            return

        with cls._ticker_lock:
            if cls.socket_conn:
                logger.info("Closing existing WebSocket connection...")
                cls.socket_conn.close()

            logger.info("Starting new WebSocket connection...")
            cls.socket_conn = KiteTicker(cls.kite_conn.api_key, cls.kite_conn._access_token)
            cls.socket_conn.on_ticks = cls.on_ticks
            cls.socket_conn.on_connect = cls.on_connect
            cls.socket_conn.on_close = cls.on_close
            cls.socket_conn.on_error = cls.on_error
            cls.socket_conn.on_reconnect = cls.on_reconnect
            cls.socket_conn.connect(threaded=True)

    @classmethod
    def on_connect(cls, ws, response):
        """Subscribes to instrument tokens when WebSocket connects."""
        with cls._ticker_lock:
            if cls.instrument_tokens:
                ws.subscribe(list(cls.instrument_tokens))
                ws.set_mode(ws.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to tokens: {cls.instrument_tokens}")

    @classmethod
    def on_ticks(cls, ws, ticks):
        """Handles incoming market data."""
        logger.info(f"Received tick data: {ticks}")

    @classmethod
    def on_close(cls, ws, code, reason):
        """Handles WebSocket connection closure and attempts to reconnect."""
        logger.warning(f"WebSocket connection closed: {reason}. Reconnecting...")

        if "TokenException" in str(reason) or "Invalid access token" in str(reason):
            logger.error("Access token may be invalid. Re-authenticating...")
            cls.kite_conn.get_kite_conn()

        cls.get_socket_conn()

    @classmethod
    def on_error(cls, ws, code, reason):
        """Handles WebSocket errors."""
        logger.error(f"WebSocket error {code}: {reason}")

    @classmethod
    def on_reconnect(cls, ws, attempts):
        """Handles WebSocket reconnection attempts."""
        logger.info(f"WebSocket reconnecting, attempt {attempts}...")

    @classmethod
    def add_instruments(cls, tokens):
        """Adds instrument tokens to subscribe to."""
        with cls._ticker_lock:
            cls.instrument_tokens.update(tokens)
            if cls.socket_conn:
                cls.socket_conn.subscribe(list(cls.instrument_tokens))
                cls.socket_conn.set_mode(cls.socket_conn.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to new tokens: {cls.instrument_tokens}")

    @classmethod
    def remove_instruments(cls, tokens):
        """Removes instrument tokens from subscription."""
        with cls._ticker_lock:
            cls.instrument_tokens.difference_update(tokens)
            if cls.socket_conn:
                cls.socket_conn.unsubscribe(list(tokens))
                logger.info(f"Unsubscribed from tokens: {tokens}")
