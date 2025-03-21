from dotenv import load_dotenv

load_dotenv()

INDIAN_TIMEZONE = 'Asia/Kolkata'
EST_TIMEZONE = 'EST'

TRADEBOOK = {
    "url": "https://console.zerodha.com/reports/tradebook",
    "segment": {
        "element": "//label[contains(text(), 'Segment')]/following-sibling::select",
        "values": ["Equity", "Futures & Options"]
    },
    "date_range": "//input[@placeholder='Select range']",
    "button": "//button[@type='submit']",
    "href": "//a[contains(text(), 'CSV')]",
    "prefix": "tradebook",
    "file_regex": r"(tradebook)-([^-]*)-([^-.(]*)(?:[(]\d*[)])?[.](csv)"
}
PNL = {
    "url": "https://console.zerodha.com/reports/pnl",
    "segment": {
        "element": "//label[contains(text(), 'Segment')]/following-sibling::select",
        "values": ["Equity", "Futures & Options"]
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
}
LEDGER = {
    "url": "https://console.zerodha.com/funds/statement",
    "segment": {
        "element": "//label[contains(text(), 'Category')]/following-sibling::select",
        "values": ["Equity"]
    },
    "date_range": "//input[@placeholder='Date']",
    "button": "//button[@type='submit']",
    "href": "//a[contains(text(), 'CSV')]",
    "prefix": "ledger",
    "file_regex": r"(ledger)-(.+?)(?:[(]\d+[)])?[.](csv|xlsx)"
}


import os
from types import SimpleNamespace
from dotenv import dotenv_values
from datetime import time

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

Account = SimpleNamespace(ACCOUNT1='ZG0790', ACCOUNT2='ZJ6924')

Schedule = SimpleNamespace(MARKET='MARKET', PRE_MARKET='PRE_MARKET')

Type = SimpleNamespace(FLOAT='float', BOOL='bool', INT='int', STR='str')

Thread = SimpleNamespace(
    SOCKET="SOCKET", SYNC_REPORT_DATA="SYNC_REPORT_DATA", UPDATE_STOCK_LIST="UPDATE_STOCK_LIST",
    UPDATE_HIST_PRICES="UPDATE_HIST_PRICES", UPDATE_WATCHLIST_INSTRUMENTS="UPDATE_WATCHLIST_INSTRUMENTS"
)

# Default configurations
DEFAULT_ACCESS_TOKENS = (
    {'account': Account.ACCOUNT1, 'token': ''},
    {'account': Account.ACCOUNT2, 'token': None}
)

DEFAULT_ALGO_THREADS = tuple({"thread": thread} for thread in Thread.__dict__.values() if not thread.startswith('_'))

DEFAULT_ALGO_SCHEDULES = tuple({"schedule": schedule} for schedule in Schedule.__dict__.values() if not schedule.startswith('_'))

DEFAULT_ALGO_SCHEDULE_TIME_RECORDS = (
    {'weekday': Weekday.GLOBAL, 'schedule': Schedule.MARKET, 'start_time': time(9, 0), 'end_time': time(15, 30), 'is_active': True},
    {'weekday': Weekday.SATURDAY, 'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None, 'is_active': False},
    {'weekday': Weekday.SUNDAY, 'schedule': Schedule.MARKET, 'start_time': None, 'end_time': None, 'is_active': False},
    {'weekday': Weekday.SATURDAY, 'schedule': Schedule.PRE_MARKET, 'start_time': time(9, 0), 'end_time': None, 'is_active': True}
)

DEFAULT_THREAD_SCHEDULE_XREF = (
    {'thread': Thread.SOCKET, 'schedule': Schedule.MARKET},
    {'thread': Thread.SYNC_REPORT_DATA, 'schedule': Schedule.PRE_MARKET},
    {'thread': Thread.UPDATE_STOCK_LIST, 'schedule': Schedule.PRE_MARKET},
    {'thread': Thread.UPDATE_HIST_PRICES, 'schedule': Schedule.PRE_MARKET},
    {'thread': Thread.UPDATE_WATCHLIST_INSTRUMENTS, 'schedule': Schedule.PRE_MARKET}
)

DEFAULT_BROKER_ACCOUNTS = (
    {'account': Account.ACCOUNT1, 'broker_name': 'Zerodha', 'notes': 'Haritha account'},
    {'account': Account.ACCOUNT2, 'broker_name': 'Zerodha', 'notes': 'Ramana account'}
)

DEFAULT_WATCHLISTS = (
    {'watchlist': 'STOCKS'}, {'watchlist': 'STOCKS-TURNAROUND'},
    {'watchlist': 'OPTIONS'}, {'watchlist': 'POSITION-WATCHLIST'}, {'watchlist': 'HOLDING-WATCHLIST'}
)

# Load environment variables from .env file
env_vars = dotenv_values()
DEFAULT_PARAMETERS = tuple([{'parameter': key, 'value': val} for key, val in env_vars.items()] + [
    {'account': Account.ACCOUNT1, 'parameter': 'API_KEY', 'value': os.getenv('ACCOUNT1_API_KEY'), 'encrypted': True},
    {'account': Account.ACCOUNT1, 'parameter': 'API_SECRET', 'value': os.getenv('ACCOUNT1_API_SECRET'), 'encrypted': True},
    {'account': Account.ACCOUNT1, 'parameter': 'PASSWORD', 'value': os.getenv('ACCOUNT1_PASSWORD'), 'encrypted': True},
    {'account': Account.ACCOUNT1, 'parameter': 'TOTP_TOKEN', 'value': os.getenv('ACCOUNT1_TOTP_TOKEN'), 'encrypted': True},
    {'account': Account.ACCOUNT1, 'parameter': 'TWILIO_API_TOKEN', 'value': os.getenv('ACCOUNT1_TWILIO_API_TOKEN'), 'encrypted': True},

    {'account': Account.ACCOUNT2, 'parameter': 'API_KEY', 'value': os.getenv('ACCOUNT2_API_KEY'), 'encrypted': True},
    {'account': Account.ACCOUNT2, 'parameter': 'API_SECRET', 'value': os.getenv('ACCOUNT2_API_SECRET'), 'encrypted': True},
    {'account': Account.ACCOUNT2, 'parameter': 'PASSWORD', 'value': os.getenv('ACCOUNT2_PASSWORD'), 'encrypted': True},
    {'account': Account.ACCOUNT2, 'parameter': 'TOTP_TOKEN', 'value': os.getenv('ACCOUNT2_TOTP_TOKEN'), 'encrypted': True},
    {'account': Account.ACCOUNT1, 'parameter': 'ACCOUNT2_TWILIO_API_TOKEN', 'value': None, 'encrypted': True}
])
