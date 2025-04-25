import queue
from threading import Lock
from src.websocket_ticks.TickModel import TickModel
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class TickQueueManager(SingletonBase):
    def __init__(self):
        self._queue = queue.Queue()
        self._lock = Lock()

    def enqueue(self, tick: TickModel):
        try:
            self._queue.put_nowait(tick)
            logger.debug(f"Tick enqueued for instrument: {tick.instrument_token}")
        except queue.Full:
            logger.warning("Tick queue is full. Dropping tick.")

    def dequeue(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def size(self):
        return self._queue.qsize()
