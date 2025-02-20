import pyotp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_totp():
    """Generate a TOTP (Time-Based One-Time Password) using PyOTP."""
    totp_secret = os.getenv("ZERODHA_TOTP_SECRET")
    if not totp_secret:
        raise ValueError("TOTP secret is not set in .env")

    totp = pyotp.TOTP(totp_secret)
    return totp.now()


if __name__ == "__main__":
    print("Current TOTP:", generate_totp())
