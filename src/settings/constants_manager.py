import os
from datetime import time
from types import SimpleNamespace

from dotenv import load_dotenv, dotenv_values

load_dotenv()

INDIAN_TIMEZONE = 'Asia/Kolkata'
EST_TIMEZONE = 'EST'

REPORT = {
    'TRADEBOOK': {
        "url": "https://console.zerodha.com/reports/tradebook",
        "segment": {
            "element": "//label[contains(text(), 'Segment')]/following-sibling::select",
            "values": ["Equity", "Futures & Options"]
        },
        'P&L': None,
        "date_range": "//input[@placeholder='Select range']",
        "button": "//button[@type='submit']",
        "href": "//a[contains(text(), 'CSV')]",
        "prefix": "tradebook",
        "file_regex": r"(tradebook)-([^-]*)-([^-.(]*)(?:[(]\d*[)])?[.](csv)"
    },

    'PNL': {
        "url": "https://console.zerodha.com/reports/pnl",
        "segment": {
            "element": "//label[contains(text(), 'Segment')]/following-sibling::select",
            "values": ["Equity", "Futures & Options"]
        },
        "pnl_type": {  # Fixed key name (was "P&L")
            "element": "//label[contains(text(), 'P&L')]/following-sibling::select",
            "values": ["Realised P&L"]
        },
        "P&L": {
            "element": "//label[contains(text(), 'P&L')]/following-sibling::select",
            "values": ["Realised P&L"]
        },
        "date_range": "//input[@placeholder='Select range']",
        "button": "//button[@class='btn-blue']",
        "href": "//div[contains(text(), 'Download')]",
        "prefix": "pnl",
        "file_regex": r"(pnl)-(.+?)(?:[(]\d+[)])?[.](csv|xlsx)"
    },

    'LEDGER': {
        "url": "https://console.zerodha.com/funds/statement",
        "segment": {
            "element": "//label[contains(text(), 'Category')]/following-sibling::select",
            "values": ["Equity"]
        },
        'P&L': None,
        "date_range": "//input[@placeholder='Date']",
        "button": "//button[@type='submit']",
        "href": "//a[contains(text(), 'CSV')]",
        "prefix": "ledger",
        "file_regex": r"(ledger)-(.+?)(?:[(]\d+[)])?[.](csv|xlsx)"
    }
}

# Define constants using SimpleNamespace instead of Enums
Weekday = SimpleNamespace(
    MONDAY='Monday', TUESDAY='Tuesday', WEDNESDAY='Wednesday', THURSDAY='Thursday',
    FRIDAY='Friday', SATURDAY='Saturday', SUNDAY='Sunday', GLOBAL='GLOBAL'
)

Source = SimpleNamespace(
    API='API', MANUAL='MANUAL', WEBSOCKET='WEBSOCKET', REPORTS='REPORTS', FRONTEND='FRONTEND', CODE='CODE'
)

ThreadStatus = SimpleNamespace(
    IN_PROGRESS="IN_PROGRESS", COMPLETED="COMPLETED", FAILED="FAILED", RESTARTED="RESTARTED"
)

Account = SimpleNamespace(ACCOUNT1=os.getenv('ACCOUNT1'), ACCOUNT2=os.getenv('ACCOUNT2'))

Schedule = SimpleNamespace(MARKET='MARKET', PRE_MARKET='PRE_MARKET')

Type = SimpleNamespace(FLOAT='float', BOOL='bool', INT='int', STR='str')

Thread = SimpleNamespace(**{"socket_ticker": Schedule.MARKET, "sync_stock_reports": Schedule.PRE_MARKET,
                            "sync_stock_list": Schedule.PRE_MARKET,
                            "sync_holdings": Schedule.PRE_MARKET, "sync_positions": Schedule.PRE_MARKET,
                            'update_watch_list': Schedule.PRE_MARKET
                            })

# Default configurations
DEF_ACCESS_TOKENS = (
    {'account': Account.ACCOUNT1, 'token': None},
    {'account': Account.ACCOUNT2, 'token': None}
)

DEF_ALGO_THREADS = tuple({"thread": thread} for thread in vars(Thread) if not thread.startswith('_'))

DEF_ALGO_SCHEDULES = tuple(
    {"schedule": schedule} for schedule in Schedule.__dict__.values() if not schedule.startswith('_'))

DEF_ALGO_SCHEDULE_TIME_RECORDS = (
    {'weekday': Weekday.GLOBAL, 'exchange': None,'schedule': Schedule.MARKET, 'start_time': time(9, 00), 'end_time': time(15, 30),
     'is_active': True},
    {'weekday': Weekday.GLOBAL, 'exchange': 'MCX', 'schedule': Schedule.MARKET, 'start_time': time(8, 30), 'end_time': time(23, 15),
     'is_active': True},
    {'weekday': Weekday.SATURDAY, 'exchange': None,'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None,
     'is_active': False},
    {'weekday': Weekday.SUNDAY, 'exchange': None,'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None, 'is_active': False},
    {'weekday': Weekday.SATURDAY, 'exchange': None,'schedule': Schedule.PRE_MARKET, 'start_time': time(8, 30), 'end_time': None,
     'is_active': True}
)

DEF_THREAD_SCHEDULE_XREF = ({'thread': k, 'schedule': v} for k, v in vars(Thread).items())

DEF_BROKER_ACCOUNTS = (
    {'account': Account.ACCOUNT1, 'broker_name': 'Zerodha', 'notes': 'Haritha account'},
    {'account': Account.ACCOUNT2, 'broker_name': 'Zerodha', 'notes': 'Ramana account'}
)

DEF_WATCHLISTS = (
    {'watchlist': f'{Account.ACCOUNT1}_POSITIONS', 'account': Account.ACCOUNT1},
    {'watchlist': f'{Account.ACCOUNT1}_HOLDINGS', 'account': Account.ACCOUNT1},
    {'watchlist': f'{Account.ACCOUNT2}_POSITIONS', 'account': Account.ACCOUNT2},
    {'watchlist': f'{Account.ACCOUNT2}_HOLDINGS', 'account': Account.ACCOUNT2},
    {'watchlist': 'INDEX_MINI'},
    {'watchlist': 'INDEX'},
    {'watchlist': 'OPTION_STOCKS'},
    {'watchlist': 'HOT_STOCKS'}, {'watchlist': 'TURNAROUND'}, {'watchlist': 'WATCHLIST'}
)

DEF_EXCHANGES = (
    {"exchange": "NSE", "desc": "National Stock Exchange of India"},
    {"exchange": "BSE", "desc": "Bombay Stock Exchange"},
    {"exchange": "NFO", "desc": "NSE Futures & Options (Derivatives)"},
    {"exchange": "BFO", "desc": "BSE Futures & Options (Derivatives)"},
    {"exchange": "CDS", "desc": "Currency Derivatives (NSE)"},
    {"exchange": "MCX", "desc": "Multi Commodity Exchange"},
    {"exchange": "MCXSX", "desc": "MCX Stock Exchange (Deprecated, now part of CDS)"},
)

# Load environment variables from .env file
env_vars = dotenv_values()
DEF_PARAMETERS = tuple(
    [{'parameter': key, 'value': val} for key, val in env_vars.items() if not key.startswith('ACCOUNT')] + [
        {'account': Account.ACCOUNT1, 'parameter': 'API_KEY', 'value': os.getenv('ACCOUNT1_API_KEY'),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'API_SECRET', 'value': os.getenv('ACCOUNT1_API_SECRET'),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'PASSWORD', 'value': os.getenv('ACCOUNT1_PASSWORD'),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'TOTP_TOKEN', 'value': os.getenv('ACCOUNT1_TOTP_TOKEN'),
         'encrypted': True},

        {'account': Account.ACCOUNT2, 'parameter': 'API_KEY', 'value': os.getenv('ACCOUNT2_API_KEY'),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'API_SECRET', 'value': os.getenv('ACCOUNT2_API_SECRET'),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'PASSWORD', 'value': os.getenv('ACCOUNT2_PASSWORD'),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'TOTP_TOKEN', 'value': os.getenv('ACCOUNT2_TOTP_TOKEN'),
         'encrypted': True},
    ])
