from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv
from auth.login import zerodha_login
from utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

class ZerodhaSession:
    def __init__(self):
        """Initialize KiteConnect session."""
        api_key = os.getenv("ZERODHA_API_KEY")
        api_secret = os.getenv("ZERODHA_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("API key or secret is missing in .env")

        self.kite = KiteConnect(api_key=api_key)

    def generate_access_token(self):
        """Generates and sets access token for Zerodha API."""
        request_token = zerodha_login()
        api_secret = os.getenv("ZERODHA_API_SECRET")

        logger.info("Generating access token...")
        data = self.kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        # Set session token
        self.kite.set_access_token(access_token)
        logger.info("Access token generated and set successfully.")

        return access_token

    def get_kite_client(self):
        """Returns an authenticated KiteConnect client instance."""
        return self.kite

if __name__ == "__main__":
    session = ZerodhaSession()
    access_token = session.generate_access_token()
    print("Access Token:", access_token)
