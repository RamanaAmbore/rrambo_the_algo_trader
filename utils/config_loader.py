import os
from types import SimpleNamespace

import yaml
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# Function to load YAML file
def load_yaml(file_name):
    """Load constants from a YAML file."""
    path = os.path.join(os.path.dirname(__file__), "..", "config", file_name)  # Updated path
    with open(path, "r") as file:
        return yaml.safe_load(file)


# Load constants
constants = SimpleNamespace(**load_yaml("constants.yaml"))
sc = SimpleNamespace(**constants.source)


class env:
    # Zerodha Credentials
    API_KEY = os.getenv("API_KEY")
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

    # PostgreSQL Configuration (Only used if SQLITE_DB=False)
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    ACCESS_TOKEN_VALIDITY = int(os.getenv("ACCESS_TOKEN_VALIDITY"))

    DB_DEBUG = os.getenv('DB_DEBUG').lower() == 'true'
