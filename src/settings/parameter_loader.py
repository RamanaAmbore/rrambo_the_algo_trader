import enum
import os
from datetime import time

from src.helpers.cipher_utils import encrypt_text
from dotenv import load_dotenv

load_dotenv()


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
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RESTARTED = "RESTARTED"


class Account(enum.Enum):
    ACCOUNT1 = 'ZG0790'
    ACCOUNT2 = 'ZJ6924'


class Schedule(enum.Enum):
    MARKET = 'MARKET'
    PRE_MARKET = 'PRE_MARKET'


class Thread(enum.Enum):
    SOCKET = "SOCKET"
    SYNC_REPORT_DATA = "SYNC_REPORT_DATA"
    UPDATE_STOCK_LIST = "UPDATE_STOCK_LIST"
    UPDATE_HIST_PRICES = "UPDATE_HIST_PRICES"
    UPDATE_WATCHLIST_INSTRUMENTS = "UPDATE_WATCHLIST_INSTRUMENTS"


DEFAULT_ACCESS_TOKENS = [{'account': Account.ACCOUNT1.value, 'token': ''},
                         {'account': Account.ACCOUNT2.value, 'token': None}]

DEFAULT_ALGO_THREADS = tuple(
    {"thread": thread.value} for thread in Thread
)

DEFAULT_ALGO_SCHEDULES = tuple(
    {"schedule": schedule.value} for schedule in Schedule
)

DEFAULT_ALGO_SCHEDULE_TIME_RECORDS = [
    {'weekday': Weekday.GLOBAL.value, 'schedule': Schedule.MARKET.value, 'start_time': time(9, 0),
     'end_time': time(15, 30),
     'is_active': True},
    {'weekday': Weekday.SATURDAY.value, 'schedule': Schedule.MARKET.value, 'start_time': None, 'end_time': None,
     'is_active': False},
    {'weekday': Weekday.SUNDAY.value, 'schedule': Schedule.MARKET.value, 'start_time': None, 'end_time': None,
     'is_active': False},
    {'weekday': Weekday.SATURDAY.value, 'schedule': Schedule.PRE_MARKET.value, 'start_time': time(9, 0),
     'end_time': None,
     'is_active': True}]

DEFAULT_THREAD_SCHEDULE_XREF = [{'thread': Thread.SOCKET.value, 'schedule': Schedule.MARKET.value},
                                {'thread': Thread.SYNC_REPORT_DATA.value, 'schedule': Schedule.PRE_MARKET.value},
                                {'thread': Thread.UPDATE_STOCK_LIST.value, 'schedule': Schedule.PRE_MARKET.value},
                                {'thread': Thread.UPDATE_HIST_PRICES.value, 'schedule': Schedule.PRE_MARKET.value},
                                {'thread': Thread.UPDATE_WATCHLIST_INSTRUMENTS.value,
                                 'schedule': Schedule.PRE_MARKET.value}]

DEFAULT_BROKER_ACCOUNTS = [{'account': Account.ACCOUNT1.value, 'broker_name': 'Zerodha', 'notes': 'Haritha account'},
                           {'account': Account.ACCOUNT2.value, 'broker_name': 'Zerodha', 'notes': 'Ramana account'}, ]

DEFAULT_WATCHLISTS = [{'watchlist': 'STOCKS'}, {'watchlist': 'STOCKS-TURNAROUND'}, {'watchlist': 'OPTIONS'},
                      {'watchlist': 'POSITION-WATCHLIST'}, {'watchlist': 'HOLDING-WATCHLIST'}]

DEFAULT_PARAMETERS = [  # Zerodha Credentials
    {'account': Account.ACCOUNT1.value, 'parameter': 'API_KEY', 'value': encrypt_text(os.getenv('ACCOUNT1_API_KEY'))},
    {'account': Account.ACCOUNT1.value, 'parameter': 'API_SECRET',
     'value': encrypt_text(os.getenv('ACCOUNT1_API_SECRET'))},
    {'account': Account.ACCOUNT1.value, 'parameter': 'PASSWORD', 'value': encrypt_text(os.getenv('ACCOUNT1_PASSWORD'))},
    {'account': Account.ACCOUNT1.value, 'parameter': 'TOTP_TOKEN',
     'value': encrypt_text(os.getenv('ACCOUNT1_TOTP_TOKEN'))},

    {'account': Account.ACCOUNT2.value, 'parameter': 'API_KEY', 'value': os.getenv('ACCOUNT2_API_KEY')},
    {'account': Account.ACCOUNT2.value, 'parameter': 'API_SECRET', 'value': os.getenv('ACCOUNT2_API_SECRET')},
    {'account': Account.ACCOUNT2.value, 'parameter': 'PASSWORD', 'value': encrypt_text(os.getenv('ACCOUNT2_PASSWORD'))},
    {'account': Account.ACCOUNT2.value, 'parameter': 'TOTP_TOKEN',
     'value': encrypt_text(os.getenv('ACCOUNT2_TOTP_TOKEN'))},
    # Market Configurations
    {'account': None, 'parameter': 'DATA_FETCH_INTERVAL', 'value': os.getenv('DATA_FETCH_INTERVAL')},

    # Logging Configuration
    {'account': None, 'parameter': 'DEBUG_LOG_FILE', 'value': os.getenv("DEBUG_LOG_FILE")},
    {'account': None, 'parameter': 'ERROR_LOG_FILE', 'value': os.getenv("ERROR_LOG_FILE")},
    {'account': None, 'parameter': 'CONSOLE_LOG_LEVEL', 'value': 'DEBUG'},
    {'account': None, 'parameter': 'FILE_LOG_LEVEL', 'value': 'DEBUG'},
    {'account': None, 'parameter': 'ERROR_LOG_LEVEL', 'value': 'ERROR'},

    # URLs
    {'account': None, 'parameter': 'BASE_URL', 'value': os.getenv('BASE_URL')},
    {'account': None, 'parameter': 'LOGIN_URL', 'value': os.getenv('BASE_URL')},
    {'account': None, 'parameter': 'TWOFA_URL', 'value': os.getenv('BASE_URL')},
    {'account': None, 'parameter': 'INSTRUMENTS_URL', 'value': os.getenv('BASE_URL')},
    {'account': None, 'parameter': 'REDIRECT_URL', 'value': os.getenv('BASE_URL')},
    {'account': None, 'parameter': 'KITE_URL', 'value': os.getenv('BASE_URL')},

    # Database Configuration
    {'account': None, 'parameter': 'SQLITE_DB', 'value': os.getenv('SQLITE_DB')},
    {'account': None, 'parameter': 'SQLITE_PATH', 'value': os.getenv('SQLITE_PATH')},

    {'account': None, 'parameter': 'ACCESS_TOKEN_VALIDITY', 'value': os.getenv('ACCESS_TOKEN_VALIDITY')},

    # Other Configurations
    {'account': None, 'parameter': 'MAX_RETRIES', 'value': os.getenv('MAX_RETRIES')},
    {'account': None, 'parameter': 'RETRY_DELAY', 'value': os.getenv('RETRY_DELAY')},

    {'account': None, 'parameter': 'DB_DEBUG', 'value': os.getenv('DB_DEBUG')},
    {'account': None, 'parameter': 'DROP_TABLES', 'value': os.getenv('DROP_TABLES')},
    {'account': None, 'parameter': 'TEST_MODE', 'value': os.getenv('TEST_MODE')},

    {'account': None, 'parameter': 'REFRESH_TRADEBOOK', 'value': os.getenv('REFRESH_TRADEBOOK')},
    {'account': None, 'parameter': 'REFRESH_PNL', 'value': os.getenv('REFRESH_PNL')},
    {'account': None, 'parameter': 'REFRESH_LEDGER', 'value': os.getenv('REFRESH_LEDGER')},

    {'account': None, 'parameter': 'DOWNLOAD_DIR', 'value': os.getenv('DOWNLOAD_DIR')},
    {'account': None, 'parameter': 'REPORT_START_DATE', 'value': os.getenv('REPORT_START_DATE')},
    {'account': None, 'parameter': 'REPORT_LOOKBACK_DAYS', 'value': os.getenv('REPORT_LOOKBACK_DAYS')},

    {'account': None, 'parameter': 'MAX_TOTP_CONN_RETRY_COUNT', 'value': os.getenv('MAX_TOTP_CONN_RETRY_COUNT')},
    {'account': None, 'parameter': 'MAX_KITE_CONN_RETRY_COUNT', 'value': os.getenv('MAX_KITE_CONN_RETRY_COUNT')},
    {'account': None, 'parameter': 'MAX_SOCKET_RECONNECT_ATTEMPTS',
     'value': os.getenv('MAX_SOCKET_RECONNECT_ATTEMPTS')}, ]
