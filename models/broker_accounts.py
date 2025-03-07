from sqlalchemy import Column, String, DateTime, text, Boolean, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base

from model_utils import source
class BrokerAccounts(Base):
    """Model for storing broker account details manually."""
    __tablename__ = "broker_accounts"

    account_id = Column(String(10), primary_key=True)  # Unique account identifier
    broker_name = Column(String(20), nullable=False)  # Name of the broker
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Auto timestamps with timezone
    warning_error = Column(Boolean, nullable=False, default=False)  # Flag for any warnings/errors in scheduling
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        """String representation for debugging."""
        return f"<BrokerAccounts(account_id='{self.account_id}', broker_name='{self.broker_name}', notes='{self.notes}')>"
