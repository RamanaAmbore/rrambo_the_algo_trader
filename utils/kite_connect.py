import os
import threading
import pyotp
import requests
from dotenv import load_dotenv
from kiteconnect import KiteConnect, KiteTicker
from kiteconnect.exceptions import TokenException
from models.access_token import AccessToken
from utils.config_loader import sc
from utils.logger import get_logger
from utils.market_ticker import MarketTicker

# Load environment variables
load_dotenv()
logger = get_logger(__name__)


class ZerodhaKite:
    """Handles Kite API authentication, access token management, and WebSocket connection."""

    _lock = threading.Lock()
    _ticker_lock = threading.Lock()
    _access_token = None
    _db_token = AccessToken()

    api_key = os.getenv("API_KEY")
    _api_secret = os.getenv("API_SECRET")  # Fixed incorrect variable name
    username = os.getenv("ZERODHA_USERNAME")
    _password = os.getenv("ZERODHA_PASSWORD")
    login_url = os.getenv("LOGIN_URL")
    twofa_url = os.getenv("TWOFA_URL")
    totp_token = os.getenv("TOTP_TOKEN")

    kite = None
    socket_conn = None
    instrument_tokens = set()
    market_monitor = None

    @classmethod
    def get_kite_connection(cls, test_conn=False):
        """Returns KiteConnect instance, initializing it if necessary."""
        cls._setup_conn(test_conn=test_conn)
        cls._set_market_monitor()
        return cls.kite

    @classmethod
    def get_access_key(cls):
        """Returns WebSocket connection for live market data."""
        return cls._access_token

    @classmethod
    def _setup_conn(cls, test_conn=False):
        """Authenticates with Zerodha, retrieves access token, and sets up WebSocket."""
        with cls._lock:
            if not test_conn and cls.kite:
                return  # Already initialized

            stored_token = cls._db_token.get_stored_access_token()
            if stored_token:
                logger.info("Using stored access token from database.")
                cls._access_token = stored_token
                cls.kite = KiteConnect(api_key=cls.api_key)
                cls.kite.set_access_token(cls._access_token)

                # Validate stored token
                try:
                    cls.kite.profile()  # If this fails, the token is invalid
                    logger.info("Stored access token is valid.")
                    cls._setup_socket_conn()
                    return
                except TokenException:
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

        cls._setup_socket_conn()

    @classmethod
    def _set_market_monitor(cls):

        # Start the market monitor thread once
        if cls.market_monitor is None:
            cls.market_monitor = MarketTicker(cls)
            cls.market_monitor.daemon = True  # Stops with main program
            cls.market_monitor.start()

    @classmethod
    def _setup_socket_conn(cls):
        """Initializes WebSocket connection for real-time market data."""
        with cls._ticker_lock:
            if cls.socket_conn:
                logger.info("Closing existing WebSocket connection...")
                cls.socket_conn.close()

            logger.info("Starting new WebSocket connection...")
            cls.socket_conn = KiteTicker(cls.api_key, cls._access_token)
            cls.socket_conn.on_ticks = cls.on_ticks
            cls.socket_conn.on_connect = cls.on_connect
            cls.socket_conn.on_close = cls.on_close
            cls.socket_conn.connect(threaded=True)

    @classmethod
    def on_connect(cls, ws, response):
        """Subscribes to instrument tokens when WebSocket connects."""
        with cls._ticker_lock:
            if cls.instrument_tokens:
                ws.subscribe(list(cls.instrument_tokens))
                ws.set_mode(ws.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to tokens: {cls.instrument_tokens}")

    @classmethod
    def on_ticks(cls, ws, ticks):
        """Handles incoming market data."""
        logger.info(f"Received tick data: {ticks}")

    @classmethod
    def on_close(cls, ws, code, reason):
        """Handle Websocket connection closure and attempt to reconnect."""
        logger.warning(f"WebSocket connection closed: {reason}. Reconnecting...")

        # Check if the error message suggests an invalid access token
        if "TokenException" in str(reason) or "Invalid access token" in str(reason):
            logger.error("Access token may be invalid. Re-authenticating...")

            # Re-authenticate and get a fresh access token
            cls.get_kite_connection()

        # Reconnect WebSocket
        cls.get_socket_conn()

    @classmethod
    def add_instruments(cls, tokens):
        """Adds instrument tokens to subscribe to."""
        with cls._ticker_lock:
            cls.instrument_tokens.update(tokens)
            if cls.socket_conn:
                cls.socket_conn.subscribe(list(cls.instrument_tokens))
                cls.socket_conn.set_mode(cls.socket_conn.MODE_FULL, list(cls.instrument_tokens))
                logger.info(f"Subscribed to new tokens: {cls.instrument_tokens}")

    @classmethod
    def remove_instruments(cls, tokens):
        """Removes instrument tokens from subscription."""
        with cls._ticker_lock:
            cls.instrument_tokens.difference_update(tokens)
            if cls.socket_conn:
                cls.socket_conn.unsubscribe(list(tokens))
                logger.info(f"Unsubscribed from tokens: {tokens}")


# Initialize singleton instance
ZerodhaKite.get_kite_connection(test_conn=True)

if __name__ == "__main__":
    logger.info(f"Kite connection initialized: {ZerodhaKite.kite}")

    # Example usage:
    ZerodhaKite.add_instruments([738561, 5633])  # Add tokens
    ZerodhaKite.remove_instruments([5633])  # Remove tokens

