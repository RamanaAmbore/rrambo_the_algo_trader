from datetime import timedelta
from typing import Optional

from models import AccessTokens
from models.access_tokens import logger
from utils.date_time_utils import timestamp_indian
from utils.db_connect import DbConnect as Db
from utils.parms import Parms
from cryptography.fernet import Fernet, InvalidToken




def encrypt_token(token: str) -> str:
    """Encrypt access token."""
    try:
        return cipher_suite.encrypt(token.encode()).decode()
    except Exception as e:
        logger.error(f"Error encrypting token: {e}")
        raise


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt access token."""
    try:
        return cipher_suite.decrypt(encrypted_token.encode()).decode()
    except InvalidToken:
        logger.error("Invalid token format")
        raise
    except Exception as e:
        logger.error(f"Error decrypting token: {e}")
        raise


def get_stored_access_tokens(db_connection: Db, account: str) -> Optional[str]:
    """
    Retrieve stored access token for a given account.

    Args:
        db_connection: Database connection instance
        account: Account ID for which the token is being fetched

    Returns:
        str: Valid access token or None if expired/missing
    """
    try:
        with db_connection.sync_session() as session:
            token_entry = session.query(AccessTokens).filter_by(account=account).first()

            if token_entry:
                age = timestamp_indian() - token_entry.timestamp
                if age < timedelta(hours=Parms.ACCESS_TOKEN_VALIDITY):
                    logger.info('Using access token from database')
                    return decrypt_token(token_entry.token)
                logger.info('Stored token has expired')
    except Exception as e:
        logger.error(f"Error retrieving access token: {e}")
        raise

    return None


def check_update_access_tokens(new_token: str, account: str) -> None:
    """
    Save or update access token in database.

    Args:
        new_token: New access token to be stored
        account: Account ID for which the token is being updated
    """
    try:
        with Db.get_sync_session() as session:
            token_entry = session.query(AccessTokens).filter_by(account=account).first()
            encrypted_token = encrypt_token(new_token)

            if token_entry:
                if token_entry.token != encrypted_token:
                    token_entry.token = encrypted_token
                    token_entry.timestamp = timestamp_indian()
                    session.commit()
                    logger.info("Access Token updated in database")
            else:
                new_entry = AccessTokens(account=account, token=encrypted_token, timestamp=timestamp_indian())
                session.add(new_entry)
                session.commit()
                logger.info("Access Token added to database")
    except Exception as e:
        logger.error(f"Error updating access token: {e}")
        raise
