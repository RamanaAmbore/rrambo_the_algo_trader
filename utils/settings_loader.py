import os
from types import SimpleNamespace

import yaml
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# Function to load YAML file
def load_yaml(file_name):
    """Load constants from a YAML file."""
    path = os.path.join(os.path.dirname(__file__), "..", "settings", file_name)  # Updated path
    with open(path, "r") as file:
        return yaml.safe_load(file)


# Load constants
constants = SimpleNamespace(**load_yaml("constants.yaml"))
sc = SimpleNamespace(**constants.source)


class Env:
    # Database Configuration
    SQLITE_DB = os.getenv("SQLITE_DB", "True").lower() == "true"
    SQLITE_PATH = os.getenv("SQLITE_PATH", "database.db")

    # PostgresSQL Configuration (Only used if SQLITE_DB=False)
    POSTGRES_URL = os.getenv("POSTGRES_URL")


    # Logging Configuration
    DEBUG_LOG_FILE = os.getenv("DEBUG_LOG_FILE", "logs/debug.log")
    ERROR_LOG_FILE = os.getenv("ERROR_LOG_FILE", "logs/error.log")
    CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")
    FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "DEBUG")
    ERROR_LOG_LEVEL = os.getenv("ERROR_LOG_LEVEL", "ERROR")
    DB_DEBUG = os.getenv('DB_DEBUG').lower() == 'true'

    API_KEY = None
    API_SECRET = None
    ZERODHA_USERNAME = None
    ZERODHA_PASSWORD = None
    TOTP_TOKEN = None

    # Market Configurations
    INSTRUMENT_TOKEN = None
    DATA_FETCH_INTERVAL = None

    # urls
    BASE_URL = None
    LOGIN_URL = None
    TWOFA_URL = None
    INSTRUMENTS_URL = None
    REDIRECT_URL = None

    ACCESS_TOKEN_VALIDITY = None

    DOWNLOAD_TRADEBBOOK = None
    DOWNLOAD_PL = None
    DOWNLOAD_LEDGER = None
    DOWNLOAD_POSITIONS = None
    DOWNLOAD_HOLDINGS = None
    DOWNLOAD_DIR = None
    REPORT_START_DATE = None
    REPORT_LOOKBACK_DAYS = None


    @classmethod
    def update_settings(account_settings_dict):
        pass

