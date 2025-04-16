from threading import Lock
from typing import Any

from bidict import bidict

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


def locked_update(method):
    """Decorator to acquire a lock before updating instance variables."""
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return wrapper


class AppState(SingletonBase):
    """
    Singleton class to manage the application's state, including instrument mappings,
    watchlist, holdings, and positions, with thread-safe updates.
    """
    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self._instrument_map = bidict()  # token <-> tradingsymbol|exchange
        self._watchlist = set()
        self._holdings = {}
        self._positions = {}
        self.lock = Lock()

    # Instrument Map using property decorator
    @property
    def instrument_map(self) -> bidict:
        """Returns the instrument map."""
        return self._instrument_map

    @instrument_map.setter
    @locked_update
    def instrument_map(self, value: bidict):
        """Sets the instrument map."""
        self._instrument_map = value

    @locked_update
    def update_instrument_map(self, token: str, trading_symbol_exchange: str):
        """Updates the instrument map with a single entry."""
        self._instrument_map[token] = trading_symbol_exchange

    # Watchlist using property decorator
    @property
    def watchlist(self) -> set:
        """Returns the watchlist."""
        return self._watchlist

    @watchlist.setter
    @locked_update
    def watchlist(self, value: set):
        """Sets the watchlist."""
        self._watchlist = value

    @locked_update
    def add_to_watchlist(self, instrument: Any):
        """Adds an instrument to the watchlist."""
        self._watchlist.add(instrument)

    @locked_update
    def remove_from_watchlist(self, instrument: Any):
        """Removes an instrument from the watchlist."""
        if instrument in self._watchlist:
            self._watchlist.remove(instrument)

    # Holdings using property decorator
    @property
    def holdings(self) -> dict:
        """Returns the holdings data."""
        return self._holdings

    @holdings.setter
    @locked_update
    def holdings(self, value: dict):
        """Sets the holdings data."""
        self._holdings = value

    @locked_update
    def update_holdings(self, symbol: str, data: dict):
        """Updates the holdings for a specific symbol."""
        self._holdings[symbol] = data

    # Positions using property decorator
    @property
    def positions(self) -> dict:
        """Returns the positions data."""
        return self._positions

    @positions.setter
    @locked_update
    def positions(self, value: dict):
        """Sets the positions data."""
        self._positions = value

    @locked_update
    def update_positions(self, symbol: str, data: dict):
        """Updates the positions for a specific symbol."""
        self._positions[symbol] = data


# Example of how to get the singleton instance
app_state = AppState()

