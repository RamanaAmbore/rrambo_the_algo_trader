import enum
from datetime import time

from src.helpers.cipher_utils import encrypt_text


class Weekday(enum.Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'
    GLOBAL = 'GLOBAL'


class Source(enum.Enum):
    API = 'API'
    MANUAL = 'MANUAL'
    WEBSOCKET = 'WEBSOCKET'
    REPORTS = 'REPORTS'
    FRONTEND = 'FRONTEND'
    CODE = 'CODE'


class ThreadStatus(enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RESTARTED = "RESTARTED"


class Account(enum.Enum):
    ACCOUNT1 = 'ZG0790'
    ACCOUNT2 = 'ZJ6924'


class Schedule(enum.Enum):
    MARKET = 'MARKET'
    PRE_MARKET = 'PRE-MARKET'


class Thread(enum.Enum):
    SOCKET = "SOCKET"
    SYNC_REPORT_DATA = "SYNC_REPORT_DATA"
    UPDATE_STOCK_LIST = "UPDATE_STOCK_LIST"
    UPDATE_HIST_PRICES = "UPDATE_HIST_PRICES"
    UPDATE_WATCHLIST_INSTRUMENTS = "UPDATE_WATCHLIST_INSTRUMENTS"


DEFAULT_ACCESS_TOKENS = [{'account': Account.ACCOUNT1, 'token': ''}, {'account': Account.ACCOUNT2, 'token': None}]

DEFAULT_ALGO_THREADS = [{'thread': Thread.SOCKET}, {'thread': Thread.SYNC_REPORT_DATA},
                        {'thread': Thread.UPDATE_STOCK_LIST},
                        {'thread': Thread.UPDATE_HIST_PRICES}, {'thread': Thread.UPDATE_WATCHLIST_INSTRUMENTS}]

DEFAULT_ALGO_SCHEDULES = [{'schedule': Schedule.MARKET}, {'schedule': Schedule.PRE_MARKET}, ]

DEFAULT_ALGO_SCHEDULE_TIME_RECORDS = [
    {'weekday': Weekday.GLOBAL, 'schedule': Schedule.MARKET, 'start_time': time(9, 0), 'end_time': time(15, 30),
     'is_active': True},
    {'weekday': Weekday.SATURDAY, 'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None,
     'is_active': False},
    {'weekday': Weekday.SUNDAY, 'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None, 'is_active': False},
    {'weekday': Weekday.SATURDAY, 'schedule': Schedule.PRE_MARKET, 'start_time': time(9, 0), 'end_time': None,
     'is_active': True}]

DEFAULT_THREAD_SCHEDULE_XREF = [{'thread': Thread.SOCKET, 'schedule': Schedule.MARKET},
                                {'thread': Thread.SYNC_REPORT_DATA, 'schedule': Schedule.PRE_MARKET},
                                {'thread': Thread.UPDATE_STOCK_LIST, 'schedule': Schedule.PRE_MARKET},
                                {'thread': Thread.UPDATE_HIST_PRICES, 'schedule': Schedule.PRE_MARKET},
                                {'thread': Thread.UPDATE_WATCHLIST_INSTRUMENTS, 'schedule': Schedule.PRE_MARKET}]

DEFAULT_BROKER_ACCOUNTS = [{'account': Account.ACCOUNT1, 'broker_name': 'Zerodha', 'notes': 'Haritha account'},
                           {'account': Account.ACCOUNT2, 'broker_name': 'Zerodha', 'notes': 'Ramana account'}, ]

DEFAULT_PARAMETERS = [  # Zerodha Credentials
    {'account': Account.ACCOUNT1, 'parameter': 'API_KEY', 'value': encrypt_text(r'05hjicsyku3stv9o')},
    {'account': Account.ACCOUNT1, 'parameter': 'API_SECRET',
     'value': encrypt_text(r'2b5npva2x8f8fvd5lxhte3xpn4zh7lc8')},
    {'account': Account.ACCOUNT1, 'parameter': 'PASSWORD', 'value': encrypt_text(r'Zerodha01#')},
    {'account': Account.ACCOUNT1, 'parameter': 'TOTP_TOKEN',
     'value': encrypt_text(r'YJPG3JUXH365ENNG7LNGEWRMQWQBKSSZ')},

    {'account': Account.ACCOUNT2, 'parameter': 'API_KEY', 'value': None},
    {'account': Account.ACCOUNT2, 'parameter': 'API_SECRET', 'value': None},
    {'account': Account.ACCOUNT2, 'parameter': 'PASSWORD', 'value': encrypt_text(r'Anirudh01#')},
    {'account': Account.ACCOUNT2, 'parameter': 'TOTP_TOKEN',
     'value': encrypt_text(r'RQA7KROPJPY4FTBDG6JWG3WQDHGO3DDF')},
    # Market Configurations
    {'account': None, 'parameter': 'INSTRUMENT_TOKEN', 'value': '260105'},
    {'account': None, 'parameter': 'DATA_FETCH_INTERVAL', 'value': '5'},

    # Logging Configuration
    {'account': None, 'parameter': 'DEBUG_LOG_FILE', 'value': r'D:/rrambo_trader_new/logs/debug.log'},
    {'account': None, 'parameter': 'ERROR_LOG_FILE', 'value': r'D:/rrambo_trader_new/logs/error.log'},
    {'account': None, 'parameter': 'CONSOLE_LOG_LEVEL', 'value': 'DEBUG'},
    {'account': None, 'parameter': 'FILE_LOG_LEVEL', 'value': 'DEBUG'},
    {'account': None, 'parameter': 'ERROR_LOG_LEVEL', 'value': 'ERROR'},

    # URLs
    {'account': None, 'parameter': 'BASE_URL', 'value': r'https://kite.zerodha.com'},
    {'account': None, 'parameter': 'LOGIN_URL', 'value': r'https://kite.zerodha.com/api/login'},
    {'account': None, 'parameter': 'TWOFA_URL', 'value': r'https://kite.zerodha.com/api/twofa'},
    {'account': None, 'parameter': 'INSTRUMENTS_URL', 'value': r'https://api.kite.trade/instruments'},
    {'account': None, 'parameter': 'REDIRECT_URL', 'value': r'http://localhost:8080/apis/broker/login/zerodha'},
    {'account': None, 'parameter': 'KITE_URL', 'value': r'https://kite.zerodha.com/'},

    # Database Configuration
    {'account': None, 'parameter': 'SQLITE_DB', 'value': 'False'},
    {'account': None, 'parameter': 'SQLITE_PATH', 'value': r'D:/rrambo_trader_new/db/sqlite.db'},

    {'account': None, 'parameter': 'ACCESS_TOKEN_VALIDITY', 'value': '24'},

    # Other Configurations
    {'account': None, 'parameter': 'MAX_RETRIES', 'value': '3'},
    {'account': None, 'parameter': 'RETRY_DELAY', 'value': '1'},

    {'account': None, 'parameter': 'DB_DEBUG', 'value': 'True'},
    {'account': None, 'parameter': 'TEST_MODE', 'value': 'True'},

    {'account': None, 'parameter': 'REFRESH_TRADEBOOK', 'value': 'True'},
    {'account': None, 'parameter': 'REFRESH_PNL', 'value': 'True'},
    {'account': None, 'parameter': 'REFRESH_LEDGER', 'value': 'True'},

    {'account': None, 'parameter': 'DOWNLOAD_DIR', 'value': r'D:/rrambo_trader_new/data'},
    {'account': None, 'parameter': 'REPORT_START_DATE', 'value': '2015-01-01'},
    {'account': None, 'parameter': 'REPORT_LOOKBACK_DAYS', 'value': '30'}, ]

DEFAULT_WATCHLISTS = [{'watchlist': 'STOCKS'}, {'watchlist': 'STOCKS-TURNAROUND'}, {'watchlist': 'OPTIONS'},
                      {'watchlist': 'POSITION-WATCHLIST'}, {'watchlist': 'HOLDING-WATCHLIST'}]
