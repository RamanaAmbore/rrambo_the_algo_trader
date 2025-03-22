from datetime import timedelta
from typing import Optional

from src.core.database_manager import DatabaseManager as Db
from src.helpers.cipher_utils import encrypt_text, decrypt_text
from src.helpers.date_time_utils import timestamp_indian
from src.models import AccessTokens
from src.models.access_tokens import logger
from src.settings.parameter_manager import parms


def get_stored_access_tokens(account: str) -> Optional[str]:
    """
    Retrieve stored access token for a given account.

    Args:
        account: Account ID for which the token is being fetched

    Returns:
        str: Valid access token or None if expired/missing
    """
    try:
        with Db.get_sync_session() as session:
            token_entry = session.query(AccessTokens).filter_by(account=account).first()

            if token_entry:
                age = timestamp_indian() - token_entry.timestamp
                if age < timedelta(hours=parms.ACCESS_TOKEN_VALIDITY):
                    logger.info('Using access token from database')
                    return decrypt_text(token_entry.token)
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
            encrypted_token = encrypt_text(new_token)

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
