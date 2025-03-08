import os
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Any, Optional



import yaml
from dotenv import load_dotenv

# from services.parameters import fetch_all_records

# Load environment variables from .env
load_dotenv()


# Function to load YAML file
def load_yaml(file_name: str) -> dict:
    """
    Load constants from a YAML file.
    
    Args:
        file_name: Name of the YAML file in settings directory
    
    Returns:
        dict: Loaded YAML content
    """
    try:
        path = Path(__file__).parent.parent / "settings" / file_name
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {file_name}: {e}")
        raise


# Load constants
try:
    constants = SimpleNamespace(**load_yaml("constants.yaml"))
    sc = SimpleNamespace(**constants.source)
except Exception as e:
    print(f"Failed to load constants: {e}")
    raise


class Env:
    """Environment configuration and parameter management."""
    
    # Database and Logging Configuration (unchanged)
    SQLITE_DB: bool = os.getenv("SQLITE_DB", "True").lower() == "true"
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "database.db")
    POSTGRES_URL: Optional[str] = os.getenv("POSTGRES_URL")

    # Logging Configuration
    DEBUG_LOG_FILE: str = os.getenv("DEBUG_LOG_FILE", "logs/debug.log")
    ERROR_LOG_FILE: str = os.getenv("ERROR_LOG_FILE", "logs/error.log")
    CONSOLE_LOG_LEVEL: str = os.getenv("CONSOLE_LOG_LEVEL", "DEBUG")
    FILE_LOG_LEVEL: str = os.getenv("FILE_LOG_LEVEL", "DEBUG")
    ERROR_LOG_LEVEL: str = os.getenv("ERROR_LOG_LEVEL", "ERROR")
    DB_DEBUG: bool = os.getenv('DB_DEBUG', 'false').lower() == 'true'
    ENCRYPTION_KEY: str = os.getenv('ENCRYPTION_KEY', '')

    # Dynamic Parameters (converted to lowercase)
    USER_CREDENTIALS: Dict[str, Dict[str, Any]] = {}
    INSTRUMENT_TOKEN: Optional[str] = None
    DATA_FETCH_INTERVAL: Optional[int] = None
    
    # URLs (converted to lowercase)
    BASE_URL: Optional[str] = None
    LOGIN_URL: Optional[str] = None
    TWOFA_URL: Optional[str] = None
    INSTRUMENT_URL: Optional[str] = None
    REDIRECT_URL: Optional[str] = None
    
    # Token Configuration (converted to lowercase)
    ACCESS_TOKEN_VALIDITY: Optional[int] = None
    
    # Download Configuration (converted to lowercase)
    DOWNLOAD_TRADEBOOK: Optional[bool] = None
    DOWNLOAD_PL: Optional[bool] = None
    DOWNLOAD_LEDGER: Optional[bool] = None
    DOWNLOAD_POSITIONS: Optional[bool] = None
    DOWNLOAD_HOLDINGS: Optional[bool] = None
    DOWNLOAD_DIR: Optional[str] = None
    REPORT_START_DATE: Optional[datetime] = None
    REPORT_LOOKBACK_DAYS: Optional[int] = None

    @classmethod
    def reset_parms(cls, records, refresh=False) -> None:
        try:
            if not cls.USER_CREDENTIALS or refresh:
                unique_BrokerAccounts = {record.account for record in records if record.account}

                for record in records:
                    # Handle account-specific parameters
                    if record.account:
                        if record.account not in cls.USER_CREDENTIALS:
                            cls.USER_CREDENTIALS[record.account] = {}
                        cls.USER_CREDENTIALS[record.account][record.parameter] = record.value
                        continue
                    
                    # Handle global parameters
                    param_value = record.value.strip()
                    param_name = record.parameter.strip()  # Convert to lowercase
                    
                    if hasattr(cls, param_name):
                        # Convert value to appropriate type
                        if isinstance(getattr(cls, param_name), bool):
                            setattr(cls, param_name, param_value.lower() == 'true')
                        elif isinstance(getattr(cls, param_name), int):
                            setattr(cls, param_name, int(param_value))
                        else:
                            setattr(cls, param_name, param_value)
        except Exception as e:
            print(f"Error resetting parameters: {e}")
            raise

    @classmethod
    def get_credentials(cls, user_id: str) -> Dict[str, Any]:
        if not cls.USER_CREDENTIALS:
            cls.reset_parms()
        
        if user_id not in cls.USER_CREDENTIALS:
            print(f"No credentials found for user {user_id}")
            raise KeyError(f"No credentials found for user {user_id}")
            
        return cls.USER_CREDENTIALS[user_id]


def main():
    """Test function to verify parameter loading functionality."""
    try:
        print("Testing parameter loading...")
        
        # Reset parameters
        Env.reset_parms()
        
        # Print loaded parameters
        print("Global Parameters:")
        for param_name in ['instrument_token', 'data_fetch_interval', 'base_url', 
                          'access_token_validity', 'download_dir']:
            value = getattr(Env, param_name)
            print(f"{param_name}: {value}")
        
        # Print user credentials if any exist
        if Env.USER_CREDENTIALS:
            print("\nUser Credentials:")
            for user_id, creds in Env.USER_CREDENTIALS.items():
                print(f"User {user_id}:")
                for param, value in creds.items():
                    print(f"  {param}: {value}")
        else:
            print("No user credentials found")

    except Exception as e:
        print(f"Error testing parameters: {e}")
        raise


# if __name__ == "__main__":
#     main()
