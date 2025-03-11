import threading

import requests
from kiteconnect import KiteConnect

from src.services.access_tokens import get_stored_access_tokens
from src.core.db_connect import DbConnect
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager
from src.utils.parameter_manager import sc
from src.utils.utils import generate_totp

logger = get_logger(__name__)


class ZerodhaKite:
    """Handles Kite API authentication and access token management."""

    _lock = threading.Lock()
    _access_tokens = None
    username = ParameterManager.USERS[0]
    _password = ParameterManager.USER_CREDENTIALS[username]['PASSWORD']
    api_key = ParameterManager.USER_CREDENTIALS[username]["API_KEY"]
    _api_secret = ParameterManager.USER_CREDENTIALS[username]["API_SECRET"]
    totp_token = ParameterManager.USER_CREDENTIALS[username]['TOTP_TOKEN']
    login_url = ParameterManager.LOGIN_URL
    twofa_url = ParameterManager.TWOFA_URL

    kite = None

    @classmethod
    def get_kite_conn(cls, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        cls._setup_conn(test_conn=test_conn)
        return cls.kite

    @classmethod
    def get_access_tokens(cls, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        if cls._access_tokens is None:
            cls._setup_conn(test_conn=test_conn)
        return cls._access_tokens

    @classmethod
    def _setup_conn(cls, test_conn=False):
        """Authenticates with Zerodha, retrieves access token."""
        with cls._lock:
            if not test_conn and cls.kite:
                return

            stored_token = get_stored_access_tokens(DbConnect)
            if stored_token:
                cls._access_tokens = stored_token
                cls.kite = KiteConnect(api_key=cls.api_key)
                cls.kite.set_access_token(cls._access_tokens)
                try:
                    cls.kite.profile()
                    logger.info("Stored access token is fetched and successfully validated")
                    return
                except Exception:
                    logger.warning("Stored access token is invalid. Re-authenticating...")

            cls._authenticate()

    @classmethod
    def _authenticate(cls):
        """Handles login, TOTP authentication, and token generation."""
        session = requests.Session()

        # Step 1: Perform initial login
        try:
            response = session.post(cls.login_url, data={"user_id": cls.username, "password": cls._password})
            response.raise_for_status()
            request_id = response.json()["data"]["request_id"]
            logger.info(f"Login successful, Request ID: {request_id}")
        except Exception as e:
            logger.error(f"Failed to log in: {e}")
            raise

        # Step 2: Perform TOTP authentication
        for attempt in range(sc.MAX_TOTP_CONN_RETRY_COUNT):
            try:
                totp_pin = generate_totp()
                response = session.post(cls.twofa_url, data={"user_id": cls.username, "request_id": request_id,
                                                             "twofa_value": totp_pin, "twofa_type": "totp"}, )
                response.raise_for_status()
                logger.info("TOTP authentication successful.")
                break
            except Exception as e:
                logger.warning(f"TOTP attempt {attempt + 1} of {sc.MAX_TOTP_CONN_RETRY_COUNT} failed: {e}...")
                if attempt == sc.MAX_TOTP_CONN_RETRY_COUNT - 1:
                    logger.error("TOTP authentication failed after multiple attempts.")
                    raise

        # Step 3: Fetch request token manually
        # Request Kite login URL
        try:
            kite = KiteConnect(api_key=cls.api_key)
            kite_url = kite.login_url()
            logger.info("Kite login URL received.")
            session.get(kite_url)
            request_token = ""
        except Exception as e:
            # Extract request token from URL exception
            try:
                request_token = str(e).split("request_token=")[1].split("&")[0].split()[0]
                logger.info(f"Request Token received: {request_token}")
            except Exception:
                notes = "Failed to extract request token."
                logger.error(notes)
                raise

        # Step 4: Generate access token
        try:
            kite = KiteConnect(api_key=cls.api_key)
            session_data = kite.generate_session(request_token, api_secret=cls._api_secret)
            cls._access_tokens = session_data["access_tokens"]
            cls.kite = kite
            cls.kite.set_access_tokens(cls._access_tokens)

            # Store the new access token
            cls._db_token.check_update_access_tokens(cls._access_tokens, DbConnect)
            logger.info("Access token successfully generated and stored.")
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            raise


# Initialize singleton instance
ZerodhaKite.get_kite_conn(test_conn=True)

if __name__ == "__main__":
    logger.info(f"Kite connection initialized: {ZerodhaKite.kite}")
