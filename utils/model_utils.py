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
    {"schedule": "MARKET"},
    {"schedule": "WEEKEND"}]

DEFAULT_SCHEDULE_TIME_RECORDS = [
    {"weekday": WeekdayEnum.GLOBAL, "schedule": "MARKET", "start_time": time(9, 0), "end_time": time(15, 30),
        "is_active": True},
    {"weekday": WeekdayEnum.SATURDAY, "schedule": "MARKET", "start_time": None, "end_time": None,
        "is_active": False},
    {"weekday": WeekdayEnum.SUNDAY, "schedule": "MARKET", "start_time": None, "end_time": None,
        "is_active": False},
    {"weekday": WeekdayEnum.SATURDAY, "schedule": "WEEKEND", "start_time": time(9, 0), "end_time": None,
        "is_active": True}]

DEFAULT_BROKER_ACCOUNTS = [{"account": "ZG0790", "broker_name": "Zerodha", "notes": "Haritha account"},
                           {"account": "ZJ6294", "broker_name": "Zerodha", "notes": "Ramana account"}, ]

DEFAULT_PARAMETERS = [  # Zerodha Credentials
    {"account": "ZG0790", "parameter": "API_KEY", "value": "05hjicsyku3stv9o"},
    {"account": "ZG0790", "parameter": "API_SECRET", "value": "2b5npva2x8f8fvd5lxhte3xpn4zh7lc8"},
    {"account": "ZG0790", "parameter": "ZERODHA_PASSWORD", "value": "Zerodha01#"},
    {"account": "ZG0790", "parameter": "TOTP_TOKEN", "value": "YJPG3JUXH365ENNG7LNGEWRMQWQBKSSZ"},

    {"account": "ZJ6294", "parameter": "API_KEY", "value": None},
    {"account": "ZJ6294", "parameter": "API_SECRET", "value": None},
    {"account": "ZJ6294", "parameter": "ZERODHA_PASSWORD", "value": "Anirudh01#"},
    {"account": "ZJ6294", "parameter": "TOTP_TOKEN", "value": "W765AAJV7VU55C6LNBEIFSCWZ2LCALXB"},

    # Market Configurations
    {"account": None, "parameter": "INSTRUMENT_TOKEN", "value": "260105"},
    {"account": None, "parameter": "DATA_FETCH_INTERVAL", "value": "5"},

    # Logging Configuration
    {"account": None, "parameter": "DEBUG_LOG_FILE", "value": "D:/rrambo_trader_new/logs/debug.log"},
    {"account": None, "parameter": "ERROR_LOG_FILE", "value": "D:/rrambo_trader_new/logs/error.log"},
    {"account": None, "parameter": "CONSOLE_LOG_LEVEL", "value": "DEBUG"},
    {"account": None, "parameter": "FILE_LOG_LEVEL", "value": "DEBUG"},
    {"account": None, "parameter": "ERROR_LOG_LEVEL", "value": "ERROR"},

    # URLs
    {"account": None, "parameter": "BASE_URL", "value": "https://kite.zerodha.com"},
    {"account": None, "parameter": "LOGIN_URL", "value": "https://kite.zerodha.com/api/login"},
    {"account": None, "parameter": "TWOFA_URL", "value": "https://kite.zerodha.com/api/twofa"},
    {"account": None, "parameter": "INSTRUMENTS_URL", "value": "https://api.kite.trade/instruments"},
    {"account": None, "parameter": "REDIRECT_URL", "value": "http://localhost:8080/apis/broker/login/zerodha"},

    # Database Configuration
    {"account": None, "parameter": "SQLITE_DB", "value": "False"},
    {"account": None, "parameter": "SQLITE_PATH", "value": "D:/rrambo_trader_new/db/sqlite.db"},

    {"account": None, "parameter": "ACCESS_TOKEN_VALIDITY", "value": "24"},

    # Other Configurations
    {"account": None, "parameter": "DB_DEBUG", "value": "True"},
    {"account": None, "parameter": "DOWNLOAD_TRADEBOOK", "value": "True"},
    {"account": None, "parameter": "DOWNLOAD_PL", "value": "True"},
    {"account": None, "parameter": "DOWNLOAD_LEDGER", "value": "True"},
    {"account": None, "parameter": "DOWNLOAD_POSITIONS", "value": "False"},
    {"account": None, "parameter": "DOWNLOAD_HOLDINGS", "value": "False"},
    {"account": None, "parameter": "DOWNLOAD_DIR", "value": "D:/rrambo_trader_new/data"},
    {"account": None, "parameter": "REPORT_START_DATE", "value": "2017-03-01"},
    {"account": None, "parameter": "REPORT_LOOKBACK_DAYS", "value": "30"}, ]
