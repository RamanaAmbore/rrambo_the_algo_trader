import threading
from collections import defaultdict

from bidict import bidict

from src.core.decorators import update_lock, track_it
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.helpers.utils import reverse_dict, create_instr_symbol_xref

multi_set_dict = defaultdict(set)

logger = get_logger(__name__)


class Xref:
    SYMBOL_INSTR_XREF = 'symbol_instr_xref'
    INSTR_SYMBOL_XREF = 'instr_symbol_xref'

    HOLDINGS = 'holdings'
    SYMBOL_HOLDINGS = 'symbol_holdings'
    INSTR_HOLDINGS = 'instr_holdings'

    POSITIONS = 'positions'
    SYMBOL_POSITIONS = 'symbol_positions'
    INSTR_POSITIONS = 'instr_positions'

    WATCHLISTS = 'watchlists'
    SYMBOL_WATCHLISTS = 'symbol_watchlists'
    INSTR_WATCHLISTS = 'instr_watchlists'

    INSTR_TRACKLIST = 'instr_tracklist'
    SYMBOL_TRACKLIST = 'symbol_tracklist'

    SCHEDULE_TIME = 'schedule_time'

    TRACK_INSTR_XREF_BY_CATEGORY = 'track_instr_xref_by_category'
    TRACK_INSTR_XREF_XCHANGE = 'track_instr_xref_xchange'
    TRACK_INSTR_SYMBOL_XREF = 'track_instr_symbol_xref'


class AppState(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.track_state = {}
        self.element_locks = {}
        self.lock = threading.RLock()
        self._singleton_initialized = True

    def get(self, key=None, sub_key=None, default=None):
        if key is None:
            return self.track_state
        result = self.track_state.get(key, default)
        if sub_key is None:
            return result
        return result.get(sub_key, default) if isinstance(result, dict) else default

    @update_lock
    def set(self, key, value, sub_key=None):
        if sub_key is None:
            self.track_state[key] = value
        else:
            if key not in self.track_state:
                self.track_state[key] = {}
            self.track_state[key][sub_key] = value

    @update_lock
    def remove(self, key, sub_key=None):
        if sub_key is None:
            self.track_state.pop(key, None)
        else:
            if key in self.track_state:
                self.track_state[key].pop(sub_key, None)

    def set_instruments(self, value=None, sub_key=None):
        self.set(Xref.SYMBOL_INSTR_XREF, value, sub_key)
        self.set(Xref.INSTR_SYMBOL_XREF, reverse_dict(value, reverse_key='instrument_token', use_type=None), sub_key)

    # Specific set methods
    def set_positions(self, value=None, sub_key=None):
        self.set(Xref.POSITIONS, value, sub_key)
        symbol_instr_xref = self.get(Xref.SYMBOL_INSTR_XREF)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_POSITIONS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_POSITIONS, instr_id_xref, sub_key)

    def set_holdings(self, value=None, sub_key=None):
        self.set(Xref.HOLDINGS, value, sub_key)
        symbol_instr_xref = self.get(Xref.SYMBOL_INSTR_XREF)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_HOLDINGS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_HOLDINGS, instr_id_xref, sub_key)

    def set_watchlist(self, value=None, sub_key=None):
        self.set(Xref.WATCHLISTS, value, sub_key)
        symbol_instr_xref = self.get(Xref.SYMBOL_INSTR_XREF)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_WATCHLISTS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_WATCHLISTS, instr_id_xref, sub_key)

    @track_it()
    def set_track_list(self, unique_exchanges):
        track_instr_xref_by_category = defaultdict(dict)
        track_instr_xref_xchange = defaultdict(set)

        track_instr_set = defaultdict(set)

        # Populate cross-reference and token sets
        for key, val in self.get(Xref.INSTR_POSITIONS).items():
            track_instr_xref_by_category[key]['p'] = val
            track_instr_set[key].update(val)

        for key, val in self.get(Xref.INSTR_HOLDINGS).items():
            track_instr_xref_by_category[key]['h'] = val
            track_instr_set[key].update(val)

        for key, val in self.get(Xref.INSTR_WATCHLISTS).items():
            track_instr_xref_by_category[key]['w'] = val
            track_instr_set[key].update(val)

        # Finalize dicts
        track_instr_xref_by_category = dict(track_instr_xref_by_category)
        track_instr_set = dict(track_instr_set)

        # Prepare for exchange-specific mapping

        exchange_specific_instr = set()
        instr_symbol_xref = self.get(Xref.INSTR_SYMBOL_XREF)

        for exchange in unique_exchanges:
            if exchange != '*':
                for token in track_instr_set:
                    symbol = instr_symbol_xref.get(token)
                    if symbol and symbol.endswith(f':{exchange}'):
                        track_instr_xref_xchange[exchange].add(token)
                        exchange_specific_instr.add(token)

        # Assign tokens without a specific exchange under '*'
        wildcard_instr = set(track_instr_set.keys()) - exchange_specific_instr
        track_instr_xref_xchange['*'].update(wildcard_instr)

        track_instr_symbol_xref = {i: instr_symbol_xref[i] for i in track_instr_set}

        # Convert to regular dict if needed
        track_instr_xref_xchange = dict(track_instr_xref_xchange)

        self.set(Xref.TRACK_INSTR_SYMBOL_XREF, bidict(track_instr_symbol_xref))
        self.set(Xref.TRACK_INSTR_XREF_XCHANGE, track_instr_xref_xchange)
        self.set(Xref.TRACK_INSTR_XREF_BY_CATEGORY, track_instr_xref_by_category)


# Singleton instance
app_state = AppState()
