import pytest
import asyncio
from utils.db_connection import DbConnection
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture(scope="session", autouse=True)
def init_sync_db():
    """Initialize the database synchronously before running tests."""
    DbConnection.init_db()


@pytest.fixture(scope="session", autouse=True)
async def init_async_db():
    """Initialize the database asynchronously before running tests."""
    await DbConnection.init_async_db()


def test_sync_db_connection():
    """Test synchronous database connection."""
    session = DbConnection.get_session(async_mode=False)
    try:
        result = session.execute("SELECT 1").fetchone()
        assert result is not None, "Sync query failed"
        assert result[0] == 1, "Unexpected sync query result"
    except SQLAlchemyError as e:
        pytest.fail(f"Sync query error: {e}")
    finally:
        session.close()


@pytest.mark.asyncio
async def test_async_db_connection():
    """Test asynchronous database connection."""
    async_session = DbConnection.get_session(async_mode=True)
    async with async_session as session:
        try:
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1, "Unexpected async query result"
        except SQLAlchemyError as e:
            pytest.fail(f"Async query error: {e}")
