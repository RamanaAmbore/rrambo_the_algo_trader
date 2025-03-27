import threading

import requests
from kiteconnect import KiteConnect

from src.core.decorators import retry_kite_conn
from src.helpers.logger import get_logger
from src.helpers.utils import generate_totp
from src.services.service_access_tokens import service_access_token
from src.settings.parameter_manager import parms, ACCOUNT_CREDENTIALS

logger = get_logger(__name__)


class ZerodhaKiteConnect:
    """Handles Kite API authentication and access token management."""

    _lock = threading.Lock()
    _access_token = None
    account = parms.DEFAULT_ACCOUNT
    _password = ACCOUNT_CREDENTIALS[account]['PASSWORD']
    api_key = ACCOUNT_CREDENTIALS[account]["API_KEY"]
    _api_secret = ACCOUNT_CREDENTIALS[account]["API_SECRET"]
    totp_token = ACCOUNT_CREDENTIALS[account]['TOTP_TOKEN']
    login_url = parms.LOGIN_URL
    twofa_url = parms.TWOFA_URL
    id = None

    kite = None

    @classmethod
    def get_kite_conn(cls, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        cls._setup_conn(test_conn=test_conn)
        return cls.kite

    @classmethod
    def get_access_token(cls, test_conn=False):
        """Returns access tokens, initializing them if necessary."""
        if cls._access_token is None:
            cls._setup_conn(test_conn=test_conn)
        return cls._access_token

    @classmethod
    def _setup_conn(cls, test_conn=False):
        """Authenticates with Zerodha, retrieves access token."""
        with cls._lock:
            if not test_conn and cls.kite:
                return

            stored_token, cls.id = service_access_token.get_stored_access_token(cls.account)
            if stored_token:
                cls._access_token = stored_token
                cls.kite = KiteConnect(api_key=cls.api_key)
                cls.kite.set_access_token(cls._access_token)
                try:
                    cls.kite.profile()
                    logger.info("Stored access token is fetched and successfully validated")
                    return
                except Exception:
                    logger.warning("Stored access token is invalid. Re-authenticating...")

            cls._authenticate()

    @classmethod
    def _authenticate(cls):
        """Handles login process and calls authentication steps."""
        session = requests.Session()

        # Step 1: Perform initial login
        try:
            response = session.post(cls.login_url, data={"user_id": cls.account, "password": cls._password})
            response.raise_for_status()
            request_id = response.json()["data"]["request_id"]
            logger.info(f"Login successful, Request ID: {request_id}")
        except Exception as e:
            logger.error(f"Failed to log in: {e}")
            raise

        # Step 2: Perform TOTP authentication with retry logic
        cls._authenticate_totp(session, request_id)

        # Step 3: Generate access token with retry logic
        cls._generate_access_token(session)

    @classmethod
    @retry_kite_conn(parms.MAX_TOTP_CONN_RETRY_COUNT)
    def _authenticate_totp(cls, session, request_id):
        """
        Authenticates using TOTP.

        :param session: Requests session object.
        :param request_id: Login request ID.
        """
        totp_pin = generate_totp(cls.totp_token)
        response = session.post(cls.twofa_url, data={"user_id": cls.account, "request_id": request_id,
                                                     "twofa_value": totp_pin, "twofa_type": "totp"})
        response.raise_for_status()
        logger.info("TOTP authentication successful.")


    @classmethod
    @retry_kite_conn(parms.MAX_TOTP_CONN_RETRY_COUNT)
    def _generate_access_token(cls, session):
        """
        Generates access token after successful authentication.

        :param session: Requests session object.
        """
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
                logger.error("Failed to extract request token.")
                raise

        try:
            kite = KiteConnect(api_key=cls.api_key)
            session_data = kite.generate_session(request_token, api_secret=cls._api_secret)
            cls._access_token = session_data["access_token"]
            cls.kite = kite
            cls.kite.set_access_token(cls._access_token)

            # Store the new access token
            service_access_token.check_update_access_token(cls._access_token, cls.account)
            logger.info("Access token successfully generated and stored.")
        except Exception as e:
            logger.error(f"Failed to generate access token for account {cls.account}: {e}")
            raise


# Initialize singleton instance
ZerodhaKiteConnect.get_kite_conn(test_conn=True)

if __name__ == "__main__":
    logger.info(f"Kite connection initialized: {ZerodhaKiteConnect.kite}")