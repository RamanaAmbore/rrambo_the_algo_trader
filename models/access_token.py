from datetime import timedelta

from sqlalchemy import Column, String, DateTime, Integer, text

from utils.config_loader import Env
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)


# Define AccessToken model
class AccessToken(Base):
    __tablename__ = "access_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))

    @staticmethod
    def get_stored_access_token(db_connection):
        """Fetch stored access token and check validity."""
        with db_connection.sync_session() as session:
            token_entry = session.query(AccessToken).first()
            if token_entry:
                age = timestamp_indian() - token_entry.timestamp
                if age < timedelta(hours=Env.ACCESS_TOKEN_VALIDITY):
                    logger.info('Using access token from database')
                    return token_entry.token
        return None  # Token is expired or missing

    @staticmethod
    def check_update_access_token(new_token: str, db_connection):
        """Save or update access token in the database."""
        with db_connection.sync_session() as session:
            token_entry = session.query(AccessToken).first()
            if token_entry:
                if token_entry.token != new_token:
                    token_entry.token = new_token
                    token_entry.timestamp = timestamp_indian()
                    logger.info("Access Token updated in database")
            else:
                session.add(AccessToken(token=new_token, timestamp=timestamp_indian()))
                logger.info("Access Token added to database")
            session.commit()
