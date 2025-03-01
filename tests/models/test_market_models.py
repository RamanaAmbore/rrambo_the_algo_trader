import pytest
import asyncio
from datetime import datetime, time, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from models.algoschedule import AlgoSchedule
from utils.db_connection import DbConnection

AsyncSessionLocal = DbConnection.async_session


@pytest.fixture
async def db_session():
    """Creates a new database session for testing."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_set_default_market_hours(db_session: AsyncSession):
    """Test setting default market hours if none exist."""
    # Ensure there is no existing default record
    await AlgoSchedule.set_default_market_hours(db_session)

    # Fetch the default market hours
    market_hours = await AlgoSchedule.get_market_hours(db_session)

    assert market_hours is not None
    assert market_hours.is_default is True
    assert market_hours.start_time.time() == time(9, 15)
    assert market_hours.end_time.time() == time(15, 30)


@pytest.mark.asyncio
async def test_get_market_hours_with_today_entry(db_session: AsyncSession):
    """Test retrieving today's market hours when an entry exists."""
    today = datetime.utcnow().date()
    market_start = datetime.combine(today, time(9, 30), tzinfo=timezone.utc)
    market_end = datetime.combine(today, time(15, 15), tzinfo=timezone.utc)

    # Insert a market hours entry for today
    new_market_hours = AlgoSchedule(
        market_date=datetime.utcnow(), start_time=market_start, end_time=market_end, is_default=False
    )
    db_session.add(new_market_hours)
    await db_session.commit()

    # Fetch market hours and check
    market_hours = await AlgoSchedule.get_market_hours(db_session)

    assert market_hours is not None
    assert market_hours.start_time == market_start
    assert market_hours.end_time == market_end


@pytest.mark.asyncio
async def test_get_market_hours_fallback_to_default(db_session: AsyncSession):
    """Test retrieving default market hours when no entry exists for today."""
    today = datetime.utcnow().date()

    # Delete today's entry (if any)
    await db_session.execute(
        AlgoSchedule.__table__.delete().where(AlgoSchedule.market_date == today)
    )
    await db_session.commit()

    # Ensure default hours exist
    await AlgoSchedule.set_default_market_hours(db_session)

    # Fetch market hours (should return default)
    market_hours = await AlgoSchedule.get_market_hours(db_session)

    assert market_hours is not None
    assert market_hours.is_default is True
    assert market_hours.start_time.time() == time(9, 15)
    assert market_hours.end_time.time() == time(15, 30)
