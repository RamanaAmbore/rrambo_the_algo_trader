from sqlalchemy import (
    Column, Integer, String, DateTime, UniqueConstraint, Index, Boolean,
    CheckConstraint, func, text, ForeignKey
)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class ParameterTable(Base):
    """Model for storing system-wide and account-specific parameters."""
    __tablename__ = 'parameter_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    parameter = Column(String(50), nullable=False)
    value = Column(String(255), nullable=True)
    type = Column(String(10), nullable=True)
    encrypted = Column(Boolean, nullable=False, default=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    notes = Column(String(255), nullable=True)
    broker_accounts_rel = relationship("BrokerAccounts", back_populates="parameter_table_rel", passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint('account', 'parameter', name='uq_account_parameter_table'),
        Index('parameter_table1', 'account', 'parameter'),
        Index('idx_parameter_lookup', 'parameter'),
        CheckConstraint("parameter IS NOT NULL", name="check_parameter_not_null"),
    )

    def __repr__(self):
        return (f"<ParameterTable(id={self.id}, account='{self.account}', "
                f"parameter='{self.parameter}', value='{self.value}', "
                f"source='{self.source}', timestamp={self.timestamp})>")
