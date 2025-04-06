import threading

import requests
from kiteconnect import KiteConnect

from src.core.decorators import retry_kite_conn
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.helpers.utils import generate_totp
from src.services.service_access_tokens import service_access_tokens
from src.settings.parameter_manager import parms, ACCOUNT_CREDENTIALS

logger = get_logger(__name__)


class ZerodhaKiteConnect(SingletonBase):
    """Singleton class to handle Kite API authentication and access token management."""

    def __init__(self):
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        self.account = parms.DEF_ACCOUNT
        credentials = ACCOUNT_CREDENTIALS[self.account]

        self._password = credentials['PASSWORD']
        self.api_key = credentials["API_KEY"]
        self._api_secret = credentials["API_SECRET"]
        self.totp_token = credentials['TOTP_TOKEN']

        self.login_url = parms.LOGIN_URL
        self.twofa_url = parms.TWOFA_URL

        self._access_token = None
        self.kite = None

        self._initialized = True

        self.init_kite_conn()

    def init_kite_conn(self, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        with ZerodhaKiteConnect._lock:
            if not test_conn and self.kite:
                return

            stored_token = service_access_tokens.get_stored_access_token(self.account)
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

            request_id, session = self.login()

            self.totp_authenticate(request_id, session)

            try:
                self.kite = KiteConnect(api_key=self.api_key)
                kite_url = self.kite.login_url()
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

            self.setup_access_token(request_token)

    def get_kite_conn(self,test_conn=True):
        self.init_kite_conn(test_conn=test_conn)
        return self.kite

    @retry_kite_conn(parms.MAX_KITE_CONN_RETRY_COUNT)
    def login(self):
        session = requests.Session()
        try:
            response = session.post(self.login_url, data={"user_id": self.account, "password": self._password})
            response.raise_for_status()
            request_id = response.json()["data"]["request_id"]
            logger.info(f"Login successful, Request ID: {request_id}")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
        return request_id, session

    @retry_kite_conn(parms.MAX_KITE_CONN_RETRY_COUNT)
    def totp_authenticate(self, request_id, session):
        try:
            totp = generate_totp(self.totp_token)
            response = session.post(self.twofa_url,
                                    data={"user_id": self.account, "request_id": request_id, "twofa_value": totp})
            response.raise_for_status()
            logger.info("2FA authentication successful")
        except Exception as e:
            logger.error(f"2FA authentication failed: {e}")
            raise

    @retry_kite_conn(parms.MAX_KITE_CONN_RETRY_COUNT)
    def setup_access_token(self, request_token):
        try:
            self.kite = KiteConnect(api_key=self.api_key)
            session_data = self.kite.generate_session(request_token, api_secret=self._api_secret)
            self._access_token = session_data["access_token"]
            self.kite.set_access_token(self._access_token)

            # Store the new access token
            service_access_tokens.check_update_access_token(self._access_token, self.account)
            logger.info("Access token successfully generated and stored.")
        except Exception as e:
            logger.error(f"Failed to generate access token for account {self.account}: {e}")
            raise
    def get_access_token(self):
        return self._access_token