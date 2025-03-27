from sqlalchemy import Column, String, DateTime, text, Integer, ForeignKey, UniqueConstraint, Index, \
    func
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class AccessTokens(Base):
    """Stores access tokens for API authentication."""
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=True)
    source = Column(String(50), nullable=False, server_default=Source.API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship
    broker_account = relationship("BrokerAccounts", back_populates="access_tokens")

    __table_args__ = (UniqueConstraint('account', name='uq_access_token'), Index("idx_account", "account"),)

    def __repr__(self):
        return (f"<AccessTokens(id={self.id}, account='{self.account}', "
                f"source='{self.source}', warning_error={self.warning_error})>")


