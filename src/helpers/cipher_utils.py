import os
import secrets
import string

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

f = Fernet(os.getenv('ENCRYPTION_KEY'))


def generate_api_key_pair():
    """Generate a new API key and secret pair."""
    # Generate a random API key (typically alphanumeric)
    api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))

    # Generate a more complex secret
    api_secret = secrets.token_urlsafe(32)

    return api_key, api_secret


def encrypt_text(text):
    """Encrypt text using Fernet."""
    if not text: return None
    text = text.strip()
    return f.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    """Decrypt text using Fernet."""
    if not encrypted_text: return None
    return f.decrypt(encrypted_text.encode()).decode()
