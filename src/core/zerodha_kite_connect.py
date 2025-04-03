import threading

import requests
from kiteconnect import KiteConnect

from src.core.decorators import retry_kite_conn
from src.helpers.logger import get_logger
from src.helpers.utils import generate_totp
from src.services.service_access_tokens import service_access_tokens
from src.settings.parameter_manager import parms, ACCOUNT_CREDENTIALS

logger = get_logger(__name__)


class ZerodhaKiteConnect:
    """Singleton class to handle Kite API authentication and access token management."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ZerodhaKiteConnect, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.account = parms.DEF_ACCOUNT
        self._password = ACCOUNT_CREDENTIALS[self.account]['PASSWORD']
        self.api_key = ACCOUNT_CREDENTIALS[self.account]["API_KEY"]
        self._api_secret = ACCOUNT_CREDENTIALS[self.account]["API_SECRET"]
        self.totp_token = ACCOUNT_CREDENTIALS[self.account]['TOTP_TOKEN']
        self.login_url = parms.LOGIN_URL
        self.twofa_url = parms.TWOFA_URL
        self._access_token = None
        self.id = None
        self.kite = None

    def get_kite_conn(self, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        self._setup_conn(test_conn=test_conn)
        return self.kite

    def get_access_token(self, test_conn=False):
        """Returns access tokens, initializing them if necessary."""
        if self._access_token is None:
            self._setup_conn(test_conn=test_conn)
        return self._access_token

    def _setup_conn(self, test_conn=False):
        """Authenticates with Zerodha, retrieves access token."""
        with self._lock:
            if not test_conn and self.kite:
                return

            stored_token, self.id = service_access_tokens.get_stored_access_token(self.account)
            if stored_token:
                self._access_token = stored_token
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self._access_token)
                try:
                    self.kite.profile()
                    logger.info("Stored access token is fetched and successfully validated")
                    return
                except Exception:
                    logger.warning("Stored access token is invalid. Re-authenticating...")

            self._authenticate()

    def _authenticate(self):
        """Handles login process and calls authentication steps."""
        session = requests.Session()

        try:
            response = session.post(self.login_url, data={"user_id": self.account, "password": self._password})
            response.raise_for_status()
            request_id = response.json()["data"]["request_id"]
            logger.info(f"Login successful, Request ID: {request_id}")
        except Exception as e:
            logger.error(f"Failed to log in: {e}")
            raise

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
            service_access_tokens.check_update_access_tokens(cls._access_token, cls.account)
            logger.info("Access token successfully generated and stored.")
        except Exception as e:
            logger.error(f"Failed to generate access token for account {cls.account}: {e}")
            raise


if __name__ == "__main__":
    logger.info(f"Kite connection initialized: {ZerodhaKiteConnect.kite}")
