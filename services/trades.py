from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db_connect import DbConnect as Db
from models import ReportTradebook
from utils.logger import get_logger

logger = get_logger(__name__)  # Initialize logger


async def get_all_trades(sync=False):
    """Fetch all trades asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(ReportTradebook))
        return result.scalars().all()


async def exists(trade_id: str, sync=False):
    """Check if a trade already exists."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(ReportTradebook).where(ReportTradebook.trade_id.is_(trade_id)))
    return result.scalars().first() is not None


async def get_existing_records(sync=False):
    """Fetch all existing trade IDs from the table."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(ReportTradebook.trade_id))
    return set(result.scalars().all())


async def bulk_insert(records,sync=False):
    """Insert multiple trade records in bulk."""
    with Db.get_session(sync) as session:
        session.add_all(records)
