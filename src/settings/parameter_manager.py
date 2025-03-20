import os
import threading
from types import SimpleNamespace
from typing import Dict, Any

from dotenv import load_dotenv

from src.helpers.cipher_utils import decrypt_text
from src.helpers.utils import parse_value

load_dotenv('src/settings/environment_manager')

# Thread safety lock
_lock = threading.Lock()

# Database Configuration
try:
    parms = SimpleNamespace(
        SQLITE_DB=os.getenv("SQLITE_DB").lower() == "true",
        SQLITE_PATH=os.getenv("SQLITE_PATH"),
        POSTGRES_URL=os.getenv("POSTGRES_URL"),
        DROP_TABLES=os.getenv("DROP_TABLES").lower() == "true",
        DB_DEBUG=os.getenv('DB_DEBUG').lower() == 'true',

        # Logging Configuration
        DEBUG_LOG_FILE=os.getenv("DEBUG_LOG_FILE"),
        ERROR_LOG_FILE=os.getenv("ERROR_LOG_FILE"),
        CONSOLE_LOG_LEVEL=os.getenv("CONSOLE_LOG_LEVEL"),
        FILE_LOG_LEVEL=os.getenv("FILE_LOG_LEVEL"),
        ERROR_LOG_LEVEL=os.getenv("ERROR_LOG_LEVEL"),

        # Security Configuration
        ENCRYPTION_KEY=os.getenv('ENCRYPTION_KEY'),

        # Dynamic Parameters
        DEFAULT_ACCOUNT=os.getenv('DEFAULT_ACCOUNT'),
    )
except Exception as e:
    print(f"Error initializing configuration parameters: {e}")
    raise SystemExit(1)  # Immediately exit the script on failure

USER_CREDENTIALS: Dict[str, Dict[str, Any]] = {}


def refresh_parameters(records, refresh=False) -> None:
    """Reset parameters from database records."""
    global USER_CREDENTIALS
    with _lock:  # Thread-safe parameter updates
        try:
            if USER_CREDENTIALS and not refresh:
                return
            for record in records:
                account = None if record.account is None else record.account.strip()
                value = parse_value(value, record_type)
                parameter = None if record.parameter is None else record.parameter.strip()
                record_type = None if record.type is None else record.type.strip()

                if account not in USER_CREDENTIALS:
                    USER_CREDENTIALS[account] = {}
                    USER_CREDENTIALS[account][parameter] = value
                else:
                    setattr(parms, parameter, value)
        except Exception as e:
            print(f"Error resetting parameters: {e}")
            raise SystemExit(1)  # Fail immediately if an error occurs


def get_credentials(user_id: str) -> Dict[str, Any]:
    """Get credentials for a specific user."""
    with _lock:  # Thread-safe credential access
        if user_id not in USER_CREDENTIALS:
            raise KeyError(f"No credentials found for user {user_id}")

        return dict(USER_CREDENTIALS[user_id])  # Return a deep copy
