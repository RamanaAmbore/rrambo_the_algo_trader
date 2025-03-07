import os

import yaml
from dotenv import load_dotenv

from models import Settings
# Load environment variables from .env
from utils.logger import get_logger
from utils.db_connection import DbConnection as Db

logger = get_logger(__name__)
load_dotenv()


# Function to load YAML file
def load_yaml(file_name):
    """Load constants from a YAML file."""
    path = os.path.join(os.path.dirname(__file__), "..", "settings", file_name)  # Updated path
    with open(path, "r") as file:
        return yaml.safe_load(file)


class Env:
    """Loads configuration settings dynamically from the database."""

    with Db.get_sync_session() as session:
        values = Settings.get_all_records(session)


    # Zerodha Credentials
    API_KEY = values
    API_SECRET = os.getenv("API_SECRET")
    ZERODHA_USERNAME = os.getenv("ZERODHA_USERNAME")
    ZERODHA_PASSWORD = os.getenv("ZERODHA_PASSWORD")
    TOTP_TOKEN = os.getenv("TOTP_TOKEN")

    # Market Configurations
    INSTRUMENT_TOKEN = os.getenv("INSTRUMENT_TOKEN")
    DATA_FETCH_INTERVAL = os.getenv("DATA_FETCH_INTERVAL")

    # Logging Configuration
    DEBUG_LOG_FILE = os.getenv("DEBUG_LOG_FILE", "logs/debug.log")
    ERROR_LOG_FILE = os.getenv("ERROR_LOG_FILE", "logs/error.log")
    CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")
    FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "DEBUG")
    ERROR_LOG_LEVEL = os.getenv("ERROR_LOG_LEVEL", "ERROR")

    # urls
    BASE_URL = os.getenv("BASE_URL")
    LOGIN_URL = os.getenv("LOGIN_URL")
    TWOFA_URL = os.getenv("TWOFA_URL")
    INSTRUMENTS_URL = os.getenv("INSTRUMENTS_URL")
    REDIRECT_URL = os.getenv("REDIRECT_URL")

    # Database Configuration
    SQLITE_DB = os.getenv("SQLITE_DB", "True").lower() == "true"
    SQLITE_PATH = os.getenv("SQLITE_PATH", "database.db")

    # PostgresSQL Configuration (Only used if SQLITE_DB=False)
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    ACCESS_TOKEN_VALIDITY = int(os.getenv("ACCESS_TOKEN_VALIDITY"))

    DB_DEBUG = os.getenv('DB_DEBUG').lower() == 'true'
    DOWNLOAD_TRADEBBOOK = os.getenv('DOWNLOAD_TRADEBBOOK').lower() == 'true'
    DOWNLOAD_PL = os.getenv('DOWNLOAD_PL').lower() == 'true'
    DOWNLOAD_LEDGER = os.getenv('DOWNLOAD_LEDGER').lower() == 'true'
    DOWNLOAD_POSITIONS = os.getenv('DOWNLOAD_POSITIONS').lower() == 'true'
    DOWNLOAD_HOLDINGS = os.getenv('DOWNLOAD_HOLDINGS').lower() == 'true'
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
    REPORT_START_DATE = os.getenv('REPORT_START_DATE')
    REPORT_LOOKBACK_DAYS = int(os.getenv('REPORT_LOOKBACK_DAYS'))
