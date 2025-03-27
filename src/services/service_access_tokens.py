from datetime import timedelta
from typing import Any

from sqlalchemy import select

from src.core.database_manager import DatabaseManager as Db
from src.helpers.cipher_utils import encrypt_text, decrypt_text
from src.helpers.date_time_utils import timestamp_indian
from src.models import AccessTokens
from src.models.access_tokens import AccessTokens, logger
from src.services.service_base import ServiceBase  # Assuming BaseService exists
from src.settings.constants_manager import DEFAULT_ACCESS_TOKENS
from src.settings.parameter_manager import parms


class ServiceAccessToken(ServiceBase):
    """Service class for handling AccessTokens database operations."""

    model = AccessTokens  # Assign model at the class level

    def __init__(self):
        """Initialize the service with the AccessTokens model."""
        super().__init__(self.model)

    def get_stored_access_token(self, account: str) -> tuple[Any, Any] | None:
        """
        Retrieve stored access token for a given account.
        """
        try:
            with Db.get_sync_session() as session:
                token_entry = session.query(self.model).filter_by(account=account).first()

                if token_entry:
                    age = timestamp_indian() - token_entry.timestamp
                    if age < timedelta(hours=parms.ACCESS_TOKEN_VALIDITY):
                        logger.info('Using access token from database')
                        return decrypt_text(token_entry.token), token_entry.id
                    logger.info(f'Stored token has expired for {account}')
        except Exception as e:
            logger.error(f"Error retrieving access token: {e}")
            raise

        return None, None

    def check_update_access_token(self, new_token: str, account: str) -> None:
        """
        Save or update access token in the database.
        """
        try:
            with Db.get_sync_session() as session:
                token_entry = session.query(self.model).filter_by(account=account).first()
                encrypted_token = encrypt_text(new_token)

                if token_entry:
                    if token_entry.token != encrypted_token:
                        token_entry.token = encrypted_token
                        token_entry.timestamp = timestamp_indian()
                        session.commit()
                        logger.info(f"Access Token updated in database for {account}")
                else:
                    new_entry = self.model(account=account, token=encrypted_token, timestamp=timestamp_indian())
                    session.add(new_entry)
                    session.commit()
                    logger.info("Access Token added to database")
        except Exception as e:
            logger.error(f"Error updating access token: {e}")
            raise


# Create a Singleton Instance
service_access_token = ServiceAccessToken()


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AccessTokens.__table__
        for record in DEFAULT_ACCESS_TOKENS:
            exists = connection.execute(select(table.c.account).where(
                table.c.account == record['account'])).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Access Token records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default access tokens: {e}")
        raise
