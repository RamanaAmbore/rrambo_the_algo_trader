import threading
from collections import defaultdict
from enum import Enum

from bidict import bidict

from src.helpers.decorators import update_lock, track_it
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.helpers.utils import reverse_dict, create_instr_symbol_xref

multi_set_dict = defaultdict(set)

logger = get_logger(__name__)


from enum import Enum

class AppState(Enum):
    SYMBOL_TOKEN_MAP = "SYM_TOK"
    TOKEN_SYMBOL_MAP = "TOK_SYM"

    HOLDINGS = "HOLD"
    SYMBOL_HOLDING_MAP = "SYM_HOLD"
    TOKEN_HOLDING_MAP = "TOK_HOLD"

    POSITIONS = "POS"
    SYMBOL_POS_MAP = "SYM_POS"
    TOKEN_POS_MAP = "TOK_POS"

    WATCHLISTS = "WATCH"
    SYMBOL_WATCH_MAP = "SYM_WATCH"
    TOKEN_WATCH_MAP = "TOK_WATCH"

    TOKEN_TRACK_MAP = "TOK_TRACK"
    SYMBOL_TRACK_MAP = "SYM_TRACK"

    SCHEDULE_TIME = "SCHED_TIME"

    TRACK_TOKEN_XREF_BY_CATEGORY = "TRACK_XREF_CAT"
    TRACK_TOKEN_XREF_XCHANGE = "TRACK_XREF_XCHG"
    TRACK_TOKEN_SYMBOL_MAP = "TRACK_TOK_SYM"
    TRACK_TOKEN_LTP_MAP = "TRACK_LTP"

class AppStateManager(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.track_state = {}
        self.element_locks = {}
        self.lock = threading.RLock()
        self._singleton_initialized = True

    def get(self, key=None, sub_key=None, default=None):
        if isinstance(key, AppState):
            key = str(key)
        if key is None:
            return self.track_state
        result = self.track_state.get(key, default)
        if sub_key is None:
            return result
        return result.get(sub_key, default) if isinstance(result, dict) else default

    @update_lock
    def set(self, key, value, sub_key=None):
        if isinstance(key, AppState):
            key = str(key)
        if sub_key is None:
            self.track_state[key] = value
        else:
            if key not in self.track_state:
                self.track_state[key] = {}
            self.track_state[key][sub_key] = value

    @update_lock
    def remove(self, key, sub_key=None):
        if isinstance(key, AppState):
            key = str(key)
        if sub_key is None:
            self.track_state.pop(key, None)
        else:
            if key in self.track_state:
                self.track_state[key].pop(sub_key, None)

    def set_instruments(self, value=None, sub_key=None):
        self.set(AppState.SYMBOL_TOKEN_MAP, value, sub_key)
        self.set(AppState.TOKEN_SYMBOL_MAP, reverse_dict(value, reverse_key='instrument_token', use_type=None), sub_key)

    def set_positions(self, value=None, sub_key=None):
        self.set(AppState.POSITIONS, value, sub_key)
        symbol_instr_xref = self.get(AppState.SYMBOL_TOKEN_MAP)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(AppState.SYMBOL_POS_MAP, symbol_id_xref, sub_key)
        self.set(AppState.TOKEN_POS_MAP, instr_id_xref, sub_key)

    def set_holdings(self, value=None, sub_key=None):
        self.set(AppState.HOLDINGS, value, sub_key)
        symbol_instr_xref = self.get(AppState.SYMBOL_TOKEN_MAP)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(AppState.SYMBOL_HOLDING_MAP, symbol_id_xref, sub_key)
        self.set(AppState.TOKEN_HOLDING_MAP, instr_id_xref, sub_key)

    def set_watchlist(self, value=None, sub_key=None):
        self.set(AppState.WATCHLISTS, value, sub_key)
        symbol_instr_xref = self.get(AppState.SYMBOL_TOKEN_MAP)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(AppState.SYMBOL_WATCH_MAP, symbol_id_xref, sub_key)
        self.set(AppState.TOKEN_WATCH_MAP, instr_id_xref, sub_key)

    def set_ltp(self, value=None, sub_key=None):
        self.set(AppState.TRACK_TOKEN_LTP_MAP, value, sub_key)

    @track_it()
    def set_track_list(self, unique_exchanges):
        track_instr_xref_by_category = defaultdict(dict)
        track_instr_xref_xchange = defaultdict(set)

        track_instr_set = defaultdict(set)

        # Populate cross-reference and token sets
        for key, val in self.get(AppState.TOKEN_POS_MAP).items():
            track_instr_xref_by_category[key]['p'] = val
            track_instr_set[key].update(val)

        for key, val in self.get(AppState.TOKEN_HOLDING_MAP).items():
            track_instr_xref_by_category[key]['h'] = val
            track_instr_set[key].update(val)

        for key, val in self.get(AppState.TOKEN_WATCH_MAP).items():
            track_instr_xref_by_category[key]['w'] = val
            track_instr_set[key].update(val)

        # Finalize dicts
        track_instr_xref_by_category = dict(track_instr_xref_by_category)
        track_instr_set = dict(track_instr_set)

        # Prepare for exchange-specific mapping
        exchange_specific_instr = set()
        instr_symbol_xref = self.get(AppState.TOKEN_SYMBOL_MAP)

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

        self.set(AppState.TRACK_TOKEN_SYMBOL_MAP, bidict(track_instr_symbol_xref))
        self.set(AppState.TRACK_TOKEN_XREF_XCHANGE, track_instr_xref_xchange)
        self.set(AppState.TRACK_TOKEN_XREF_BY_CATEGORY, track_instr_xref_by_category)


# Singleton instance
app_state = AppStateManager()
