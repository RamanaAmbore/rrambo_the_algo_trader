import logging

from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint, event, ForeignKey

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source
logger = logging.getLogger(__name__)


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    parameter = Column(String, nullable=False)  # Changed from "key"
    parameter_value = Column(Numeric, nullable=False)

    timestamp = Column(DateTime, default=timestamp_indian, nullable=False)
    source = Column(String(10), nullable=False, default='MANUAL')
    warning_error = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('account_id', 'parameter', name='uq_account_parameter'),)

    def __repr__(self):
        return (f"<Settings(id={self.id}, account_id={self.account_id}, "
                f"parameter='{self.parameter}', value={self.parameter_value})>")
