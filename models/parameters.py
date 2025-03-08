from typing import Optional

from sqlalchemy import (Column, Integer, String, DateTime, UniqueConstraint, ForeignKey, Enum, Index, Boolean, event,
                        CheckConstraint)
from sqlalchemy.orm import relationship

from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from utils.model_utils import source, DEFAULT_PARAMETERS
from .base import Base

logger = get_logger(__name__)


class Parameters(Base):
    """Model for storing system and account-specific parameters."""
    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    parameter = Column(String(50), nullable=False)
    value = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian)
    source = Column(Enum(source), nullable=False, server_default="MANUAL")
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationship with BrokerAccounts model
    broker_account = relationship("BrokerAccounts", back_populates="parameter")
    __table_args__ = (
        UniqueConstraint('account_id', 'parameter', name='uq_account_parameter'),
        Index('idx_account_parameter', 'account_id', 'parameter'),
        Index('idx_parameter_lookup', 'parameter'),
        CheckConstraint("parameter IS NOT NULL",
                       name="check_value_or_notes_not_null"),
    )
    @classmethod
    def get_parameter(cls, session, parameter: str, account_id: Optional[str] = None) -> Optional['Parameters']:
        """Get parameter value for given parameter name and optional account."""
        return session.query(cls).filter(
            cls.parameter == parameter,
            cls.account_id == account_id
        ).first()
    def __repr__(self):
        return (f"<Parameters(id={self.id}, account_id='{self.account_id}', "
                f"parameter='{self.parameter}', value='{self.value}', "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error})>")


@event.listens_for(Parameters.__table__, "after_create")
def initialize_parameters(target, connection, **kwargs):
    """Initialize default system parameters after table creation."""
    try:
        connection.execute(target.insert(), DEFAULT_PARAMETERS)
        logger.info("Default parameters initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing default parameters: {e}")

