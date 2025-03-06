from datetime import timedelta
from sqlalchemy import Column, String, DateTime, text, Boolean, Integer
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from utils.settings_loader import Env
from .base import Base

logger = get_logger(__name__)

class AccessToken(Base):
    """
    Stores access tokens for API authentication.

    This table keeps track of access tokens associated with different accounts.
    It ensures that tokens are stored securely and can be retrieved or updated when needed.
    """

    __tablename__ = "access_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)  # Unique account identifier
    token = Column(String, nullable=False)  # Access token for authentication
    source = Column(String, nullable=True, default="API")  # Indicates source of the token (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Token creation timestamp
    warning_error = Column(Boolean, default=False)  # Flag for warnings or errors
    msg = Column(String, nullable=True)  # Additional message field for logging

    @staticmethod
    def get_stored_access_token(db_connection, account_id=Env.ZERODHA_USERNAME):
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

    @staticmethod
    def check_update_access_token(new_token: str, db_connection, account_id=Env.ZERODHA_USERNAME):
        """
        Saves or updates the access token in the database for the given account_id.

        If a token exists and is different from the new token, it updates the record.
        If no token exists, it inserts a new record.

        :param new_token: The new access token to be stored
        :param db_connection: Database connection instance
        :param account_id: Account ID for which the token is being updated
        """
        with db_connection.sync_session() as session:
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

