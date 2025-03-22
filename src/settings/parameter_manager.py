import threading
from types import SimpleNamespace
from typing import Dict, Any

from dotenv import load_dotenv, dotenv_values

from src.helpers.utils import parse_value

load_dotenv()

# Thread safety lock
_lock = threading.Lock()

# Database Configuration
env_vars = {k: parse_value(v) for k, v in dotenv_values().items()}
parms = SimpleNamespace(**env_vars)

ACCOUNT_CREDENTIALS: Dict[str, Dict[str, Any]] = {}


def refresh_parameters(records, refresh=False) -> None:
    """Reset parameters from database records."""
    global ACCOUNT_CREDENTIALS
    with _lock:  # Thread-safe parameter updates
        try:
            if ACCOUNT_CREDENTIALS and not refresh:
                return
            for record in records:
                account = None if record.account is None else record.account.strip()
                parameter = None if record.parameter is None else record.parameter.strip()
                record_type = None if record.type is None else record.type.strip()
                value = parse_value(record.value, record_type)
                if account is None:
                    setattr(parms, parameter, value)
                    continue
                if account not in ACCOUNT_CREDENTIALS:
                    ACCOUNT_CREDENTIALS[account] = {}
                ACCOUNT_CREDENTIALS[account][parameter] = value


        except Exception as e:
            print(f"Error resetting parameters: {e}")
            raise SystemExit(1)  # Fail immediately if an error occurs


def get_credentials(user_id: str) -> Dict[str, Any]:
    """Get credentials for a specific user."""
    with _lock:  # Thread-safe credential access
        if user_id not in ACCOUNT_CREDENTIALS:
            raise KeyError(f"No credentials found for user {user_id}")

        return dict(ACCOUNT_CREDENTIALS[user_id])  # Return a deep copy
