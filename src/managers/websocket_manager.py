import asyncio
from kiteconnect import KiteTicker
from src.core.app_initializer import get_kite_conn
from src.helpers.logger import get_logger
from src.managers.makret_state_manager import MarketStateManager
from src.services.service_websocket_tick import ServiceWebsocketTick

logger = get_logger(__name__)


class WebSocketManager:
    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.kite = get_kite_conn()
        self.ticker = KiteTicker(self.kite.api_key, self.kite.access_token)
        self.market_state = MarketStateManager()
        self.service = ServiceWebsocketTick()
        self.reconnect_attempts = 0

        # Bind callbacks
        self.ticker.on_connect = self.on_connect
        self.ticker.on_ticks = self.on_ticks
        self.ticker.on_close = self.on_close
        self.ticker.on_error = self.on_error
        self.ticker.on_reconnect = self.on_reconnect

    def start(self):
        logger.info("Starting WebSocketManager...")
        self.ticker.connect(threaded=True)

    def on_connect(self, ws, response):
        logger.info("WebSocket connected.")
        tokens = self.market_state.get_token_list()
        if tokens:
            self.ticker.subscribe(tokens)
            self.ticker.set_mode(self.ticker.MODE_FULL, tokens)
            logger.info(f"Subscribed to tokens: {tokens}")
        else:
            logger.warning("No tokens to subscribe to.")

    def on_close(self, ws, code, reason):
        logger.warning(f"WebSocket closed with code={code}, reason={reason}")

    def on_error(self, ws, code, reason):
        logger.error(f"WebSocket error: code={code}, reason={reason}")

    def on_reconnect(self, ws, attempt_count):
        logger.warning(f"WebSocket reconnecting... attempt {attempt_count}")
        self.reconnect_attempts += 1

    def on_ticks(self, ws, ticks):
        logger.debug(f"Received ticks: {len(ticks)}")

        # Update in-memory state
        self.market_state.update_ticks(ticks)

        # Enqueue async processing
        try:
            asyncio.create_task(self.service.process_ticks(ticks))
        except Exception as e:
            logger.error(f"Error creating async task: {e}")

# Example after fetching updated watchlist
# market_state_manager.update_watchlist(new_symbols)
# websocket_manager.update_subscription(market_state_manager.get_token_list())