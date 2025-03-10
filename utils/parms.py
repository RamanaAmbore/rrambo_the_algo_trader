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


class Parms:
    """Environment configuration and parameter management."""
    
    # Thread safety lock
    _lock = threading.Lock()
    _initialized = False
    
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
    INSTRUMENT_TOKEN: Optional[str] = ''
    DATA_FETCH_INTERVAL: Optional[int] = 0
    BASE_URL: Optional[str] = ''
    LOGIN_URL: Optional[str] = ''
    TWOFA_URL: Optional[str] = ''
    INSTRUMENT_URL: Optional[str] = ''
    REDIRECT_URL: Optional[str] = ''
    ACCESS_TOKEN_VALIDITY: Optional[int] = 0

    # Download Configuration
    DOWNLOAD_TRADEBOOK: Optional[bool] = True
    DOWNLOAD_PNL: Optional[bool] = True
    DOWNLOAD_LEDGER: Optional[bool] = True
    DOWNLOAD_DIR: Optional[str] = ''
    REPORT_START_DATE: Optional[datetime] = ''
    REPORT_LOOKBACK_DAYS: Optional[int] = 0
    USERS: list = []
    MAX_SELENIUM_RETRIES=0

    @classmethod
    def refresh_parms(cls, records=None, refresh=False) -> None:
        """Reset parameters from database records."""
        with cls._lock:  # Thread-safe parameter updates
            try:
                if not cls._initialized or refresh:
                    if records is None:
                        return
                        
                    temp_credentials = {}
                    for record in records:
                        account = None if record.account is None else record.account.strip()
                        value = None if record.value is None else record.value.strip()
                        parameter = None if record.parameter is None else record.parameter.strip()

                        if account:
                            if account not in temp_credentials:
                                temp_credentials[account] = {}
                            temp_credentials[account][parameter] = None if value is None else decrypt_text(value)
                            continue

                        if hasattr(cls, parameter):
                            if isinstance(getattr(cls, parameter), bool):
                                setattr(cls, parameter, value.lower() == 'true')
                            elif isinstance(getattr(cls, parameter), int):
                                setattr(cls, parameter, int(value))
                            else:
                                setattr(cls, parameter, value)
                    
                    cls.USER_CREDENTIALS = temp_credentials
                    cls.USERS = list(cls.USER_CREDENTIALS.keys())
                    cls._initialized = True
            except Exception as e:
                print(f"Error resetting parameters: {e}")
                raise

    @classmethod
    def get_credentials(cls, user_id: str) -> Dict[str, Any]:
        """Get credentials for a specific user."""
        with cls._lock:  # Thread-safe credential access
            if not cls._initialized:
                print(f"Parameters not initialized")
                raise RuntimeError("Parameters not initialized")

            if user_id not in cls.USER_CREDENTIALS:
                print(f"No credentials found for user {user_id}")
                raise KeyError(f"No credentials found for user {user_id}")

            return dict(cls.USER_CREDENTIALS[user_id])  # Return a deep copy

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if parameters are initialized."""
        with cls._lock:
            return cls._initialized