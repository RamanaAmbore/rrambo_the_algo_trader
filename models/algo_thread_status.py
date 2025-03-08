from sqlalchemy import (
    Column, String, DateTime, text, Boolean, Integer,
    ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source

logger = get_logger(__name__)


class AlgoThreadStatus(Base):
    """Stores thread information for scheduled tasks."""
    __tablename__ = "algo_thread_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(50), ForeignKey("algo_threads.thread", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    schedule = Column(String(20), ForeignKey("algo_schedule.schedule", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    run_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    source = Column(Enum(source), nullable=True, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_threads = relationship("AlgoThreads", back_populates="algo_thread_status")
    broker_account = relationship("BrokerAccounts", back_populates="algo_thread_status")
    algo_schedule = relationship("AlgoSchedules", back_populates="algo_thread_status")

    __table_args__ = (
        UniqueConstraint('thread', 'account_id', name='uq_algo_thread_account'),
        Index('idx_active_threads', 'is_active', 'next_run'),
        Index('idx_thread_status', 'thread', 'is_active'),
    )

    def __repr__(self):
        return (f"<ThreadStatus(id={self.id}, thread={self.thread}, "
                f"account_id='{self.account_id}', schedule='{self.schedule}', "
                f"is_active={self.is_active}, last_run={self.last_run}, "
                f"next_run={self.next_run}, run_count={self.run_count}, "
                f"error_count={self.error_count}, source='{self.source}')>")


