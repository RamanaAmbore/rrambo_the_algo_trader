from sqlalchemy import (
    Column, String, Integer, DateTime, DECIMAL, text, Index, UniqueConstraint, func, Date, ForeignKey
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)


class InstrumentList(Base):
    """Model to store stock listing information."""
    __tablename__ = "instrument_list"

    id = Column(Integer, primary_key=True, autoincrement=True)

    tradingsymbol = Column(String(50), nullable=False)
    exchange_token = Column(String(20), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    @hybrid_property
    def symbol_exchange(self):
        return f"{self.tradingsymbol}:{self.exchange}"

    name = Column(String(50), nullable=False)
    segment = Column(String(50), nullable=False)
    instrument_type = Column(String(50), nullable=False)
    exchange = Column(String(10), ForeignKey("exchange_list.exchange", ondelete="CASCADE"), nullable=False)
    lot_size = Column(Integer, nullable=False, server_default=text("1"))
    last_price = Column(DECIMAL(10, 4), nullable=True)  # For options
    tick_size = Column(DECIMAL(10, 4), nullable=False, server_default=text("0.05"))
    expiry = Column(Date, nullable=True)  # Converted from String to Date
    strike = Column(DECIMAL(10, 4), nullable=True)  # For options

    source = Column(String(50), nullable=False, server_default="API")
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    positions_rel = relationship("Positions", back_populates="instrument_list_rel", passive_deletes=True, )
    holdings_rel = relationship("Holdings", back_populates="instrument_list_rel", passive_deletes=True, )
    exchange_rel = relationship("ExchangeList", back_populates="instrument_list_rel", passive_deletes=True, )

    __table_args__ = (
        # Composite unique constraint (needed for FK in Positions)
        UniqueConstraint("tradingsymbol", "exchange", name="uq_tradingsymbol"),

        # Indexes for performance
        Index("idx_tradingsymbol3", "tradingsymbol"),
        Index("idx_instrument_token1", "instrument_token"),
    )

    def __repr__(self):
        return (f"<InstrumentList(id={self.id}, tradingsymbol='{self.tradingsymbol}', "
                f"instrument_token={self.instrument_token}, exchange='{self.exchange}', "
                f"lot_size={self.lot_size}, source='{self.source}', timestamp={self.timestamp})>")
