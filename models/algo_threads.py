from sqlalchemy import Column, Integer, String, DateTime, text, Boolean, Index, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)

class AlgoThreads(Base):
    """Model for storing thread definitions."""
    __tablename__ = "algo_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(50), nullable=False, unique=True)  # Changed length to match ThreadStatus
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationship with ThreadStatus
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="algo_threads", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('thread', name='uq_algo_thread'),
        Index("idx_thread", "thread"),
    )

    def __repr__(self):
        return (f"<Thread(id={self.id}, thread='{self.thread}', "  # Fixed class name in repr
                f"source='{self.source}', notes='{self.notes}')>")