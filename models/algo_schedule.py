from sqlalchemy import Column, String, DateTime, text, Boolean, Enum, Integer, event
from sqlalchemy.orm import relationship
from utils.date_time_utils import timestamp_indian
from utils.logger import get_logger
from .base import Base
from utils.model_utils import source, DEFAULT_SCHEDULE_RECORDS

logger = get_logger(__name__)


class AlgoSchedules(Base):
    """Stores schedule definitions that can be referenced by other tables."""
    __tablename__ = "algo_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(String(20), nullable=False, unique=True)  # Unique constraint for referential integrity
    is_active = Column(Boolean, nullable=False, default=True)
    source = Column(Enum(source), nullable=True, server_default="MANUAL")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                      server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    algo_schedule_time = relationship("AlgoScheduleTime", back_populates="algo_schedule")
    algo_thread_status = relationship("AlgoThreadStatus", back_populates="algo_schedule")

    def __repr__(self):
        return (f"<AlgoSchedules(id={self.id}, schedule='{self.schedule}', "
                f"is_active={self.is_active}, source='{self.source}', "
                f"timestamp={self.timestamp}, notes='{self.notes}')>")

@event.listens_for(AlgoSchedules.__table__, "after_create")
def insert_default_records(target, connection, **kwargs):
    """Ensure default market hour records exist for 'GLOBAL' and weekends."""
    try:
        connection.execute(target.insert(), DEFAULT_SCHEDULE_RECORDS)
        logger.info("Default market hours inserted successfully")
    except Exception as e:
        logger.error(f"Error inserting default records: {e}")