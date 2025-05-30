import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

f = Fernet(os.getenv('ENCRYPTION_KEY'))


def encrypt_text(text):
    """Encrypt text using Fernet."""
    if not text: return None
    text = text.strip()
    return f.encrypt(text.encode()).decode()


def decrypt_text(encrypted_text):
    """Decrypt text using Fernet."""
    if not encrypted_text: return None
    return f.decrypt(encrypted_text.encode()).decode()
