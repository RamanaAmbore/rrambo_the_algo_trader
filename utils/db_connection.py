import os


from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils import database_exists, create_database

from models.base import Base
from utils.logger import get_logger
from utils.config_loader import sc, env

# Load environment variables
logger = get_logger(__name__)  # Initialize logger




class DbConnection:
    """Database Utility Class for handling both Sync and Async database connections."""

    if env.SQLITE_DB:
        DB_URL = f"sqlite:///{env.SQLITE_PATH}"
        DB_ASYNC_URL = f"sqlite+aiosqlite:///{env.SQLITE_PATH}"

        # Ensure SQLite database file exists
        if not os.path.exists(env.SQLITE_PATH):
            open(env.SQLITE_PATH, "w").close()
            logger.info(f"Created new SQLite database at {env.SQLITE_PATH}")

    else:
        DB_URL = f"postgresql://{env.POSTGRES_URL}"
        DB_ASYNC_URL = f"postgresql+asyncpg://{env.POSTGRES_URL}"

        # Ensure PostgreSQL database exists
        if not database_exists(DB_URL):
            create_database(DB_URL)
            logger.info("Created new PostgreSQL database.")

    # Create synchronous engine & session
    echo = os.getenv('DB_DEBUG').lower() == 'true'
    engine = create_engine(DB_URL, echo=echo)
    sync_session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False))

    # Create async engine & session
    async_engine = create_async_engine(DB_ASYNC_URL, echo=echo, future=True)
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def get_session(cls, async_mode: bool = False):
        """
        Returns a database session.

        :param async_mode: If True, returns an async session, else returns a sync session.
        :return: Sync or Async session object
        """
        return cls.async_session() if async_mode else cls.sync_session()

    @classmethod
    def init_db(cls):
        """Initialize the database (Sync mode)"""
        Base.metadata.create_all(cls.engine)  # Create tables if they don’t exist
        logger.info("Database tables created, if not existed (sync mode).")

    @classmethod
    async def init_async_db(cls):
        """Initialize the database asynchronously (Async mode)"""
        async with cls.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)  # Async way to create tables
        logger.info("Database tables created if not existed (async mode).")

    @classmethod
    def test_connection(cls):
        """Tests the database connection (Sync mode)."""
        try:
            with cls.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Successfully connected to the database.")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")

    @classmethod
    async def get_async_session(cls):
        """Provides an async session for database operations."""
        async with cls.async_session() as session:
            yield session


DbConnection.init_db()
