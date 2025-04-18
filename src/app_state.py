from threading import Lock
from bidict import bidict
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


def locked_update(method):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return wrapper


class AppState(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self._instrument_map = {}
        self._instrument_list = {}
        self._watchlist = {}
        self._watchlist_inst = {}
        self._holdings = {}
        self._positions = {}
        self._instrument_xref = {}  # symbol_exchange -> {category: key}
        self._xref_reverse = {}     # (category, key) -> symbol_exchange

        # Instrument/symbol collections
        self._token_list_all = set()
        self._token_list_watchlist = set()
        self._token_list_positions = set()
        self._token_list_holdings = set()

        self._symbol_list_all = set()
        self._symbol_list_watchlist = set()
        self._symbol_list_positions = set()
        self._symbol_list_holdings = set()

        self.lock = Lock()
        self._singleton_initialized = True

    def _add_xref(self, symbol_exchange, category, key):
        self._instrument_xref.setdefault(symbol_exchange, {})[category] = key
        self._xref_reverse[(category, key)] = symbol_exchange

        token = self._instrument_map.get(symbol_exchange)
        if token:
            self._token_list_all.add(token)
            self._symbol_list_all.add(symbol_exchange)
            if category == "watchlist":
                self._token_list_watchlist.add(token)
                self._symbol_list_watchlist.add(symbol_exchange)
            elif category == "positions":
                self._token_list_positions.add(token)
                self._symbol_list_positions.add(symbol_exchange)
            elif category == "holdings":
                self._token_list_holdings.add(token)
                self._symbol_list_holdings.add(symbol_exchange)

    def _remove_xref(self, symbol_exchange, category):
        if symbol_exchange in self._instrument_xref:
            self._instrument_xref[symbol_exchange].pop(category, None)
            if not self._instrument_xref[symbol_exchange]:
                del self._instrument_xref[symbol_exchange]
        self._xref_reverse.pop((category, symbol_exchange), None)
        self._refresh_lists()

    def _refresh_xref(self):
        self._instrument_xref.clear()
        self._xref_reverse.clear()
        self._refresh_lists()

        for key, record in self._holdings.items():
            self._add_xref(record.symbol_exchange, "holdings", key)
        for key, record in self._positions.items():
            self._add_xref(record.symbol_exchange, "positions", key)
        for key, record in self._watchlist.items():
            self._add_xref(record.symbol_exchange, "watchlist", key)

    def _refresh_lists(self):
        self._token_list_all.clear()
        self._token_list_watchlist.clear()
        self._token_list_positions.clear()
        self._token_list_holdings.clear()

        self._symbol_list_all.clear()
        self._symbol_list_watchlist.clear()
        self._symbol_list_positions.clear()
        self._symbol_list_holdings.clear()

    # Helpers to retrieve mappings
    def get_instrument_xref(self):
        return self._instrument_xref

    def get_tokens_with_keys(self):
        return self._instrument_xref

    def get_all_tokens(self):
        return {token: None for token in self._token_list_all}

    def get_symbol_exchange_by_key(self, category, key):
        return self._xref_reverse.get((category, key))

    # Instrument Tokens Helpers
    def get_all_tokens_list(self):
        return list(self._token_list_all)

    def get_tokens_by_category(self, category):
        return {
            "watchlist": list(self._token_list_watchlist),
            "positions": list(self._token_list_positions),
            "holdings": list(self._token_list_holdings),
        }.get(category, [])

    def get_symbol_list_by_category(self, category):
        return {
            "watchlist": list(self._symbol_list_watchlist),
            "positions": list(self._symbol_list_positions),
            "holdings": list(self._symbol_list_holdings),
        }.get(category, [])

    def get_all_symbol_exchanges(self):
        return list(self._symbol_list_all)

    # Instrument Map
    def get_instrument_list(self):
        return self._instrument_list

    @locked_update
    def set_instrument_list(self, value):
        self._instrument_list = value
        self._instrument_map = bidict({key: val.instruement_token for key, val in value.items()})
        self._refresh_xref()

    @locked_update
    def update_instrument_list(self, symbol_exchange, insturment_token):
        self._instrument_map[symbol_exchange] = insturment_token
        self._instrument_list[symbol_exchange] = insturment_token

    # Watchlist
    def get_watchlist(self):
        return self._watchlist

    @locked_update
    def set_watchlist(self, value):
        self._watchlist = value
        self._refresh_xref()

    @locked_update
    def add_to_watchlist(self, symbol_exchange, record):
        self._watchlist[symbol_exchange] = record
        self._add_xref(record.symbol_exchange, "watchlist", symbol_exchange)

    @locked_update
    def remove_from_watchlist(self, symbol_exchange):
        self._watchlist.pop(symbol_exchange, None)
        self._remove_xref(symbol_exchange, "watchlist")

    # Watchlist Instrument Map
    def get_watchlist_inst(self):
        return self._watchlist_inst

    @locked_update
    def set_watchlist_inst(self, value):
        self._watchlist_inst = value

    @locked_update
    def add_to_watchlist_inst(self, token):
        self._watchlist_inst[token] = None

    @locked_update
    def remove_from_watchlist_inst(self, token):
        self._watchlist_inst.pop(token, None)

    # Holdings
    def get_holdings(self):
        return self._holdings

    @locked_update
    def set_holdings(self, value):
        self._holdings = value
        self._refresh_xref()

    @locked_update
    def update_holdings(self, symbol_exchange, data):
        self._holdings[symbol_exchange] = data
        self._add_xref(symbol_exchange, "holdings", symbol_exchange)

    @locked_update
    def remove_holdings(self, symbol_exchange):
        if symbol_exchange in self._holdings:
            del self._holdings[symbol_exchange]
            self._remove_xref(symbol_exchange, "holdings")

    # Positions
    def get_positions(self):
        return self._positions

    @locked_update
    def set_positions(self, value):
        self._positions = value
        self._refresh_xref()

    @locked_update
    def update_positions(self, symbol_exchange, data):
        self._positions[symbol_exchange] = data
        self._add_xref(symbol_exchange, "positions", symbol_exchange)

    @locked_update
    def remove_positions(self, symbol_exchange):
        if symbol_exchange in self._positions:
            del self._positions[symbol_exchange]
            self._remove_xref(symbol_exchange, "positions")


# Singleton instance
app_state = AppState()
