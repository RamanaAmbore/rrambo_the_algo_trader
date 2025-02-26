import os
import threading
import pyotp
import requests
from dotenv import load_dotenv
from kiteconnect import KiteConnect
from models.access_token import AccessToken
from utils.config_loader import sc
from utils.logger import get_logger

# Load environment variables
load_dotenv()
logger = get_logger(__name__)


class ZerodhaKite:
    """Handles Kite API authentication and access token management."""

    _lock = threading.Lock()
    _access_token = None
    _db_token = AccessToken()

    api_key = os.getenv("API_KEY")
    _api_secret = os.getenv("API_SECRET")
    username = os.getenv("ZERODHA_USERNAME")
    _password = os.getenv("ZERODHA_PASSWORD")
    login_url = os.getenv("LOGIN_URL")
    twofa_url = os.getenv("TWOFA_URL")
    totp_token = os.getenv("TOTP_TOKEN")

    kite = None

    @classmethod
    def get_kite_conn(cls, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        cls._setup_conn(test_conn=test_conn)
        return cls.kite

    @classmethod
    def _setup_conn(cls, test_conn=False):
        """Authenticates with Zerodha, retrieves access token."""
        with cls._lock:
            if not test_conn and cls.kite:
                return c

            stored_token = cls._db_token.get_stored_access_token()
            if stored_token:
                cls._access_token = stored_token
                cls.kite = KiteConnect(api_key=cls.api_key)
                cls.kite.set_access_token(cls._access_token)
                try:
                    cls.kite.profile()
                    return
                except Exception:
                    logger.error("Stored access token is invalid. Re-authenticating...")

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
        for attempt in range(sc.totp_retry_count):
            try:
                totp_pin = pyotp.TOTP(cls.totp_token).now()
                response = session.post(
                    cls.twofa_url,
                    data={"user_id": cls.username, "request_id": request_id, "twofa_value": totp_pin,
                          "twofa_type": "totp"},
                )
                response.raise_for_status()
                logger.info("TOTP authentication successful.")
                break
            except Exception as e:
                logger.warning(f"TOTP attempt {attempt + 1} of {sc.totp_retry_count} failed: {e}")
                if attempt == sc.totp_retry_count - 1:
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
                msg = "Failed to extract request token."
                logger.error(msg)
                raise

        # Step 4: Generate access token
        try:
            kite = KiteConnect(api_key=cls.api_key)
            session_data = kite.generate_session(request_token, api_secret=cls._api_secret)
            cls._access_token = session_data["access_token"]
            cls.kite = kite
            cls.kite.set_access_token(cls._access_token)

            # Store the new access token
            cls._db_token.check_update_access_token(cls._access_token)
            logger.info("Access token successfully generated and stored.")
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            raise
