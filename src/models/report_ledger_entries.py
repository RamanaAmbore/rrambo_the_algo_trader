from sqlalchemy import (Column, String, Numeric, Integer, select, DateTime, text, Boolean, ForeignKey, Enum,
                        CheckConstraint, Index, UniqueConstraint, func)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class ReportLedgerEntries(Base):
    __tablename__ = "report_ledger_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    particulars = Column(String(255), nullable=False)
    posting_date = Column(DateTime(timezone=True), nullable=True)
    cost_center = Column(String(20), nullable=True)
    voucher_type = Column(String(20), nullable=True)
    debit = Column(Numeric(10, 2), default=0.00, nullable=True)
    credit = Column(Numeric(10, 2), default=0.00, nullable=True)
    net_balance = Column(Numeric(15, 2), default=0.00)
    source = Column(String(50), nullable=False, server_default="REPORTS")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="report_ledger_entries")

    __table_args__ = (CheckConstraint("debit >= 0", name="check_debit_non_negative"),
                      CheckConstraint("credit >= 0", name="check_credit_non_negative"),
                      UniqueConstraint('account', 'particulars', 'posting_date', 'cost_center',
                                       'voucher_type', 'debit', 'credit', 'net_balance', name='uq_account_symbol3'),
                      Index("idx_account_symbol8", 'account', 'particulars', 'posting_date',
                            'cost_center', 'voucher_type', 'debit', 'credit', 'net_balance'),
                      Index("idx_account_date1", "account", "posting_date"),
                      Index("idx_voucher_type", "voucher_type"),)

    def __repr__(self):
        return (f"<LedgerEntry(id={self.id}, account='{self.account}', "
                f"particulars='{self.particulars}', posting_date='{self.posting_date}', "
                f"voucher_type='{self.voucher_type}', debit={self.debit}, credit={self.credit}, "
                f"net_balance={self.net_balance}, source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")

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
