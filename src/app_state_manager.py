import threading
from collections import defaultdict

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
    EXCHANGE_LIST = 'exchange_list'


class AppState(SingletonBase):
    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.track_state = {}
        self.element_locks = {}
        self.lock = threading.RLock()
        self._singleton_initialized = True
        self.symbol_instr_xref = {}
        self.track_instr_set = set()
        self.track_symbol_set = set()
        self.track_instr_xref = {}

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
        self.symbol_instr_xref = value
        self.set(Xref.SYMBOL_INSTR_XREF, value, sub_key)
        self.set(Xref.INSTR_SYMBOL_XREF, reverse_dict(value, reverse_key='instrument_token', use_type=None), sub_key)

    # Specific set methods
    def set_positions(self, value=None, sub_key=None):
        self.set(Xref.POSITIONS, value, sub_key)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, self.symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_POSITIONS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_POSITIONS, instr_id_xref, sub_key)

    def set_holdings(self, value=None, sub_key=None):
        self.set(Xref.HOLDINGS, value, sub_key)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, self.symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_HOLDINGS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_HOLDINGS, instr_id_xref, sub_key)

    def set_watchlist(self, value=None, sub_key=None):
        self.set(Xref.WATCHLISTS, value, sub_key)
        symbol_id_xref, instr_id_xref = create_instr_symbol_xref(value, self.symbol_instr_xref,
                                                                 reverse_key='symbol_exchange')
        self.set(Xref.SYMBOL_WATCHLISTS, symbol_id_xref, sub_key)
        self.set(Xref.INSTR_WATCHLISTS, instr_id_xref, sub_key)

    def set_schedule_time(self, value=None, sub_key=None):
        self.set(Xref.SCHEDULE_TIME, value, sub_key=sub_key)

    @track_it()
    def set_track_list(self):

        self.track_instr_xref = defaultdict(dict)

        for key, val in self.get(Xref.INSTR_POSITIONS).items():
            self.track_instr_xref[key]['p'] = val

        for key, val in self.get(Xref.INSTR_HOLDINGS).items():
            self.track_instr_xref[key]['h'] = val

        for key, val in self.get(Xref.INSTR_WATCHLISTS).items():
            self.track_instr_xref[key]['w'] = val

        self.track_instr_xref = dict(self.track_instr_xref)

        self.track_instr_set = set(self.track_instr_xref.keys())
        instr_symbol_xref = self.get(Xref.INSTR_SYMBOL_XREF)
        self.track_symbol_set = {instr_symbol_xref[key] for key in self.track_instr_xref}


# Singleton instance
app_state = AppState()
