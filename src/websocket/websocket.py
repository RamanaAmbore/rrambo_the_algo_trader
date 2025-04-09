import threading
from kiteconnect import KiteTicker
from src.services.service_websocket_tick import ServiceWebsocketTick
from src.queues.websocket_tick_queue import tick_queue
from src.helpers.logger import get_logger
import asyncio

logger = get_logger(__name__)

class MarketTicker(threading.Thread):
    def __init__(self, api_key, access_token, memory_store):
        super().__init__(daemon=True)
        self.kws = KiteTicker(api_key, access_token)
        self.memory_store = memory_store
        self.service = ServiceWebsocketTick(memory_store)

        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_error = self.on_error

    def run(self):
        asyncio.create_task(self.service.process_tick())
        self.kws.connect(threaded=True)

    def on_connect(self, ws, response):
        instrument_tokens = list(self.memory_store.keys())
        ws.subscribe(instrument_tokens)
        logger.info("Subscribed to tokens.")

    def on_ticks(self, ws, ticks):
        for tick in ticks:
            asyncio.create_task(tick_queue.push(tick))

    def on_error(self, ws, code, reason):
        logger.error(f"WebSocket error: {reason}")
