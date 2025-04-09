# src/services/market_state_manager.py

from threading import Lock
from bidict import bidict

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)

class MarketStateManager(SingletonBase):
    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.instrument_map = bidict()  # token <-> tradingsymbol|exchange
        self.watchlist = set()
        self.holdings = {}
        self.positions = {}
        self.lock = Lock()

    def update_watchlist(self, new_stocks):
        with self.lock:
            self.watchlist = set(new_stocks)
            self._update_instrument_map(new_stocks)

    def update_holdings(self, holdings_list):
        with self.lock:
            self.holdings = {h['tradingsymbol']: h for h in holdings_list}
            self._update_instrument_map([h['tradingsymbol'] for h in holdings_list])

    def update_positions(self, positions_list):
        with self.lock:
            self.positions = {p['tradingsymbol']: p for p in positions_list}
            self._update_instrument_map([p['tradingsymbol'] for p in positions_list])

    def _update_instrument_map(self, tradingsymbols):
        for symbol in tradingsymbols:
            token = self._get_token_from_symbol(symbol)
            if token:
                self.instrument_map[token] = symbol

    def _get_token_from_symbol(self, symbol):
        """
        Replace this with actual logic to fetch instrument token
        from DB or in-memory map/cache.
        """
        return self.fetch_token_from_db_or_cache(symbol)

    def fetch_token_from_db_or_cache(self, symbol):
        """
        Example: Query DB or Redis or in-memory static map.
        Should return integer instrument_token for the given symbol.
        """
        from src.db.instrument_repository import InstrumentRepository  # hypothetical module
        try:
            return InstrumentRepository.get_token_by_symbol(symbol)
        except Exception as e:
            logger.warning(f"Could not find token for symbol: {symbol} - {e}")
            return None

    def get_token_list(self):
        with self.lock:
            return list(self.instrument_map.keys())

    def get_all_symbols(self):
        with self.lock:
            return list(self.instrument_map.values())

