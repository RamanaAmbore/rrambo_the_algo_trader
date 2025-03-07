from sqlalchemy import Column, String, Numeric, Integer, select, DateTime, text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class LedgerEntries(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    particulars = Column(String(255), nullable=False)
    posting_date = Column(String(10), nullable=True)
    cost_center = Column(String(20), nullable=True)
    voucher_type = Column(String(20), nullable=False)
    debit = Column(Numeric(10, 2), default=0.00)
    credit = Column(Numeric(10, 2), default=0.00)
    net_balance = Column(Numeric(15, 2), default=0.00)
    source = Column(Enum(source), nullable=True, server_default="REPORTS")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        return f"<LedgerEntry(particulars='{self.particulars}', posting_date='{self.posting_date}')>"

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing ledger entry IDs from the table."""
        result = await session.execute(
            select(cls.particulars, cls.posting_date, cls.cost_center, cls.voucher_type, cls.debit, cls.credit,
                   cls.net_balance))
        return {row for row in result.fetchall()}

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple ledger records in bulk."""
        session.add_all(records)
        await session.commit()
