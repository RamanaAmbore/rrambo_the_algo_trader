from sqlalchemy import (
    Column, Integer, DateTime, String, Boolean, text, 
    ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from src.utils.date_time_utils import timestamp_indian
from src.utils.logger import get_logger
from .base import Base
from src.settings.parameter_loader import Source

logger = get_logger(__name__)


class RefreshFlags(Base):
    """Stores account-specific settings with key-value pairs."""
    __tablename__ = "refresh_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    thread_name = Column(String(20), nullable=False)
    value = Column(Boolean, nullable=False, default=False)
    source = Column(Enum(Source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
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
