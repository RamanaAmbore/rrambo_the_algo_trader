import asyncio
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from src.models import ParameterTable
from src.models.base import Base
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager as Parameters

logger = get_logger(__name__)  # Initialize logger


class DatabaseManager:
    """Database Utility Class for handling both Sync and Async database connections."""
    _initialized = False
    _engine = _async_engine = _sync_session = _async_session = None
    DB_URL = DB_ASYNC_URL = None

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
            logger.info("Database and parameters initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    @classmethod
    def _setup_database_urls(cls) -> None:
        """Setup database URLs based on configuration."""
        if Parameters.SQLITE_DB:
            db_path = Path(Parameters.SQLITE_PATH)
            cls.DB_URL = f"sqlite:///{db_path}"
            cls.DB_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if not db_path.exists():
                db_path.touch()
                logger.info(f"Created new SQLite database at {db_path}")
        else:
            cls.DB_URL = f"postgresql://{Parameters.POSTGRES_URL}"
            cls.DB_ASYNC_URL = f"postgresql+asyncpg://{Parameters.POSTGRES_URL}"
            if not database_exists(cls.DB_URL):
                create_database(cls.DB_URL)
                logger.info("Created new PostgreSQL database")

    @classmethod
    def _initialize_engines_and_sessions(cls) -> None:
        """Initialize database engines and sessions."""
        cls._engine = create_engine(cls.DB_URL, echo=Parameters.DB_DEBUG)
        cls._async_engine = create_async_engine(cls.DB_ASYNC_URL, echo=Parameters.DB_DEBUG, future=True)

        cls._sync_session = scoped_session(
            sessionmaker(bind=cls._engine, autocommit=False, autoflush=False, expire_on_commit=False)
        )
        cls._async_session = sessionmaker(bind=cls._async_engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def _setup_database_tables(cls) -> None:
        """Setup database tables."""
        Base.metadata.reflect(cls._engine)
        if Parameters.DROP_TABLES:
            Base.metadata.drop_all(cls._engine)
        Base.metadata.create_all(cls._engine)

    @classmethod
    def initialize_parameters(cls,refresh=False) -> None:
        """Initialize parameters from database."""
        with cls.get_sync_session() as session:
            Parameters.refresh_parameters(records=session.query(ParameterTable).all(),refresh=refresh)
            logger.info('Parameters are refreshed from database')
            session.commit()

    @classmethod
    def get_sync_session(cls) -> Session:
        """Get a synchronous database session."""
        if not cls._initialized:
            cls.initialize()
            cls.initialize_parameters()
        return cls._sync_session()

    @classmethod
    async def get_async_session(cls):
        """Get an asynchronous database session."""
        if not cls._initialized:
            cls.initialize()
        async with cls._async_session() as session:
            yield session

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
            if cls._engine:
                cls._engine.dispose()
            if cls._async_engine:
                await cls._async_engine.dispose()
            cls._initialized = False
            logger.info("Database connections cleaned up")
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")


async def test_async_session():
    """Test async session functionality."""
    try:
        async for session in DatabaseManager.get_async_session():
            result = await session.execute(text("SELECT 1"))
            logger.info(f"Async session test result: {result.scalar()}")
    except Exception as e:
        logger.error(f"Async session test failed: {e}")


def test_sync_session():
    """Test sync session functionality."""
    try:
        with DatabaseManager.get_sync_session() as session:
            result = session.execute(text("SELECT 1"))
            logger.info(f"Sync session test result: {result.scalar()}")
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


# Initialize database and parameters on import
DatabaseManager.initialize()
DatabaseManager.initialize_parameters()

if __name__ == "__main__":
    asyncio.run(main())
