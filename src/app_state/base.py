# src/app_state/base.py
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class StateComponent(SingletonBase):
    """Base class for managing a specific part of the application state."""
    def __init__(self, lock):
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.lock = lock
        self._data = {}
        self._singleton_initialized = True

    def set_data(self, value):
        self._data = value

    def get_data(self):
        return self._data

    def update_data(self, key, value):
        self._data[key] = value

    def remove_data(self, key):
        self._data.pop(key, None)

class MapState(StateComponent):
    """Base class for managing key-value map state."""
    def __init__(self, lock):
        super().__init__(lock)
        self._data = {}