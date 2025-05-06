from sqlalchemy import Column, Integer, String, DateTime, text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base
from ..settings.constants_manager import Source

logger = get_logger(__name__)

class Users(Base):
    """User model for authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    source = Column(String(50), nullable=True, server_default=Source.API)
    notes = Column(String(255), nullable=True)

    # Relationships
    # This should reference the AccessTokens class and point back to the user
    access_tokens_rel = relationship("AccessTokens", back_populates="user_rel", passive_deletes=True)
    UniqueConstraint('user_id', name='uq_user_id1'),

    def __repr__(self):
        return f'<User {self.user_id}>'