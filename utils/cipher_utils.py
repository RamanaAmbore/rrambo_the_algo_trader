from cryptography.fernet import Fernet
import base64
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def generate_cipher_key():
    """Generate a new Fernet key."""
    return Fernet.generate_key()

def encrypt_text(text, key):
    """Encrypt text using Fernet."""
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, key):
    """Decrypt text using Fernet."""
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()