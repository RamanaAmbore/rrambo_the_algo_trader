import os
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
constants = load_yaml("constants.yaml")

# Zerodha Credentials
ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
ZERODHA_TOTP_SECRET = os.getenv("ZERODHA_TOTP_SECRET")
ZERODHA_USERNAME = os.getenv("ZERODHA_USERNAME")
ZERODHA_PASSWORD = os.getenv("ZERODHA_PASSWORD")

# Market Constants from YAML
INSTRUMENT_TOKEN = constants["market"]["instrument_token"]
DATA_FETCH_INTERVAL = constants["market"]["data_fetch_interval"]

# Logging Configuration
DEBUG_LOG_FILE = os.getenv("DEBUG_LOG_FILE", "logs/debug.log")
ERROR_LOG_FILE = os.getenv("ERROR_LOG_FILE", "logs/error.log")
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")
FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "DEBUG")
ERROR_LOG_LEVEL = os.getenv("ERROR_LOG_LEVEL", "ERROR")
