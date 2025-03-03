import pyotp

from utils.config_loader import Env


def generate_totp():
    """Generate a valid TOTP using the secret key."""
    return pyotp.TOTP(Env.TOTP_TOKEN).now()
