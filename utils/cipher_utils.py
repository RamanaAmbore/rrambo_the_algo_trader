import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

f = Fernet(os.getenv('ENCRYPTION_KEY'))


def encrypt_text(text):
    """Encrypt text using Fernet."""
    return f.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    """Decrypt text using Fernet."""

    return f.decrypt(encrypted_text.encode()).decode()
