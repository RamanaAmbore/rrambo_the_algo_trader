from sqlalchemy import select

from src.models import ReportLedgerEntries
from src.utils import DbConnect as Db

 def get_existing_records(sync=False):
    """Fetch all existing ledger entry IDs from the table."""
    with Db.get_sync_session() as session:
        result = await session.execute(
            select(ReportLedgerEntries.particulars, ReportLedgerEntries.posting_date, ReportLedgerEntries.cost_center,
                   ReportLedgerEntries.voucher_type, ReportLedgerEntries.debit, ReportLedgerEntries.credit, ReportLedgerEntries.net_balance))
        return {row for row in result.fetchall()}


 def bulk_insert(records,sync=False):
    """Insert multiple ledger records in bulk."""
    with Db.get_sync_session() as session:
        session.add_all(records)
        await session.commit()
