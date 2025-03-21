from sqlalchemy import (
    Column, Integer, DateTime, String, Boolean, text,
    ForeignKey, Enum, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from src.settings.constants_manager import Source
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class RefreshFlags(Base):
    """Stores account-specific settings with key-value pairs."""
    __tablename__ = "refresh_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    thread_name = Column(String(20), nullable=False)
    value = Column(Boolean, nullable=False, default=False)
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="refresh_flags")

    __table_args__ = (
        UniqueConstraint('account', 'thread_name', name='print2'),
        Index('idx_account_timestamp1', 'account', 'timestamp'),
    )

    def __repr__(self):
        return (f"<RefreshFlags(id={self.id}, account='{self.account}', "
                f"thread_name='{self.thread_name}', value={self.value}, "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error})>")
