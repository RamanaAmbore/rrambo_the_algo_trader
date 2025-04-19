from threading import Lock
from src.core.decorators import locked_update
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class StateInstrumentList(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return

        self.lock = Lock()
        self._instrument_map = {}
        self._inv_instrument_map = {}
        self._instrument_list = {}
        self._instrument_xref = {}
        self._xref_reverse = {}
        self._singleton_initialized = True

    @locked_update
    def set_instrument_list(self, value):
        with self.lock:
            self._instrument_list = value
            self._instrument_map = {
                key: val.instrument_token
                for key, val in value.items()
                if hasattr(val, "instrument_token")
            }
            self._inv_instrument_map = {
                val.instrument_token: key
                for key, val in value.items()
                if hasattr(val, "instrument_token")
            }
            self._refresh_xref()

    @locked_update
    def update_instrument_list(self, symbol_exchange, instrument_token):
        with self.lock:
            self._instrument_map[symbol_exchange] = instrument_token
            self._instrument_list[symbol_exchange] = instrument_token

    def get_instrument_list(self):
        return self._instrument_list

    def get_instrument_xref(self):
        return self._instrument_xref

    def get_symbol_exchange_by_key(self, category, key):
        return self._xref_reverse.get((category, key))

    def _add_xref(self, symbol_exchange, category, key):
        with self.lock:
            self._instrument_xref.setdefault(symbol_exchange, {})[category] = key
            self._xref_reverse[(category, key)] = symbol_exchange

    def _remove_xref(self, symbol_exchange, category):
        with self.lock:
            if symbol_exchange in self._instrument_xref:
                self._instrument_xref[symbol_exchange].pop(category, None)
                if not self._instrument_xref[symbol_exchange]:
                    del self._instrument_xref[symbol_exchange]
            self._xref_reverse.pop((category, symbol_exchange), None)

    @locked_update
    def _refresh_xref(self):
        with self.lock:
            self._instrument_xref.clear()
            self._xref_reverse.clear()

    def get_instrument_map(self):
        return self._instrument_map

    def get_inv_instrument_map(self):
        return self._inv_instrument_map

    # Added to get xref data.  This is used by AppState.
    def get_xref_data(self):
        return self._instrument_xref, self._xref_reverse

    def get_token_from_symbol(self, symbol_exchange):
        """Helper method to get a token from a symbol exchange."""
        return self._instrument_map.get(symbol_exchange)

    def get_xref_reverse(self):
        """Helper method to get the xref reverse mapping."""
        return self._xref_reverse


class AppState(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.state = {}
        self.instrument_list_state = StateInstrumentList()
        self.watchlist_state = WatchlistState()
        self.holdings_state = HoldingsState()
        self.positions_state = PositionsState()

        self.schedule_time = {}
        # Instrument/symbol collections
        self._token_list_all = set()
        self._token_list_watchlist = set()
        self._token_list_positions = set()
        self._token_list_holdings = set()

        self._symbol_list_all = set()
        self._symbol_list_watchlist = set()
        self._symbol_list_positions = set()
        self._symbol_list_holdings = set()
        self._exchange_list = set()

        self.lock = Lock()
        self._singleton_initialized = True

    def _add_xref(self, symbol_exchange, category, key):
        """
        Adds a cross-reference.  This method is called by other state management
        methods (e.g., when an item is added to the watchlist, or holdings).
        It updates the internal xref data in StateInstrumentList.
        """
        self.instrument_list_state._add_xref(symbol_exchange, category, key)
        token = self.instrument_list_state.get_token_from_symbol(
            symbol_exchange
        )  # Use the getter
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
        """
        Removes a cross-reference.  This method is called by other state management
        methods (e.g., when an item is removed from the watchlist, or holdings).
        It updates the xref data in StateInstrumentList.
        """
        self.instrument_list_state._remove_xref(symbol_exchange, category)
        self._refresh_lists()

    def _refresh_xref(self):
        """
        Refreshes all cross-references.  This is called when the underlying data
        in holdings, positions, or watchlist is changed.
        """
        self.instrument_list_state._refresh_xref()
        self._refresh_lists()
        # Get xref data and use it.
        instrument_xref, xref_reverse = self.instrument_list_state.get_xref_data()

        for key, record in self.holdings_state.get_holdings().items():
            self._add_xref(record.symbol_exchange, "holdings", key)
        for key, record in self.positions_state.get_positions().items():
            self._add_xref(record.symbol_exchange, "positions", key)
        for key, record in self.watchlist_state.get_watchlist().items():
            self._add_xref(record.symbol_exchange, "watchlist", key)

    @locked_update
    def _refresh_lists(self):
        """
        Refreshes the token and symbol lists based on the current cross-references
        maintained in StateInstrumentList.
        """
        self._token_list_all.clear()
        self._token_list_watchlist.clear()
        self._token_list_positions.clear()
        self._token_list_holdings.clear()

        self._symbol_list_all.clear()
        self._symbol_list_watchlist.clear()
        self._symbol_list_positions.clear()
        self._symbol_list_holdings.clear()

        # Re-populate the lists by iterating through the xref data in StateInstrumentList.
        instrument_xref, xref_reverse = self.instrument_list_state.get_xref_data()
        for symbol_exchange, categories in instrument_xref.items():
            token = self.instrument_list_state.get_token_from_symbol(
                symbol_exchange
            )  # Use the getter
            if token:
                self._token_list_all.add(token)
                self._symbol_list_all.add(symbol_exchange)
                for category in categories:
                    if category == "watchlist":
                        self._token_list_watchlist.add(token)
                        self._symbol_list_watchlist.add(symbol_exchange)
                    elif category == "positions":
                        self._token_list_positions.add(token)
                        self._symbol_list_positions.add(symbol_exchange)
                    elif category == "holdings":
                        self._token_list_holdings.add(token)
                        self._symbol_list_holdings.add(symbol_exchange)

    # Helpers to retrieve mappings
    def get_instrument_xref(self):
        return self.instrument_list_state.get_instrument_xref()

    def get_tokens_with_keys(self):
        return self.instrument_list_state.get_instrument_xref()

    def get_all_tokens(self):
        return {token: None for token in self._token_list_all}

    def get_symbol_exchange_by_key(self, category, key):
        return self.instrument_list_state.get_symbol_exchange_by_key(category, key)

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
        return self.instrument_list_state.get_instrument_list()

    def set_instrument_list(self, value):
        self.instrument_list_state.set_instrument_list(value)
        self._refresh_xref()

    def update_instrument_list(self, symbol_exchange, instrument_token):
        self.instrument_list_state.update_instrument_list(
            symbol_exchange, instrument_token
        )

    # Watchlist
    def get_watchlist(self):
        return self.watchlist_state.get_watchlist()

    @locked_update
    def set_watchlist(self, value):
        self.watchlist_state.set_watchlist(value)
        self._refresh_xref()

    @locked_update
    def add_to_watchlist(self, symbol_exchange, record):
        self.watchlist_state.add_to_watchlist(symbol_exchange, record)
        self._add_xref(symbol_exchange, "watchlist", symbol_exchange)

    @locked_update
    def remove_from_watchlist(self, symbol_exchange):
        self.watchlist_state.remove_from_watchlist(symbol_exchange)
        self._remove_xref(symbol_exchange, "watchlist")

    # Watchlist
    def get_watchlist(self):
        return self.watchlist_state.get_watchlist()

    @locked_update
    def set_watchlist(self, value):
        self.watchlist_state.set_watchlist(value)
        self._refresh_xref()

    @locked_update
    def add_to_watchlist(self, symbol_exchange, record):
        self.watchlist_state.add_to_watchlist(symbol_exchange, record)
        self._add_xref(symbol_exchange, "watchlist", symbol_exchange)

    @locked_update
    def remove_from_watchlist(self, symbol_exchange):
        self.watchlist_state.remove_from_watchlist(symbol_exchange)
        self._remove_xref(symbol_exchange, "watchlist")

    # Watchlist Instrument Map
    def get_watchlist_inst(self):
        return self.watchlist_state.get_watchlist_inst()

    @locked_update
    def set_watchlist_inst(self, value):
        self.watchlist_state.set_watchlist_inst(value)

    @locked_update
    def add_to_watchlist_inst(self, token):
        self.watchlist_state.add_to_watchlist_inst(token)

    @locked_update
    def remove_from_watchlist_inst(self, token):
        self.watchlist_state.remove_from_watchlist_inst(token)

    # Holdings
    def get_holdings(self):
        return self.holdings_state.get_holdings()

    @locked_update
    def set_holdings(self, value):
        self.holdings_state.set_holdings(value)
        self._refresh_xref()

    @locked_update
    def update_holdings(self, symbol_exchange, data):
        self.holdings_state.update_holdings(symbol_exchange, data)
        self._add_xref(symbol_exchange, "holdings", symbol_exchange)

    @locked_update
    def remove_holdings(self, symbol_exchange):
        self.holdings_state.remove_holdings(symbol_exchange)
        self._remove_xref(symbol_exchange, "holdings")

    # Positions
    def get_positions(self):
        return self.positions_state.get_positions()

    @locked_update
    def set_positions(self, value):
        self.positions_state.set_positions(value)
        self._refresh_xref()

    @locked_update
    def update_positions(self, symbol_exchange, data):
        self.positions_state.update_positions(symbol_exchange, data)
        self._add_xref(symbol_exchange, "positions", symbol_exchange)

    @locked_update
    def remove_positions(self, symbol_exchange):
        self.positions_state.remove_positions(symbol_exchange)
        self._remove_xref(symbol_exchange, "positions")

    # Schedule Map Helpers
    def get_schedule_map(self):
        return self.schedule_time

    @locked_update
    def set_schedule_time(self, value):
        self.schedule_time = value

    @locked_update
    def update_schedule(self, key, value):
        self.schedule_time[key] = value

    @locked_update
    def remove_schedule(self, key):
        self.schedule_time.pop(key, None)


# Singleton instance
app_state = AppState()