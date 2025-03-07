from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import LedgerEntries
from utils.db_connection import DbConnection as Db

async def get_existing_records(sync=False):
    """Fetch all existing ledger entry IDs from the table."""
    with Db.get_session(sync) as session:
        result = await session.execute(
            select(LedgerEntries.particulars, LedgerEntries.posting_date, LedgerEntries.cost_center,
                   LedgerEntries.voucher_type, LedgerEntries.debit, LedgerEntries.credit, LedgerEntries.net_balance))
        return {row for row in result.fetchall()}


async def bulk_insert(records,sync=False):
    """Insert multiple ledger records in bulk."""
    with Db.get_session(sync) as session:
        session.add_all(records)
        await session.commit()
