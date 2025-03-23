import asyncio
import contextvars  # Context management for async sessions
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy_utils import database_exists, create_database

from src.helpers.logger import get_logger
from src.models import ParameterTable
from src.models import access_tokens
from src.models import algo_schedule_time
from src.models import algo_schedules
from src.models import algo_thread_schedule_xref
from src.models import algo_threads
from src.models import broker_accounts
from src.models import parameter_table
from src.models import watchlists
from src.models.base import Base
from src.settings.parameter_manager import parms, refresh_parameters

logger = get_logger(__name__)  # Initialize logger

# Create an async context variable for session management
async_session_context = contextvars.ContextVar("async_session_context", default=None)


class DatabaseManager:
    """Database Utility Class for handling both Sync and Async database connections."""
    _initialized = False
    _engine = _async_engine = _sync_session_factory = _async_session_factory = None
    DB_URL = DB_ASYNC_URL = None
    _records = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize database connection and create tables."""
        if cls._initialized:
            return
        try:
            cls._setup_database_urls()
            cls._initialize_engines_and_sessions()
            cls._setup_database_tables()
            cls._initialized = True
            logger.info("Database and Parameters initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    @classmethod
    def _setup_database_urls(cls) -> None:
        """Setup database URLs based on configuration."""
        if parms.SQLITE_DB:
            db_path = Path(parms.SQLITE_PATH)
            cls.DB_URL = f"sqlite:///{db_path}"
            cls.DB_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if not db_path.exists():
                db_path.touch()
                logger.info(f"Created new SQLite database at {db_path}")
        else:
            cls.DB_URL = f"postgresql://{parms.POSTGRES_URL}"
            cls.DB_ASYNC_URL = f"postgresql+asyncpg://{parms.POSTGRES_URL}"
            if not database_exists(cls.DB_URL):
                create_database(cls.DB_URL)
                logger.info("Created new PostgreSQL database")

    @classmethod
    def _initialize_engines_and_sessions(cls) -> None:
        """Initialize database engines and session factories."""
        cls._engine = create_engine(cls.DB_URL,
                                    echo=parms.DB_DEBUG,
                                    pool_size=10,
                                    max_overflow=5,
                                    pool_timeout=30,
                                    pool_recycle=1800)

        cls._async_engine = create_async_engine(
            cls.DB_ASYNC_URL,
            echo=parms.DB_DEBUG,
            future=True,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800)

        cls._sync_session_factory = scoped_session(sessionmaker(
            bind=cls._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False))

        cls._async_session_factory = async_sessionmaker(
            bind=cls._async_engine,
            class_=AsyncSession,
            expire_on_commit=False)

    @classmethod
    def _setup_database_tables(cls) -> None:
        """Setup database tables."""
        Base.metadata.reflect(cls._engine)
        if parms.DROP_TABLES:
            Base.metadata.drop_all(cls._engine)
        Base.metadata.create_all(cls._engine)
        # Manually initialize default records
        with cls._engine.connect() as connection:
            broker_accounts.initialize_default_records(connection)
            access_tokens.initialize_default_records(connection)
            algo_schedules.initialize_default_records(connection)
            algo_schedule_time.initialize_default_records(connection)
            algo_threads.initialize_default_records(connection)
            algo_thread_schedule_xref.initialize_default_records(connection)
            parameter_table.initialize_default_records(connection)
            watchlists.initialize_default_records(connection)

    @classmethod
    def initialize_parameters(cls, refresh=False) -> None:
        """Initialize Parameters from the database."""
        if cls._records and not refresh:
            return
        with cls.get_sync_session() as session:
            cls._records = session.query(ParameterTable).all()
            refresh_parameters(records=cls._records, refresh=refresh)
            logger.info('Parameters refreshed from database')

    @classmethod
    def get_sync_session(cls) -> Session:
        """Get a synchronous database session."""
        if not cls._initialized:
            cls.initialize()
            cls.initialize_parameters()
        return cls._sync_session_factory()

    @classmethod
    @asynccontextmanager
    async def get_async_session(cls):
        """Get an async session using a proper async context manager."""
        if not cls._initialized:
            cls.initialize()

        session = cls._async_session_factory()
        try:
            yield session  # ✅ Allows usage with `async with`
        finally:
            await session.close()  # ✅ Ensures session is closed properly

    @classmethod
    async def cleanup_async_session(cls) -> None:
        """Cleanup the async session for the current task."""
        session = async_session_context.get()
        if session:
            await session.close()
            async_session_context.set(None)

    @classmethod
    async def get_session(cls, async_mode=False):
        """Get a sync or async session based on the flag."""
        if async_mode:
            return await cls.get_async_session()
        return cls.get_sync_session()

    @classmethod
    def test_connection(cls) -> bool:
        """Test database connection."""
        if not cls._initialized:
            cls.initialize()
        try:
            with cls._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    @classmethod
    async def cleanup(cls) -> None:
        """Cleanup database connections."""
        try:
            await cls.cleanup_async_session()
            if cls._engine:
                cls._engine.dispose()
            if cls._async_engine:
                await cls._async_engine.dispose()
            cls._initialized = False
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")


async def test_async_session():
    """Test async session functionality using a context manager."""
    try:
        async with DatabaseManager.get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            logger.info(f"Async session test result: {result.scalar_one_or_none()}")
    except Exception as e:
        logger.error(f"Async session test failed: {e}")


def test_sync_session():
    """Test sync session functionality."""
    try:
        with DatabaseManager.get_sync_session() as session:
            result = session.execute(text("SELECT 1"))
            logger.info(f"Sync session test result: {result.scalar_one_or_none()}")
    except Exception as e:
        logger.error(f"Sync session test failed: {e}")


async def main():
    """Main function to test both sync and async database sessions."""
    try:
        logger.info("Testing synchronous session...")
        test_sync_session()

        logger.info("Testing asynchronous session...")
        await test_async_session()

        logger.info(f"Connection test status: {DatabaseManager.test_connection()}")

    except Exception as e:
        logger.error(f"Main test failed: {e}")
    finally:
        await DatabaseManager.cleanup()


# Initialize database and Parameters on import
DatabaseManager.initialize()
DatabaseManager.initialize_parameters()

if __name__ == "__main__":
    asyncio.run(main())
