import queue
from threading import Lock
from src.ticks.tick_model import TickModel
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class TickQueueManager(SingletonBase):
    def __init__(self):
        self._queue = queue.Queue()
        self._lock = Lock()
        self._tick_map = {}  # instrument_token -> TickModel

    def enqueue(self, tick: TickModel):
        try:
            self._queue.put_nowait(tick)
            with self._lock:
                self._tick_map[tick.instrument_token] = tick
            logger.debug(f"Tick enqueued and stored for instrument: {tick.instrument_token}")
        except queue.Full:
            logger.warning("Tick queue is full. Dropping tick.")

    def dequeue(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def size(self):
        return self._queue.qsize()

    def get_tick(self, instrument_token: int) -> TickModel:
        with self._lock:
            return self._tick_map.get(instrument_token)

    def get_all_ticks(self) -> dict[int, TickModel]:
        with self._lock:
            return dict(self._tick_map)  # return a shallow copy

