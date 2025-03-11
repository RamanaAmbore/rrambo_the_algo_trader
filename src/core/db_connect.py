import asyncio
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from src.models import ParmTable
from src.models.base import Base
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager

logger = get_logger(__name__)  # Initialize logger

class DbConnect:
    """Database Utility Class for handling both Sync and Async database connections."""
    _initialized = False
    _engine = _async_engine = None
    _sync_session = _async_session = None
    DB_URL = DB_ASYNC_URL = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize database connection and create tables."""
        if cls._initialized:
            return
        try:
            cls._setup_database_urls()
            cls._setup_engines_and_sessions()
            cls._setup_tables()
            cls._initialized = True
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    @classmethod
    def _setup_database_urls(cls) -> None:
        """Setup database URLs based on configuration."""
        if ParameterManager.SQLITE_DB:
            db_path = Path(ParameterManager.SQLITE_PATH)
            cls.DB_URL = f"sqlite:///{db_path}"
            cls.DB_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            if not db_path.exists():
                db_path.touch()
                logger.info(f"Created SQLite database at {db_path}")
        else:
            cls.DB_URL = f"postgresql://{ParameterManager.POSTGRES_URL}"
            cls.DB_ASYNC_URL = f"postgresql+asyncpg://{ParameterManager.POSTGRES_URL}"
            if not database_exists(cls.DB_URL):
                create_database(cls.DB_URL)
                logger.info("Created PostgreSQL database")

    @classmethod
    def _setup_engines_and_sessions(cls) -> None:
        """Initialize database engines and sessions."""
        cls._engine = create_engine(cls.DB_URL, echo=ParameterManager.DB_DEBUG)
        cls._async_engine = create_async_engine(cls.DB_ASYNC_URL, echo=ParameterManager.DB_DEBUG)

        cls._sync_session = scoped_session(sessionmaker(bind=cls._engine, autocommit=False, autoflush=False))
        cls._async_session = sessionmaker(bind=cls._async_engine, class_=AsyncSession, expire_on_commit=False)

    @classmethod
    def _setup_tables(cls) -> None:
        """Create or drop database tables."""
        Base.metadata.reflect(cls._engine)
        if ParameterManager.DROP_TABLES:
            Base.metadata.drop_all(cls._engine)
        Base.metadata.create_all(cls._engine)

    @classmethod
    def initialize_parameters(cls) -> None:
        """Initialize parameters from database."""
        with cls.get_sync_session() as session:
            ParameterManager.refresh_parameters(session.query(ParmTable).all())
            logger.info('Parameters refreshed from database')
            session.commit()

    @classmethod
    def get_sync_session(cls) -> Session:
        """Get a synchronous database session."""
        if not cls._initialized:
            cls.initialize()
            cls.initialize_parameters()
        return cls._sync_session()

    @classmethod
    async def get_async_session(cls) -> AsyncSession:
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
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
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
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Testing Functions
async def test_async_session():
    """Test async session functionality."""
    try:
        async for session in DbConnect.get_async_session():
            value = (await session.execute(text("SELECT 1"))).scalar()
            logger.info(f"Async session test result: {value}")
    except Exception as e:
        logger.error(f"Async session test failed: {e}")

def test_sync_session():
    """Test sync session functionality."""
    try:
        with DbConnect.get_sync_session() as session:
            value = session.execute(text("SELECT 1")).scalar()
            logger.info(f"Sync session test result: {value}")
    except Exception as e:
        logger.error(f"Sync session test failed: {e}")

async def main():
    """Main function to test database sessions."""
    try:
        logger.info("Testing sync session...")
        test_sync_session()

        logger.info("Testing async session...")
        await test_async_session()

        logger.info(f"Database connection status: {DbConnect.test_connection()}")
    finally:
        await DbConnect.cleanup()

DbConnect.initialize()
if __name__ == "__main__":
    asyncio.run(main())
