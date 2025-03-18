from sqlalchemy import (
    Column, String, DateTime, text, Integer, Boolean,
    ForeignKey, Enum, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from src.settings.parameter_loader import Source, ThreadStatus
from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class AlgoThreadStatus(Base):
    """Stores thread information for scheduled tasks."""
    __tablename__ = "algo_thread_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread = Column(String(50), ForeignKey("algo_threads.thread", ondelete="CASCADE"), nullable=False)
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=True)
    schedule = Column(String(20), ForeignKey("algo_schedules.schedule", ondelete="CASCADE"), nullable=False)
    thread_status = Column(Enum(ThreadStatus), nullable=False, default=ThreadStatus.STARTED)
    run_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    source = Column(Enum(Source), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    warning_error = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_thread = relationship("AlgoThreads", back_populates="algo_thread_status")
    broker_account = relationship("BrokerAccounts", back_populates="algo_thread_status")
    algo_schedules = relationship("AlgoSchedules", back_populates="algo_thread_status")

    __table_args__ = (
        UniqueConstraint('thread', 'account', 'timestamp', name='uq_algo_thread_account'),
        Index('idx_thread_status', 'thread', 'thread_status'),
    )

    def __repr__(self):
        return (f"<ThreadStatus(id={self.id}, thread={self.thread}, "
                f"account='{self.account}', schedule='{self.schedule}', "
                f"thread_status={self.thread_status}, run_count={self.run_count}, "
                f"error_count={self.error_count}, source='{self.source}', "
                f"updated_at={self.timestamp})", f"updated_at={self.upd_timestamp})>")