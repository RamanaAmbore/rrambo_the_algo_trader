import enum
from datetime import time

from dateutil.rrule import weekday


class WeekdayEnum(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    GLOBAL = "GLOBAL"


class Schedule(enum.Enum):
    MARKET = "MARKET"
    WEEKEND = 'WEEKEND'


class source(enum.Enum):
    API = "API"
    MANUAL = "MANUAL"
    WEBSOCKET = "WEBSOCKET"
    REPORTS = "REPORTS"
    FRONTEND = 'FRONTEND'
    CODE = "CODE"


DEFAULT_SCHEDULE_RECORDS = [
    {"weekday": WeekdayEnum.GLOBAL, "schedule_name": "MARKET", "start_time": time(9, 0), "end_time": time(15, 30),
        "is_active": True},
    {"weekday": WeekdayEnum.SATURDAY, "schedule_name": "MARKET", "start_time": None, "end_time": None,
        "is_active": False},
    {"weekday": WeekdayEnum.SUNDAY, "schedule_name": "MARKET", "start_time": None, "end_time": None,
        "is_active": False},
    {"weekday": WeekdayEnum.SATURDAY, "schedule_name": "WEEKEND", "start_time": time(9, 0), "end_time": None,
        "is_active": True}]

DEFAULT_BROKER_ACCOUNTS = [{"account_id": "ZG0790", "broker_name": "Zerodha", "notes": "Haritha account"},
                           {"account_id": "ZJ6294", "broker_name": "Zerodha", "notes": "Ramana account"}, ]

DEFAULT_PARAMETERS = [  # Zerodha Credentials
    {"account_id": "ZG0790", "parameter": "API_KEY", "value": "05hjicsyku3stv9o"},
    {"account_id": "ZG0790", "parameter": "API_SECRET", "value": "2b5npva2x8f8fvd5lxhte3xpn4zh7lc8"},
    {"account_id": "ZG0790", "parameter": "ZERODHA_PASSWORD", "value": "Zerodha01#"},
    {"account_id": "ZG0790", "parameter": "TOTP_TOKEN", "value": "YJPG3JUXH365ENNG7LNGEWRMQWQBKSSZ"},

    # Market Configurations
    {"account_id": None, "parameter": "INSTRUMENT_TOKEN", "value": "260105"},
    {"account_id": None, "parameter": "DATA_FETCH_INTERVAL", "value": "5"},

    # Logging Configuration
    {"account_id": None, "parameter": "DEBUG_LOG_FILE", "value": "D:/rrambo_trader_new/logs/debug.log"},
    {"account_id": None, "parameter": "ERROR_LOG_FILE", "value": "D:/rrambo_trader_new/logs/error.log"},
    {"account_id": None, "parameter": "CONSOLE_LOG_LEVEL", "value": "DEBUG"},
    {"account_id": None, "parameter": "FILE_LOG_LEVEL", "value": "DEBUG"},
    {"account_id": None, "parameter": "ERROR_LOG_LEVEL", "value": "ERROR"},

    # URLs
    {"account_id": None, "parameter": "BASE_URL", "value": "https://kite.zerodha.com"},
    {"account_id": None, "parameter": "LOGIN_URL", "value": "https://kite.zerodha.com/api/login"},
    {"account_id": None, "parameter": "TWOFA_URL", "value": "https://kite.zerodha.com/api/twofa"},
    {"account_id": None, "parameter": "INSTRUMENTS_URL", "value": "https://api.kite.trade/instruments"},
    {"account_id": None, "parameter": "REDIRECT_URL", "value": "http://localhost:8080/apis/broker/login/zerodha"},

    # Database Configuration
    {"account_id": None, "parameter": "SQLITE_DB", "value": "False"},
    {"account_id": None, "parameter": "SQLITE_PATH", "value": "D:/rrambo_trader_new/db/sqlite.db"},

    {"account_id": None, "parameter": "ACCESS_TOKEN_VALIDITY", "value": "24"},

    # Other Configurations
    {"account_id": None, "parameter": "DB_DEBUG", "value": "True"},
    {"account_id": None, "parameter": "DOWNLOAD_TRADEBOOK", "value": "True"},
    {"account_id": None, "parameter": "DOWNLOAD_PL", "value": "True"},
    {"account_id": None, "parameter": "DOWNLOAD_LEDGER", "value": "True"},
    {"account_id": None, "parameter": "DOWNLOAD_POSITIONS", "value": "False"},
    {"account_id": None, "parameter": "DOWNLOAD_HOLDINGS", "value": "False"},
    {"account_id": None, "parameter": "DOWNLOAD_DIR", "value": "D:/rrambo_trader_new/data"},
    {"account_id": None, "parameter": "REPORT_START_DATE", "value": "2017-03-01"},
    {"account_id": None, "parameter": "REPORT_LOOKBACK_DAYS", "value": "30"}, ]
