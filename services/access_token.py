from datetime import timedelta

from models import AccessToken
from models.access_token import logger
from utils.date_time_utils import timestamp_indian
from utils.db_connection import DbConnection as Db
from utils.settings_loader import Env


def get_stored_access_token(db_connection, account_id):
    """
    Retrieves the stored access token for a given account_id.

    It checks if the token is still valid based on `Env.ACCESS_TOKEN_VALIDITY`.
    If valid, it returns the token; otherwise, it returns None.

    :param db_connection: Database connection instance
    :param account_id: Account ID for which the token is being fetched
    :return: Valid access token (str) or None if expired/missing
    """
    with db_connection.sync_session() as session:
        token_entry = session.query(AccessToken).filter_by(account_id=account_id).first()

        if token_entry:
            age = timestamp_indian() - token_entry.timestamp
            if age < timedelta(hours=Env.ACCESS_TOKEN_VALIDITY):
                logger.info('Using access token from database')
                return token_entry.token

    return None  # Token is expired or missing


def check_update_access_token(new_token: str, account_id):
    """
    Saves or updates the access token in the database for the given account_id.

    If a token exists and is different from the new token, it updates the record.
    If no token exists, it inserts a new record.

    :param new_token: The new access token to be stored
    :param db_connection: Database connection instance
    :param account_id: Account ID for which the token is being updated
    """
    with Db.get_sync_session() as session:
        token_entry = session.query(AccessToken).filter_by(account_id=account_id).first()

        if token_entry:
            if token_entry.token != new_token:  # Update token only if changed
                token_entry.token = new_token
                token_entry.timestamp = timestamp_indian()
                logger.info("Access Token updated in database")
        else:
            session.add(AccessToken(account_id=account_id, token=new_token, timestamp=timestamp_indian()))
            logger.info("Access Token added to database")

        session.commit()
