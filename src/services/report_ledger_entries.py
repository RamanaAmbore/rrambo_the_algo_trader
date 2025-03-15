from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.report_ledger_entries import ReportLedgerEntries
from src.core.database_manager import DatabaseManager as Db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LedgerEntriesService:
    """Service class for managing ledger entries."""

    @staticmethod
    async def get_existing_records(async_mode=True):
        """Fetch all existing ledger entries as a set of tuples."""
        Session = Db.get_session(async_mode)
        async with Session() as session:
            result = await session.execute(select(
                ReportLedgerEntries.particulars, ReportLedgerEntries.posting_date,
                ReportLedgerEntries.cost_center, ReportLedgerEntries.voucher_type,
                ReportLedgerEntries.debit, ReportLedgerEntries.credit,
                ReportLedgerEntries.net_balance
            ))
            return {row for row in result.fetchall()}

    @staticmethod
    async def insert_ledger_entry(record, async_mode=True):
        """Insert a single ledger entry if it doesn't already exist."""
        Session = Db.get_session(async_mode)
        async with Session() as session:
            try:
                LedgerEntriesService.validate_and_clean(record)

                # Check if the record exists
                existing_entry = await session.execute(select(ReportLedgerEntries).where(
                    (ReportLedgerEntries.particulars == record.particulars) &
                    (ReportLedgerEntries.posting_date == record.posting_date) &
                    (ReportLedgerEntries.cost_center == record.cost_center) &
                    (ReportLedgerEntries.voucher_type == record.voucher_type) &
                    (ReportLedgerEntries.debit == record.debit) &
                    (ReportLedgerEntries.credit == record.credit) &
                    (ReportLedgerEntries.net_balance == record.net_balance)
                ))

                if existing_entry.scalars().first() is None:
                    session.add(record)
                    await session.commit()
                    logger.info(f"Inserted ledger entry: {record}")
                else:
                    logger.warning(f"Skipping duplicate ledger entry: {record}")
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error inserting ledger entry: {e}")

    @staticmethod
    async def bulk_insert_ledger_entries(records, async_mode=True):
        """Bulk insert multiple ledger entries, skipping duplicates efficiently."""
        Session = Db.get_session(async_mode)
        async with Session() as session:
            try:
                new_records = []

                for record in records:
                    LedgerEntriesService.validate_and_clean(record)

                    # Check if the record exists before adding
                    existing_entry = await session.execute(select(ReportLedgerEntries).where(
                        (ReportLedgerEntries.particulars == record.particulars) &
                        (ReportLedgerEntries.posting_date == record.posting_date) &
                        (ReportLedgerEntries.cost_center == record.cost_center) &
                        (ReportLedgerEntries.voucher_type == record.voucher_type) &
                        (ReportLedgerEntries.debit == record.debit) &
                        (ReportLedgerEntries.credit == record.credit) &
                        (ReportLedgerEntries.net_balance == record.net_balance)
                    ))

                    if existing_entry.scalars().first() is None:
                        new_records.append(record)
                    else:
                        logger.warning(f"Skipping duplicate ledger entry: {record}")

                if new_records:
                    session.add_all(new_records)
                    await session.commit()
                    logger.info(f"Inserted {len(new_records)} new ledger entries.")
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error in bulk ledger entry insertion: {e}")

    @staticmethod
    def validate_and_clean(record):
        """Validate and clean ledger entry data before insertion."""
        warning_messages = []

        if record.debit in ("", None):
            record.debit = 0.0
            warning_messages.append("Debit value was empty, set to 0.0")
        if record.credit in ("", None):
            record.credit = 0.0
            warning_messages.append("Credit value was empty, set to 0.0")
        if record.net_balance in ("", None):
            record.net_balance = 0.0
            warning_messages.append("Net balance was empty, set to 0.0")
        if record.posting_date in ("", None):
            record.posting_date = None
            warning_messages.append("Posting date was empty, set to None")

        if warning_messages:
            record.warning_error = True
            record.notes = "; ".join(warning_messages)
            logger.warning(f"Data corrections for record {record}: {'; '.join(warning_messages)}")
