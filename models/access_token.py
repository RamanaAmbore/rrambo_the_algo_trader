from sqlalchemy import Column, String, DateTime, text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class AccessToken(Base):
    """
    Stores access tokens for API authentication.

    This table keeps track of access tokens associated with different accounts.
    It ensures that tokens are stored securely and can be retrieved or updated when needed.
    """

    __tablename__ = "access_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    token = Column(String(255), nullable=False)  # Access token for authentication
    source = Column(Enum(source), nullable=True, server_default="API")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Token creation timestamp
    warning_error = Column(Boolean, nullable=False, default=False)  # Flag for warnings/errors
    notes = Column(String(255), nullable=True)  # Additional message field for logging

    # # Relationship with BrokerAccounts model
    # broker_account = relationship("BrokerAccounts", back_populates="access_token")

    def __repr__(self):
        return (f"<AccessToken(id={self.id}, account_id='{self.account_id}', token='{self.token}', "
                f"source='{self.source}', timestamp={self.timestamp}, "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")
