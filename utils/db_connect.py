from pathlib import Path

from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from models import Parameters
from models.base import Base
from utils.logger import get_logger
from utils.parm_loader import Parm

# Load environment variables
logger = get_logger(__name__)  # Initialize logger


class DbConnection:
    """Database Utility Class for handling both Sync and Async database connections."""

    _initialized: bool = False
    _engine = None
    _async_engine = None
    _sync_session = None
    _async_session = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize database connection and create tables."""
        if cls._initialized:
            return

        try:
            # Setup database URLs
            if Parm.SQLITE_DB:
                db_path = Path(Parm.SQLITE_PATH)
                cls.DB_URL = f"sqlite:///{db_path}"
                cls.DB_ASYNC_URL = f"sqlite+aiosqlite:///{db_path}"

                # Ensure SQLite database directory exists
                db_path.parent.mkdir(parents=True, exist_ok=True)
                if not db_path.exists():
                    db_path.touch()
                    logger.info(f"Created new SQLite database at {db_path}")

            else:
                cls.DB_URL = f"postgresql://{Parm.POSTGRES_URL}"
                cls.DB_ASYNC_URL = f"postgresql+asyncpg://{Parm.POSTGRES_URL}"

                if not database_exists(cls.DB_URL):
                    create_database(cls.DB_URL)
                    logger.info("Created new PostgreSQL database")

            # Initialize engines and sessions
            echo = Parm.DB_DEBUG
            cls._engine = create_engine(cls.DB_URL, echo=echo)
            cls._async_engine = create_async_engine(cls.DB_ASYNC_URL, echo=echo, future=True)

            cls._sync_session = scoped_session(
                sessionmaker(bind=cls._engine, autocommit=False, autoflush=False, expire_on_commit=False))
            cls._async_session = sessionmaker(bind=cls._async_engine, class_=AsyncSession, expire_on_commit=False)

            # Configure all mappers before creating
            Base.metadata.reflect(cls._engine)
            if Parm.DROP_TABLES:
                Base.metadata.drop_all(cls._engine)
            Base.metadata.create_all(cls._engine)
            cls._initialized = True

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

        with cls.get_sync_session() as session:
            parameters = session.query(Parameters).all()
            Parm.reset_parms(parameters)
            session.commit()

        logger.info("Database and parameters initialized successfully")

    @classmethod
    def get_sync_session(cls) -> Session:
        """Get a synchronous database session."""
        if not cls._initialized:
            cls.initialize()
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
        """Test database connection and return status."""
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
        async for session in DbConnection.get_async_session():
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"Async session test result: {value}")
    except Exception as e:
        logger.error(f"Async session test failed: {e}")


def test_sync_session():
    """Test sync session functionality."""
    try:
        with DbConnection.get_sync_session() as session:
            result = session.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"Sync session test result: {value}")
    except Exception as e:
        logger.error(f"Sync session test failed: {e}")


async def main():
    """Main function to test both sync and async database sessions."""
    try:
        logger.info("Testing database connections...")

        # Test sync session
        logger.info("Testing synchronous session...")
        test_sync_session()

        # Test async session
        logger.info("Testing asynchronous session...")
        await test_async_session()

        # Test connection
        connection_status = DbConnection.test_connection()
        logger.info(f"Connection test status: {connection_status}")

    except Exception as e:
        logger.error(f"Main test failed: {e}")
    finally:
        await DbConnection.cleanup()  # Changed to await cleanup

DbConnection.initialize()
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
