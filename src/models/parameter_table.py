from typing import Optional

from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, Enum, Index, Boolean, event,
                        CheckConstraint, func, text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from src.settings.parameter_loader import Source, DEFAULT_PARAMETERS
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class ParameterTable(Base):
    """Model for storing system and account-specific parameters."""
    __tablename__ = 'parameter_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    parameter = Column(String(50), nullable=False)
    value = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    source = Column(Enum(Source), nullable=False, server_default=Source.MANUAL.name)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="parameter_table")
    __table_args__ = (
        UniqueConstraint('account', 'parameter', name='uq_account_parameter_table'),
        Index('parameter_table1', 'account', 'parameter'),
        Index('idx_parameter_lookup', 'parameter'),
        CheckConstraint("parameter IS NOT NULL",
                        name="check_value_or_notes_not_null"),
    )

    def __repr__(self):
        return (f"<Parameters(id={self.id}, account='{self.account}', "
                f"parameter='{self.parameter}', value='{self.value}', "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error})>")


def get_parameter(session, parameter: str, account: Optional[str] = None) -> Optional['ParameterTable']:
    """Get parameter value for given parameter name and optional account."""
    return session.query(ParameterTable).filter(
        ParameterTable.parameter == parameter,
        ParameterTable.account == account
    ).first()


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ParameterTable.__table__
        for record in DEFAULT_PARAMETERS:
            exists = connection.execute(
                select(table).where(
                    table.c.parameter == record['parameter'],
                    table.c.account == record.get('account')
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
    except Exception as e:
        logger.error(f"Error managing default Parameter records: {e}")
        raise


@event.listens_for(ParameterTable.__table__, 'after_create')
def insert_default_records(target, connection, **kwargs):
    """Insert default records after table creation."""
    initialize_default_records(connection)
    logger.info('Default Parameter records inserted after after_create event')
