from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint, Index, func, select
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.settings.constants_manager import Source, DEF_EXCHANGE_LIST
from .base import Base

logger = get_logger(__name__)


class ExchangeList(Base):
    """Model to store exchange information."""
    __tablename__ = "exchange_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(10), nullable=False, unique=True)  # NSE, BSE, etc.
    desc = Column(String(255), nullable=True)
    country = Column(String(50), nullable=False, default="INDIA")  # India, USA, etc.
    source = Column(String(50), nullable=False, server_default=Source.MANUAL)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    instrument_list_rel = relationship("InstrumentList", back_populates="exchange_rel", passive_deletes=True, )
    schedule_time_rel = relationship("ScheduleTime", back_populates="exchange_rel", passive_deletes=True, )

    __table_args__ = (
        UniqueConstraint("exchange", name="uq_exchange"),
        Index("idx_exchange", "exchange"),
    )

    def __repr__(self):
        return (f"<ExchangeList(id={self.id}, exchange='{self.exchange}', country='{self.country}', "
                f"source='{self.source}', timestamp={self.timestamp})>")


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ExchangeList.__table__
        for record in DEF_EXCHANGE_LIST:
            exists = connection.execute(
                select(table).where(table.c.exchange == record['exchange'])
            ).fetchone() is not None  # Fetch one record instead of scalar_one_or_none

            if not exists:
                connection.execute(table.insert().values(record))

        connection.commit()
        logger.info('Default Exchange List records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Exchange List records: {e}")
        raise
