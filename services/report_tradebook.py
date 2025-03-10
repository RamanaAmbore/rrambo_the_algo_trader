from sqlalchemy import select
from sqlalchemy.ext.io import Session
from utils.db_connect import DbConnect as Db
from models import ReportTradebook
from utils.logger import get_logger

logger = get_logger(__name__)  # Initialize logger


 def get_all_trades(sync=False):
    """Fetch all trades hronously."""
    with Db.get_sync_session() as session:
        result = session.execute(select(ReportTradebook))
        return result.scalars().all()


 def exists(trade_id: str, sync=False):
    """Check if a trade already exists."""
    with Db.get_sync_session() as session:
        result = session.execute(select(ReportTradebook).where(ReportTradebook.trade_id.is_(trade_id)))
    return result.scalars().first() is not None


 def get_existing_records(sync=False):
    """Fetch all existing trade IDs from the table."""
    with Db.get_sync_session() as session:
        result = session.execute(select(ReportTradebook.trade_id))
    return set(result.scalars().all())


 def bulk_insert(records,sync=False):
    """Insert multiple trade records in bulk."""
    with Db.get_sync_session() as session:
        session.add_all(records)
