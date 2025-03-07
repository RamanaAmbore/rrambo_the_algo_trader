import logging
from collections import defaultdict

from sqlalchemy import event
from sqlalchemy.orm import Session
from utils.db_connection import DbConnection as Db
from models import Settings

logger = logging.getLogger(__name__)


def fetch_all_records(sync=True):
    """Fetch all settings as a nested dictionary."""
    try:
        with Db.get_session(sync) as session:
            records = session.query(Settings).all()
        result = defaultdict(lambda: defaultdict(dict))
        unique_account_ids = set()

        for record in records:
            # Collect unique account_ids
            if record.account_id is not None:
                unique_account_ids.add(record.account_id)

        for record in records:
            # Assign parameters to specific accounts
            ids = unique_account_ids if record.account_id is None else [record.account_id]
            for acc_id in ids:
                result[acc_id][record.parameter] = record.parameter_value

        return result
    except Exception as e:
        print('Error in fetching records from parameter table: {e}')
        return {}


@event.listens_for(Settings.__table__, "after_create")
def initialize_market_hours(target, connection, **kwargs):
    """Event listener to initialize default market hours after table creation."""

    default_records = [  # Zerodha Credentials
        {"account_id": "ZG0790", "key": "API_KEY", "value": "05hjicsyku3stv9o"},
        {"account_id": "ZG0790", "key": "API_SECRET", "value": "2b5npva2x8f8fvd5lxhte3xpn4zh7lc8"},
        {"account_id": "ZG0790", "key": "ZERODHA_USERNAME", "value": "ZG0790"},
        {"account_id": "ZG0790", "key": "ZERODHA_PASSWORD", "value": "Zerodha01#"},
        {"account_id": "ZG0790", "key": "TOTP_TOKEN", "value": "YJPG3JUXH365ENNG7LNGEWRMQWQBKSSZ"},

        # Market Configurations
        {"account_id": "ZG0790", "key": "INSTRUMENT_TOKEN", "value": "260105"},
        {"account_id": "ZG0790", "key": "DATA_FETCH_INTERVAL", "value": "5"},

        # Logging Configuration
        {"account_id": "ZG0790", "key": "DEBUG_LOG_FILE", "value": "D:/rrambo_trader_new/logs/debug.log"},
        {"account_id": "ZG0790", "key": "ERROR_LOG_FILE", "value": "D:/rrambo_trader_new/logs/error.log"},
        {"account_id": "ZG0790", "key": "CONSOLE_LOG_LEVEL", "value": "DEBUG"},
        {"account_id": "ZG0790", "key": "FILE_LOG_LEVEL", "value": "DEBUG"},
        {"account_id": "ZG0790", "key": "ERROR_LOG_LEVEL", "value": "ERROR"},

        # URLs
        {"account_id": "ZG0790", "key": "BASE_URL", "value": "https://kite.zerodha.com"},
        {"account_id": "ZG0790", "key": "LOGIN_URL", "value": "https://kite.zerodha.com/api/login"},
        {"account_id": "ZG0790", "key": "TWOFA_URL", "value": "https://kite.zerodha.com/api/twofa"},
        {"account_id": "ZG0790", "key": "INSTRUMENTS_URL", "value": "https://api.kite.trade/instruments"},
        {"account_id": "ZG0790", "key": "REDIRECT_URL", "value": "http://localhost:8080/apis/broker/login/zerodha"},

        # Database Configuration
        {"account_id": "ZG0790", "key": "SQLITE_DB", "value": "False"},
        {"account_id": "ZG0790", "key": "SQLITE_PATH", "value": "D:/rrambo_trader_new/db/sqlite.db"},

        {"account_id": "ZG0790", "key": "ACCESS_TOKEN_VALIDITY", "value": "24"},

        # Other Configurations
        {"account_id": "ZG0790", "key": "DB_DEBUG", "value": "True"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_TRADEBOOK", "value": "True"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_PL", "value": "True"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_LEDGER", "value": "True"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_POSITIONS", "value": "False"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_HOLDINGS", "value": "False"},
        {"account_id": "ZG0790", "key": "DOWNLOAD_DIR", "value": "D:/rrambo_trader_new/data"},
        {"account_id": "ZG0790", "key": "REPORT_START_DATE", "value": "2017-03-01"},
        {"account_id": "ZG0790", "key": "REPORT_LOOKBACK_DAYS", "value": "30"}, ]
    connection.execute(target.insert(), default_records)
