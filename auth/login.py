import json
import os
from datetime import datetime, timedelta

import pyotp
import requests
from dotenv import load_dotenv
from kiteconnect import KiteConnect

from utils.config_loader import sc
from utils.db_utils import get_stored_access_token, check_update_access_token
from utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


def zerodha_login():
    """Logs into Zerodha Kite and fetches the access token, storing it in the database."""

    # Load credentials from environment
    USERNAME = os.getenv("ZERODHA_USERNAME")
    PASSWORD = os.getenv("ZERODHA_PASSWORD")
    LOGIN_URL = os.getenv("LOGIN_URL")
    TWOFA_URL = os.getenv("TWOFA_URL")
    TOTP_TOKEN = os.getenv("TOTP_TOKEN")
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("API_SECRET")

    # Check if access token exists and is still valid
    stored_token= get_stored_access_token()

    if stored_token:
        try:
            kite = KiteConnect(api_key=API_KEY)
            kite.set_access_token(stored_token)
            logger.info("Using stored access token.")
            return kite, stored_token
        except Exception as e:
            logger.error(f"Stored access token is invalid: {e}")

    # Proceed with login if no valid token is found
    try:
        session = requests.Session()
        response = session.post(LOGIN_URL, data={'user_id': USERNAME, 'password': PASSWORD})
        request_id = json.loads(response.text)['data']['request_id']
        logger.info(f'Successfully processed credentials, request ID: {request_id}')
    except Exception as e:
        logger.error(f"Login request failed: {e}")
        return None, None

    # Two-factor authentication (TOTP)
    retry = 1
    while True:
        retry += 1
        no_error = True
        try:
            twofa_pin = pyotp.TOTP(TOTP_TOKEN).now()
            session.post(TWOFA_URL, data={'user_id': USERNAME, 'request_id': request_id, 'twofa_value': twofa_pin,
                                          'twofa_type': 'totp'})
            logger.info(f'Successfully processed TOTP - {twofa_pin}')
        except Exception as e:
            logger.error(f"TOTP authentication failed: {e}")
            no_error = False
        if retry > sc.totp_retry_count or no_error:
            break
        logger.error(f"Retrying TOTP authentication...")

    if not no_error:
        logger.error(f"TOTP authentication failed after {c.totp_retry_count} tries")
        return None, None

    # Get request token from Kite URL
    kite = KiteConnect(api_key=API_KEY)
    kite_url = kite.login_url()
    logger.info(f'Successfully received Kite URL: {kite_url}')

    try:
        session.get(kite_url)
    except Exception as e:
        e_msg = str(e)
        request_token = e_msg.split('request_token=')[1].split(' ')[0].split('&action')[0]
        logger.info(f'Successful Login with Request Token: {request_token}')

        # Generate Access Token
        try:
            access_token = kite.generate_session(request_token, API_SECRET)['access_token']
            logger.info(f'Successfully received Access Token')
            kite.set_access_token(access_token)

            # Store access token in the database
            check_update_access_token(access_token)
            return kite, access_token
        except Exception as e:
            logger.error(f"Failed to generate access token: {e}")
            return None, None


if __name__ == "__main__":
    zerodha_login()
    logger.info("Login process complete, Kite URL with Access Token received.")