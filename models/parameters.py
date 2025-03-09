from typing import Optional
from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, Enum, Index, Boolean, event,
                        CheckConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from settings.default_db_values import source, DEFAULT_PARAMETERS
from .base import Base

logger = get_logger(__name__)


class Parameters(Base):
    """Model for storing system and account-specific parameters."""
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    parameter = Column(String(50), nullable=False)
    value = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian)
    source = Column(Enum(source), nullable=False, server_default="MANUAL")
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="parameter")
    __table_args__ = (
        UniqueConstraint('account', 'parameter', name='uq_account_parameter'),
        Index('idx_account_parameter', 'account', 'parameter'),
        Index('idx_parameter_lookup', 'parameter'),
        CheckConstraint("parameter IS NOT NULL",
                       name="check_value_or_notes_not_null"),
    )




    def __repr__(self):
        return (f"<Parameters(id={self.id}, account='{self.account}', "
                f"parameter='{self.parameter}', value='{self.value}', "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error})>")

def get_parameter(session, parameter: str, account: Optional[str] = None) -> Optional['Parameters']:
        """Get parameter value for given parameter name and optional account."""
        return session.query(Parameters).filter(
            Parameters.parameter == parameter,
            Parameters.account == account
        ).first()
def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = Parameters.__table__
        for record in DEFAULT_PARAMETERS:
            exists = connection.execute(
                select(table).where(
                    table.c.parameter == record['parameter'],
                    table.c.account == record.get('account')
                )
            ).scalar() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default records: {e}")


@event.listens_for(Parameters.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Parameter records inserted after after_create event')

