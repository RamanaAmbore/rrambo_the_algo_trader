from datetime import timedelta
from typing import Any

from src.core.decorators import singleton_init_guard
from src.core.singleton_base import SingletonBase
from src.helpers.cipher_utils import encrypt_text, decrypt_text
from src.helpers.database_manager import db
from src.helpers.date_time_utils import timestamp_indian
from src.models.access_tokens import AccessTokens, logger
from src.services.service_base import ServiceBase  # Assuming BaseService exists
from src.settings.parameter_manager import parms


class ServiceAccessTokens(SingletonBase, ServiceBase):
    """Service class for handling AccessTokens database operations."""

    model = AccessTokens  # Assign model at the class level

    conflict_cols = ['account']

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)

    def get_stored_access_token(self, account: str) -> tuple[Any, Any] | None:
        """
        Retrieve stored access token for a given account.
        """
        try:
            with db.get_sync_session() as session:
                token_entry = session.query(self.model).filter_by(account=account).first()

                if token_entry and token_entry.token is not None:
                    age = timestamp_indian() - token_entry.timestamp
                    if age < timedelta(hours=parms.ACCESS_TOKEN_VALIDITY):
                        logger.info('Using access token from database')
                        return decrypt_text(token_entry.token)
                    logger.info(f'Stored token has expired for {account}')
        except Exception as e:
            logger.error(f"Error retrieving access token: {e}")
            raise

        return None

    def check_update_access_token(self, new_token: str, account: str) -> None:
        """
        Save or update access token in the database.
        """
        try:
            with db.get_sync_session() as session:
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
service_access_tokens = ServiceAccessTokens()
