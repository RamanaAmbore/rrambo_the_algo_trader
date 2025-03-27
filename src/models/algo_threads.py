from sqlalchemy import Column, Integer, String, DateTime, text, Index, UniqueConstraint, func, Boolean
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source
from .base import Base

logger = get_logger(__name__)


class AlgoThreads(Base):
    """Model for storing thread definitions."""
    __tablename__ = "algo_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(30), nullable=False, unique=True)  # Changed length to match ThreadStatus
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with ThreadStatus
    algo_thread_tracker = relationship("AlgoThreadTracker", back_populates="algo_thread",
                                      cascade="all, delete-orphan")  # Relationship with ThreadStatus
    algo_thread_schedule_xref = relationship("AlgoThreadScheduleXref", back_populates="algo_thread",
                                             cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('thread', name='uq_algo_thread'),
        Index("idx_thread", "thread"),
    )

    def __repr__(self):
        return (f"<Thread(id={self.id}, thread='{self.thread}', "
                f"source='{self.source}', notes='{self.notes}')>")


