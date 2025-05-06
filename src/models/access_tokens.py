from sqlalchemy import Column, String, DateTime, text, Integer, ForeignKey, UniqueConstraint, Index, \
    func, select, Boolean
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_ACCESS_TOKENS
from .base import Base

logger = get_logger(__name__)


class AccessTokens(Base):
    """Stores access tokens for API authentication."""
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    service_name = Column(String(50), nullable=True)
    token = Column(String(255), nullable=True)
    api_key = Column(String(255), nullable=True)
    api_secret = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    source = Column(String(50), nullable=True, server_default=Source.API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    broker_accounts_rel = relationship("BrokerAccounts", back_populates="access_tokens_rel", passive_deletes=True)
    # This should reference the Users class
    user_rel = relationship("Users", back_populates="access_tokens_rel", passive_deletes=True)

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_access_token_key'),
        Index("idx_account1", "account"),
    )

    def __repr__(self):
        return (f"<AccessTokens(id={self.id}, user_id='{self.user_id}, account='{self.account}', "
                f"service_name='{self.service_name}', source='{self.source}')>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AccessTokens.__table__
        with connection.begin():  # Create transaction context
            for record in DEF_ACCESS_TOKENS:
                try:
                    # Use merge instead of manual check + insert
                    stmt = table.merge().values(record)
                    connection.execute(stmt)
                except Exception as e:
                    logger.error(f"Error processing record {record['account']}: {e}")
                    raise
        logger.info('Default Access Token records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default access tokens: {e}")
        connection.rollback()  # Explicit rollback
        raise