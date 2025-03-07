from sqlalchemy import Column, Integer, DateTime, String, Boolean, text, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source

class RefreshFlags(Base):
    """Stores account-specific settings with key-value pairs."""
    __tablename__ = "refresh_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    thread_name = Column(String(20), nullable=False)  # Setting key
    value = Column(Boolean, nullable=False, default=False)  # Boolean value
    source = Column(Enum(source), nullable=True, server_default="MANUAL")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)
    notes = Column(String, nullable=True)  # Additional notes
