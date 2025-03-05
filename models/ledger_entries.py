from sqlalchemy import Column, String, Date, Numeric, Integer, select, DateTime, text, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from utils.date_time_utils import timestamp_indian
from .base import Base


class LedgerEntries(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    particulars = Column(String(255), nullable=False)
    posting_date = Column(String, nullable=True)
    cost_center = Column(String(100), nullable=True)
    voucher_type = Column(String(50), nullable=False)
    debit = Column(Numeric(15, 2), default=0.00)
    credit = Column(Numeric(15, 2), default=0.00)
    net_balance = Column(Numeric(15, 2), default=0.00)
    timestamp = Column(DateTime(timezone=True), default=timestamp_indian, server_default=text("CURRENT_TIMESTAMP"))
    source = Column(String, nullable=True, default="BATCH")
    warning = Column(Boolean, default=False)
    msg = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<LedgerEntry(particulars='{self.particulars}', posting_date='{self.posting_date}')>"

    @classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch only necessary columns to reduce memory usage."""
        result = await session.execute(select(cls.particulars, cls.posting_date))
        return {row for row in result.fetchall()}

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple ledger entries in bulk with validation."""
        for record in records:
            warning_messages = []

            # Validate and clean data
            if record.debit < 0:
                warning_messages.append("Debit value cannot be negative")
            if record.credit < 0:
                warning_messages.append("Credit value cannot be negative")
            if record.net_balance is None:
                record.net_balance = 0.00
                warning_messages.append("Net balance was empty, set to 0.00")
            if not record.posting_date:
                warning_messages.append("Posting date is missing")

            if warning_messages:
                record.warning = True
                record.msg = "; ".join(warning_messages)

        session.add_all(records)
        await session.commit()
