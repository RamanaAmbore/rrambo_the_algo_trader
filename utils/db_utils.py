import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database

from utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# Determine database type (SQLite or PostgreSQL)
SQLITE_DB = os.getenv("SQLITE_DB", "True").lower() == "true"
ACCCES_TOKEN_VALIDITY = os.getenv("ACCCES_TOKEN_VALIDITY")
logger.info(f'SQLITE database: {SQLITE_DB}')

if SQLITE_DB:
    SQLITE_PATH = os.getenv("SQLITE_PATH")
    DB_URL = f"sqlite:///{SQLITE_PATH}"

    # Ensure SQLite database file exists
    if not os.path.exists(SQLITE_PATH):
        open(SQLITE_PATH, 'w').close()  # Create empty file

else:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    DB_URL = POSTGRES_URL

    # Ensure PostgreSQL database exists
    if not database_exists(DB_URL):
        create_database(DB_URL)

# Create SQLAlchemy engine
engine = create_engine(DB_URL, echo=False)

# Create a session factory (thread-safe)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Test database connection
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("Successfully established initial connection to database")
except Exception as e:
    logger.error(f"Database connection failed: {e}")

# Define Base model
Base = declarative_base()


# Define AccessToken model
class AccessToken(Base):
    __tablename__ = "access_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
    creation_ts = Column(DateTime, default=datetime.utcnow)


# Create table if not exists
Base.metadata.create_all(engine)


def get_stored_access_token():
    """Fetch stored access token and check validity."""
    with SessionLocal() as session:
        token_entry = session.query(AccessToken).first()
        if token_entry:
            age = datetime.utcnow() - token_entry.creation_ts

            if age < timedelta(hours=int(ACCCES_TOKEN_VALIDITY)):
                return token_entry.token

    return None  # Token is expired or missing


def check_update_access_token(new_token):
    """Save or update access token in the database."""
    with SessionLocal() as session:
        token_entry = session.query(AccessToken).first()
        if token_entry:
            if token_entry.token != new_token:
                token_entry.token = new_token
                token_entry.creation_ts = datetime.utcnow()
                logger.info('Access Token updated to database')
        else:
            session.add(AccessToken(token=new_token, creation_ts=datetime.utcnow()))
            logger.info('Access Token added to database')
        session.commit()


def invalidate_access_token():
    """Remove stored access token (force re-login)."""
    with SessionLocal() as session:
        token_entry = session.query(AccessToken).first()
        if token_entry:
            session.delete(token_entry)
            session.commit()
