from sqlalchemy import Column, String, DateTime, text, Boolean, Integer, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class AccessTokens(Base):
    """Stores access tokens for API authentication."""
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False)
    source = Column(Enum(source), nullable=True, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship
    broker_account = relationship("BrokerAccounts", back_populates="access_tokens")

    __table_args__ = (
        UniqueConstraint('account', name='uq_access_token'),
        Index("idx_account", "account"),
    )

    def __repr__(self):
        return (f"<AccessTokens(id={self.id}, account='{self.account}', "
                f"source='{self.source}', warning_error={self.warning_error})>")