import os
from datetime import time
from types import SimpleNamespace

from dotenv import load_dotenv, dotenv_values

from src.helpers.cipher_utils import encrypt_text

loaded = False


def load_env():
    if loaded:
        return
    load_dotenv()


load_env()

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
    FRIDAY='Friday', SATURDAY='Saturday', SUNDAY='Sunday', GLOBAL='*'
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

Thread = SimpleNamespace(**{"start_socket_ticker": Schedule.MARKET, "sync_stock_reports": Schedule.PRE_MARKET,
                            "sync_instrument_list": Schedule.PRE_MARKET,
                            "sync_holdings": Schedule.PRE_MARKET, "sync_positions": Schedule.PRE_MARKET,
                            'sync_watchlist': Schedule.PRE_MARKET
                            })

# Default configurations
DEF_ACCESS_TOKENS = (
    {'account': Account.ACCOUNT1, 'token': None},
    {'account': Account.ACCOUNT2, 'token': None}
)

DEF_THREAD_LIST = tuple({"thread": thread} for thread in vars(Thread) if not thread.startswith('_'))

DEF_SCHEDULES = tuple(
    {"schedule": schedule} for schedule in Schedule.__dict__.values() if not schedule.startswith('_'))

DEF_SCHEDULE_TIME = (
    {'market_day': Weekday.GLOBAL, 'schedule': Schedule.MARKET, 'start_time': '09:00',
     'end_time': '15:30',
     'is_market_open': True},
    {'market_day': Weekday.GLOBAL, 'exchange': 'MCX', 'schedule': Schedule.MARKET, 'start_time': '09:00',
     'end_time': '23:00',
     'is_market_open': True},
    {'market_day': Weekday.SATURDAY, 'schedule': Schedule.MARKET, 'is_market_open': False},
    {'market_day': Weekday.SATURDAY, 'exchange': 'MCX', 'schedule': Schedule.MARKET, 'is_market_open': False},
    {'market_day': Weekday.SUNDAY, 'schedule': Schedule.MARKET, 'is_market_open': False},
    {'market_day': Weekday.SUNDAY, 'exchange': 'MCX', 'schedule': Schedule.MARKET, 'is_market_open': False},
    {'market_day': Weekday.GLOBAL, 'schedule': Schedule.PRE_MARKET, 'start_time': '08:30', 'end_time': '09:30',
     'is_market_open': True},
    {'market_day': Weekday.GLOBAL, 'exchange': 'MCX', 'schedule': Schedule.PRE_MARKET, 'start_time': '08:30',
     'end_time': '09:30',
     'is_market_open': True},
    {'market_day': Weekday.SUNDAY, 'schedule': Schedule.PRE_MARKET, 'start_time': '08:30', 'end_time': '09:30',
     'is_market_open': False},
    {'market_day': Weekday.SUNDAY, 'exchange': 'MCX', 'schedule': Schedule.PRE_MARKET, 'start_time': '08:30',
     'end_time': '09:30',
     'is_market_open': False},
)

DEF_THREAD_SCHEDULE = tuple({'thread': k, 'schedule': v} for k, v in vars(Thread).items())

DEF_BROKER_ACCOUNTS = (
    {'account': Account.ACCOUNT1, 'broker_name': 'Zerodha', 'notes': 'Haritha account'},
    {'account': Account.ACCOUNT2, 'broker_name': 'Zerodha', 'notes': 'Ramana account'},
    {'account': '*', 'broker_name': 'Zerodha', 'notes': 'Ramana account'}
)

DEF_WATCH_LIST = (
    {'watchlist': 'INDEX_MINI'},
    {'watchlist': 'INDEX'},
    {'watchlist': 'OPTION_STOCKS'},
    {'watchlist': 'WATCHLIST'},
    {'watchlist': 'COMMODITIES'}
)

DEF_WATCHLIST_SYMBOLS = (
    {"watchlist": "INDEX_MINI", "tradingsymbol": "NIFTY 50", "exchange": "NSE"},
    {"watchlist": "INDEX_MINI", "tradingsymbol": "SENSEX", "exchange": "BSE"},
    {"watchlist": "INDEX_MINI", "tradingsymbol": "NIFTY BANK", "exchange": "NSE"},
    {"watchlist": "INDEX_MINI", "tradingsymbol": "INDIA VIX", "exchange": "NSE"},

    {"watchlist": "INDEX", "tradingsymbol": "NIFTY MIDCAP 100", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY IT", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY REALTY", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY INFRA", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY ENERGY", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY FMCG", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY MNC", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY PHARMA", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY PSE", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY PSU BANK", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY SERV SECTOR", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY AUTO", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY METAL", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "NIFTY MEDIA", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "HANGSENG BEES-NAV", "exchange": "NSE"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXGOLDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXMETLDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXCRUDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXCOPRDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXCOMPDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXBULLDEX", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXENERGY", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXAGRI", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXMETAL", "exchange": "MCX"},
    {"watchlist": "INDEX", "tradingsymbol": "MCXSILVDEX", "exchange": "MCX"},

    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXGOLDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXMETLDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXCRUDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXCOPRDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXCOMPDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXBULLDEX", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXENERGY", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXAGRI", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXMETAL", "exchange": "MCX"},
    {"watchlist": "COMMODITIES", "tradingsymbol": "MCXSILVDEX", "exchange": "MCX"},

    {"watchlist": "WATCHLIST", "tradingsymbol": "RELIANCE", "exchange": "NSE"}
)

DEF_EXCHANGE_LIST = (
    {"exchange": "*", "desc": "all exchanges"},
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
        {'account': Account.ACCOUNT1, 'parameter': 'API_KEY', 'value': encrypt_text(os.getenv('ACCOUNT1_API_KEY')),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'API_SECRET',
         'value': encrypt_text(os.getenv('ACCOUNT1_API_SECRET')),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'PASSWORD', 'value': encrypt_text(os.getenv('ACCOUNT1_PASSWORD')),
         'encrypted': True},
        {'account': Account.ACCOUNT1, 'parameter': 'TOTP_TOKEN',
         'value': encrypt_text(os.getenv('ACCOUNT1_TOTP_TOKEN')),
         'encrypted': True},

        {'account': Account.ACCOUNT2, 'parameter': 'API_KEY', 'value': encrypt_text(os.getenv('ACCOUNT2_API_KEY')),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'API_SECRET',
         'value': encrypt_text(os.getenv('ACCOUNT2_API_SECRET')),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'PASSWORD', 'value': encrypt_text(os.getenv('ACCOUNT2_PASSWORD')),
         'encrypted': True},
        {'account': Account.ACCOUNT2, 'parameter': 'TOTP_TOKEN',
         'value': encrypt_text(os.getenv('ACCOUNT2_TOTP_TOKEN')),
         'encrypted': True},
    ])
