import threading
import time
from enum import Enum

from kiteconnect import KiteTicker

from src.backend.ticks.tick_service import TickService
from src.helpers.date_time_utils import current_time_indian
from src.helpers.decorators import retry_kite_conn
from src.helpers.logger import get_logger
from src.helpers.singleton_base import SingletonBase
from src.settings.parameter_manager import parms

logger = get_logger(__name__)

class TickerState(Enum):
    FIRST_RUN = 1
    CONNECTED = 2
    SUBSEQUENT_RUNS = 3

class Ticker(SingletonBase, threading.Thread):
    _instance = None
    _lock = threading.Lock()
    instrument_tokens = set()
    MAX_RECONNECT_ATTEMPTS = int(parms.MAX_SOCKET_RECONNECT_ATTEMPTS)
    RECONNECT_BACKOFF = 5  # seconds

    def __init__(self, kite_obj, track_instr_xref_exchange, schedule_time):
        with Ticker._lock:
            if Ticker._instance is not None:
                logger.debug(f"{self.__class__.__name__} already initialized.")
                return

            threading.Thread.__init__(self, daemon=True)

            self.kite = kite_obj
            self.socket_conn = None
            self.running = True
            self.tokens = set()
            self.track_instr_xref_exchange = track_instr_xref_exchange
            self.schedule_time = None
            self.instruments = set()
            self.instr_xchange_xref = {}
            self.add_instruments = set()
            self.remove_instruments = set()
            self.reconnect_attempts = 0
            self.ticker_state = TickerState.FIRST_RUN  # Using enum for state management

            Ticker._instance = self
            self.update_schedule_time(schedule_time)
            logger.info("Ticker thread initialized.")

    @retry_kite_conn(parms.MAX_KITE_CONN_RETRY_COUNT)
    def setup_socket_conn(self):
        if self.socket_conn:
            return

        self.socket_conn = KiteTicker(self.kite.api_key, self.kite.get_access_token())
        self.socket_conn.on_ticks = Ticker.on_ticks
        self.socket_conn.on_connect = Ticker.on_connect
        self.socket_conn.on_close = Ticker.on_close
        self.socket_conn.on_error = Ticker.on_error
        self.socket_conn.on_reconnect = Ticker.on_reconnect
        self.socket_conn.connect(threaded=True)

    def run(self):
        logger.info("Ticker thread started.")

        while self.running:
            try:
                if instruments := self.setup_instruments():
                    logger.debug("Market is open. Ensuring WebSocket is active.")
                    if self.ticker_state == TickerState.FIRST_RUN:
                        Ticker.add_instruments(instruments)
                        self.setup_socket_conn()
                        self.ticker_state = TickerState.CONNECTED
                    elif self.ticker_state == TickerState.CONNECTED:
                        self.socket_conn.set_mode(self.socket_conn.MODE_QUOTE, list(self.instrument_tokens))
                        self.ticker_state = TickerState.SUBSEQUENT_RUNS

                time.sleep(parms.KITE_SOCKET_SLEEP)

            except Exception as e:
                logger.error(f"Error in Ticker loop: {e}")
                raise

    def close_socket(self):
        if self.socket_conn:
            logger.info("Closing WebSocket connection...")
            self.socket_conn.close()
            self.socket_conn = None

    def setup_instruments(self):
        current_time = current_time_indian().strftime('%H:%M')

        instruments = set()
        market_open = False
        for sch_rec in self.schedule_time:
            market_open = (sch_rec['start_time'] <= current_time <= sch_rec[
                'end_time'])
            if market_open or self.ticker_state == TickerState.FIRST_RUN:
                logger.info(f"Exchange {sch_rec['exchange']} is open")
                instruments.update(self.track_instr_xref_exchange[sch_rec['exchange']])

        if market_open and not instruments:  # If no instruments are found, close the WebSocket
            logger.debug("No instruments found. Closing WebSocket and resetting Ticker state.")
            self.close_socket()
            self.ticker_state = TickerState.FIRST_RUN  # Reset to FIRST_RUN to reconnect when market opens again
            return set()

        if self.ticker_state == TickerState.FIRST_RUN:
            self.instruments = instruments
            return self.instruments

        if instruments == self.instruments:
            return self.instruments

        self.remove_instruments = self.instruments.difference(instruments)
        self.add_instruments = instruments.difference(self.instruments)

        if self.remove_instruments:
            Ticker.remove_instruments(self.remove_instruments)
        if self.add_instruments:
            Ticker.add_instruments(self.add_instruments)

        self.instruments = instruments
        return self.instruments

    def update_schedule_time(self, schedule_time):
        self.schedule_time = [val for val in schedule_time if val['schedule'] == "MARKET"]
        return self

    # ─── WebSocket Class Methods ───────────────────────────────────────────────

    @classmethod
    def on_connect(cls, ws, response):
        cls_instance = cls._instance
        if cls_instance is None:
            logger.warning("Ticker instance is None during on_connect.")
            return

        cls_instance.reconnect_attempts = 0
        with cls._lock:
            if cls.instrument_tokens:
                ws.subscribe(list(cls.instrument_tokens))
                ws.set_mode(ws.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to tokens: {cls.instrument_tokens}")

    @classmethod
    def on_ticks(cls, ws, ticks):
        # Use debug logging instead of print
        logger.debug(f"Received tick data: {ticks}")

        TickService().process_ticks(ticks)

    @classmethod
    def on_close(cls, ws, code, reason):
        logger.warning(f"WebSocket closed: {reason}")
        cls_instance = cls._instance
        if cls_instance is None:
            return

        if "TokenException" in str(reason) or "Invalid access token" in str(reason or ""):
            logger.error("Access token may be invalid. Re-authenticating...")
            try:
                logger.info("Reinitializing WebSocket with new token...")
                cls_instance.setup_socket_conn()
            except Exception as e:
                logger.error(f"Failed to re-authenticate: {e}")
        else:
            cls_instance.reconnect_attempts += 1
            time.sleep(min(cls.RECONNECT_BACKOFF * (2 ** cls_instance.reconnect_attempts), 60))
            cls_instance.setup_socket_conn()

    @classmethod
    def on_error(cls, ws, code, reason):
        logger.error(f"WebSocket error {code}: {reason}")

    @classmethod
    def on_reconnect(cls, ws, attempts):
        logger.info(f"WebSocket reconnect attempt {attempts}...")

    # ─── Instrument Token Management ────────────────────────────────────────────

    @classmethod
    def add_instruments(cls, tokens):
        with cls._lock:
            cls.instrument_tokens.update(tokens)
            if cls._instance and cls._instance.socket_conn:
                cls._instance.socket_conn.subscribe(list(tokens))
                cls._instance.socket_conn.set_mode(cls._instance.socket_conn.MODE_QUOTE, list(tokens))
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
                logger.info("Stopping Ticker thread.")
                cls._instance.running = False
                cls._instance.close_socket()
                cls._instance.join()
                cls._instance = None

