import asyncio
from datetime import datetime
from utils.db_conn import AsyncSessionLocal
from models.market_hours import MarketHours

market_hours_cache = None  # Global variable for caching market hours

async def load_market_hours():
    """Load market hours into cache at startup and refresh only if needed."""
    global market_hours_cache
    async with AsyncSessionLocal() as db_session:
        market_hours_cache = await MarketHours.get_market_hours(db_session)

async def is_market_open():
    """Check if the market is open using cached market hours."""
    global market_hours_cache
    if market_hours_cache is None:
        await load_market_hours()  # Load cache if empty

    if market_hours_cache:
        start_time, end_time = market_hours_cache
        current_time = datetime.utcnow()
        return start_time <= current_time <= end_time
    return False
