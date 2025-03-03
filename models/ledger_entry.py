from sqlalchemy import Column, String, Date, Numeric, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    particulars = Column(String(255), nullable=False)
    posting_date = Column(Date, nullable=False)
    cost_center = Column(String(255), nullable=True)
    voucher_type = Column(String(100), nullable=False)
    debit = Column(Numeric(15, 2), default=0.00)
    credit = Column(Numeric(15, 2), default=0.00)
    net_balance = Column(Numeric(15, 2), default=0.00)

    def __repr__(self):
        return f"<LedgerEntry(particulars='{self.particulars}', posting_date='{self.posting_date}')>"


@classmethod
    async def get_existing_records(cls, session: AsyncSession):
        """Fetch all existing ledger entry IDs from the table."""
        result = await session.execute(select(cls.entry_id))
        return {row[0] for row in result.fetchall()}

    @classmethod
    async def bulk_insert(cls, session: AsyncSession, records):
        """Insert multiple ledger records in bulk."""
        session.add_all(records)
        await session.commit()