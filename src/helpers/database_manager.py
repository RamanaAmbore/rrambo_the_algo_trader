import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy_utils import database_exists, create_database

from src.helpers.logger import get_logger
from src.models.base import Base
from src.settings.parameter_manager import parms

logger = get_logger(__name__)


class DatabaseManager:
    """Singleton Database Utility Class for handling both Sync and Async database connections."""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # Fix: Use instance variable
            self._setup_database_urls()
            self._initialize_engines_and_sessions()
            self._setup_database_tables()
            self._initialized = True
            logger.info("Database and Parameters initialized successfully")

    def _setup_database_urls(self):
        """Setup database URLs based on configuration."""
        if parms.SQLITE_DB:
            db_path = Path(parms.SQLITE_PATH)
            self.DB_URL = f"sqlite:///{db_path}"
            self.DB_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if not db_path.exists():
                db_path.touch()
                logger.info(f"Created new SQLite database at {db_path}")
        else:
            self.DB_URL = f"postgresql://{parms.POSTGRES_URL}"
            self.DB_ASYNC_URL = f"postgresql+asyncpg://{parms.POSTGRES_URL}"
            if not database_exists(self.DB_URL):
                create_database(self.DB_URL)
                logger.info("Created new PostgreSQL database")

    def _initialize_engines_and_sessions(self):
        """Initialize database engines and session factories."""
        self._engine = create_engine(self.DB_URL, echo=parms.DB_DEBUG, pool_size=10, max_overflow=5, pool_timeout=30,
                                     pool_recycle=1800)
        self._async_engine = create_async_engine(self.DB_ASYNC_URL, echo=parms.DB_DEBUG, future=True, pool_size=10,
                                                 max_overflow=5, pool_timeout=30, pool_recycle=1800)

        self._sync_session_factory = scoped_session(
            sessionmaker(bind=self._engine, autocommit=False, autoflush=False, expire_on_commit=False))
        self._async_session_factory = async_sessionmaker(bind=self._async_engine, class_=AsyncSession,
                                                         expire_on_commit=False)

    def _setup_database_tables(self):
        """Setup database tables."""
        Base.metadata.reflect(self._engine)
        if parms.DROP_TABLES:
            Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    def get_sync_session(self) -> Session:
        """Get a synchronous database session."""
        return self._sync_session_factory()

    @asynccontextmanager
    async def get_async_session(self):
        """Get an async session using a proper async context manager."""
        session = self._async_session_factory()
        try:
            yield session
        finally:
            await session.close()

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


async def test_async_session():
    """Test async session functionality using a context manager."""
    db_manager = DatabaseManager()
    try:
        async with db_manager.get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            logger.info(f"Async session test result: {result.scalar_one_or_none()}")
    except Exception as e:
        logger.error(f"Async session test failed: {e}")


def test_sync_session():
    """Test sync session functionality."""
    db_manager = DatabaseManager()
    try:
        with db_manager.get_sync_session() as session:
            result = session.execute(text("SELECT 1"))
            logger.info(f"Sync session test result: {result.scalar_one_or_none()}")
    except Exception as e:
        logger.error(f"Sync session test failed: {e}")

db = DatabaseManager()

async def main():
    """Main function to test both sync and async database sessions."""
    db_manager = DatabaseManager()
    try:
        logger.info("Testing synchronous session...")
        test_sync_session()

        logger.info("Testing asynchronous session...")
        await test_async_session()

        logger.info(f"Connection test status: {db_manager.test_connection()}")
    except Exception as e:
        logger.error(f"Main test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
