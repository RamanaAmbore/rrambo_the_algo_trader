from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, DateTime, Integer

from utils.config_loader import sc
from utils.db_conn import DbConnection, ACCESS_TOKEN_VALIDITY
from utils.logger import get_logger
from .base import Base

logger = get_logger(__name__)

SessionLocal = DbConnection.sync_session


# Define AccessToken model
class AccessToken(Base):
    __tablename__ = "access_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
    creation_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=ZoneInfo(sc.indian_timezone)))

    @staticmethod
    def get_stored_access_token():
        """Fetch stored access token and check validity."""
        with SessionLocal() as session:
            token_entry = session.query(AccessToken).first()
            if token_entry:
                age = datetime.now(tz=ZoneInfo(sc.indian_timezone)) - token_entry.creation_ts
                if age < timedelta(hours=int(ACCESS_TOKEN_VALIDITY)):
                    return token_entry.token
        return None  # Token is expired or missing

    @staticmethod
    def check_update_access_token(new_token: str):
        """Save or update access token in the database."""
        with SessionLocal() as session:
            token_entry = session.query(AccessToken).first()
            if token_entry:
                if token_entry.token != new_token:
                    token_entry.token = new_token
                    token_entry.creation_ts = datetime.now(timezone.utc)
                    logger.info("Access Token updated in database")
            else:
                session.add(AccessToken(token=new_token, creation_ts=datetime.now(tz=ZoneInfo(sc.indian_timezone))))
                logger.info("Access Token added to database")
            session.commit()
