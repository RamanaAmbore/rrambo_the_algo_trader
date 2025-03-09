import os
import threading
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Any, Optional

import yaml
from dotenv import load_dotenv

from utils.cipher_utils import decrypt_text

load_dotenv()


def load_yaml(file_name: str) -> dict:
    """Load constants from a YAML file."""
    try:
        path = Path(__file__).parent.parent / "settings" / file_name
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_name}: {e}")
        raise


try:
    constants = SimpleNamespace(**load_yaml("constants.yaml"))
    sc = SimpleNamespace(**constants.source)
except Exception as e:
    print(f"Failed to load constants: {e}")
    raise


class Parm:
    """Environment configuration and parameter management."""
    
    # Thread safety lock
    _lock = threading.Lock()
    
    # Database Configuration
    SQLITE_DB: bool = os.getenv("SQLITE_DB", "True").lower() == "true"
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "database.db")
    POSTGRES_URL: Optional[str] = os.getenv("POSTGRES_URL")
    DROP_TABLES: bool = os.getenv("DROP_TABLES", "True").lower() == "true"
    DB_DEBUG: bool = os.getenv('DB_DEBUG', 'false').lower() == 'true'

    # Logging Configuration
    DEBUG_LOG_FILE: str = os.getenv("DEBUG_LOG_FILE", "logs/debug.log")
    ERROR_LOG_FILE: str = os.getenv("ERROR_LOG_FILE", "logs/error.log")
    CONSOLE_LOG_LEVEL: str = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")
    FILE_LOG_LEVEL: str = os.getenv("FILE_LOG_LEVEL", "DEBUG")
    ERROR_LOG_LEVEL: str = os.getenv("ERROR_LOG_LEVEL", "ERROR")

    # Security Configuration
    ENCRYPTION_KEY: str = os.getenv('ENCRYPTION_KEY', '')

    # Dynamic Parameters
    USER_CREDENTIALS: Dict[str, Dict[str, Any]] = {}
    INSTRUMENT_TOKEN: Optional[str] = None
    DATA_FETCH_INTERVAL: Optional[int] = None
    BASE_URL: Optional[str] = None
    LOGIN_URL: Optional[str] = None
    TWOFA_URL: Optional[str] = None
    INSTRUMENT_URL: Optional[str] = None
    REDIRECT_URL: Optional[str] = None
    ACCESS_TOKEN_VALIDITY: Optional[int] = None

    # Download Configuration
    DOWNLOAD_TRADEBOOK: Optional[bool] = None
    DOWNLOAD_PL: Optional[bool] = None
    DOWNLOAD_LEDGER: Optional[bool] = None
    DOWNLOAD_POSITIONS: Optional[bool] = None
    DOWNLOAD_HOLDINGS: Optional[bool] = None
    DOWNLOAD_DIR: Optional[str] = None
    REPORT_START_DATE: Optional[datetime] = None
    REPORT_LOOKBACK_DAYS: Optional[int] = None
    USERS: list = []

    @classmethod
    def reset_parms(cls, records, refresh=False) -> None:
        """Reset parameters from database records."""
        with cls._lock:  # Thread-safe parameter updates
            try:
                if not cls.USER_CREDENTIALS or refresh:
                    for record in records:
                        account = None if record.account is None else record.account.strip()
                        value = None if record.value is None else record.value.strip()
                        parameter = None if record.parameter is None else record.parameter.strip()

                        if account:
                            if account not in cls.USER_CREDENTIALS:
                                cls.USER_CREDENTIALS[account] = {}
                            cls.USER_CREDENTIALS[account][parameter] = None if value is None else decrypt_text(value)
                            continue

                        if hasattr(cls, parameter):
                            if isinstance(getattr(cls, parameter), bool):
                                setattr(cls, parameter, value.lower() == 'true')
                            elif isinstance(getattr(cls, parameter), int):
                                setattr(cls, parameter, int(value))
                            else:
                                setattr(cls, parameter, value)
                    cls.USERS = list(cls.USER_CREDENTIALS.keys())
            except Exception as e:
                print(f"Error resetting parameters: {e}")
                raise

    @classmethod
    def get_credentials(cls, user_id: str) -> Dict[str, Any]:
        """Get credentials for a specific user."""
        with cls._lock:  # Thread-safe credential access
            if not cls.USER_CREDENTIALS:
                cls.reset_parms()

            if user_id not in cls.USER_CREDENTIALS:
                print(f"No credentials found for user {user_id}")
                raise KeyError(f"No credentials found for user {user_id}")

            return cls.USER_CREDENTIALS[user_id].copy()  # Return a copy for thread safety