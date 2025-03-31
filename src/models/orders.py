from sqlalchemy import (Column, Integer, String, DateTime, Boolean, JSON, ForeignKey,
                        CheckConstraint, Index, func, text, DECIMAL)
from sqlalchemy.orm import relationship

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from .base import Base

logger = get_logger(__name__)

# Constants for ENUM fields
ORDER_STATUS = ["COMPLETE", "CANCELLED", "REJECTED", "PENDING", "OPEN"]
ORDER_VARIETY = ["regular", "bo", "co"]
ORDER_TYPE = ["MARKET", "LIMIT", "SL", "SLM"]
TRANSACTION_TYPE = ["BUY", "SELL"]
VALIDITY = ["DAY", "IOC"]
PRODUCT = ["MIS", "CNC", "NRML"]


class Orders(Base):
    """Model to store order details as per Zerodha Kite API."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Account & Order Identifiers
    account = Column(String(10), ForeignKey("broker_accounts.account", ondelete="CASCADE"), nullable=False, default='*')
    placed_by = Column(String(10), nullable=False)
    order_id = Column(String(20), nullable=False, unique=True)
    exchange_order_id = Column(String(20), nullable=True)
    parent_order_id = Column(String(20), ForeignKey("orders.order_id", ondelete="SET NULL"), nullable=True)

    # Order Status
    status = Column(String(15), nullable=False)
    status_message = Column(String(255), nullable=True)
    status_message_raw = Column(String(255), nullable=True)

    # Timestamps
    order_timestamp = Column(DateTime, nullable=False)
    exchange_update_timestamp = Column(DateTime, nullable=True)
    exchange_timestamp = Column(DateTime, nullable=True)

    # Order Details
    variety = Column(String(10), nullable=False)
    modified = Column(Boolean, default=False)
    exchange = Column(String(10), nullable=False)
    tradingsymbol = Column(String(50), nullable=False)
    instrument_token = Column(Integer, nullable=False)
    order_type = Column(String(10), nullable=False)
    transaction_type = Column(String(10), nullable=False)
    validity = Column(String(10), nullable=False)
    validity_ttl = Column(Integer, default=0)
    product = Column(String(10), nullable=False)

    # Price & Quantity
    quantity = Column(Integer, nullable=False, default=0)
    disclosed_quantity = Column(Integer, nullable=False, default=0)
    price = Column(DECIMAL(12, 4), nullable=False, default=0)
    trigger_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    average_price = Column(DECIMAL(12, 4), nullable=False, default=0)
    filled_quantity = Column(Integer, nullable=False, default=0)
    pending_quantity = Column(Integer, nullable=False, default=0)
    cancelled_quantity = Column(Integer, nullable=False, default=0)
    market_protection = Column(Integer, nullable=False, default=0)

    # Additional Metadata
    meta = Column(JSON, nullable=True)
    tag = Column(String(20), nullable=True)
    guid = Column(String(100), nullable=True)
    source = Column(String(50), nullable=False, server_default="API")

    # Logging & Tracking
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))
    upd_timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                           onupdate=func.now(), server_default=text("CURRENT_TIMESTAMP"))
    notes = Column(String(255), nullable=True)

    # Relationships
    broker_account = relationship("BrokerAccounts", back_populates="orders")
    parent_order = relationship("Orders", remote_side=[order_id])

    __table_args__ = (
        CheckConstraint("status IN ('COMPLETE', 'CANCELLED', 'REJECTED', 'PENDING', 'OPEN')",
                        name="check_valid_status"),
        CheckConstraint("variety IN ('regular', 'bo', 'co')", name="check_valid_variety"),
        CheckConstraint("order_type IN ('MARKET', 'LIMIT', 'SL', 'SLM')", name="check_valid_order_type"),
        CheckConstraint("transaction_type IN ('BUY', 'SELL')", name="check_valid_transaction_type"),
        CheckConstraint("validity IN ('DAY', 'IOC')", name="check_valid_validity"),
        CheckConstraint("product IN ('MIS', 'CNC', 'NRML')", name="check_valid_product"),
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        CheckConstraint("trigger_price >= 0", name="check_trigger_price_non_negative"),
        CheckConstraint("filled_quantity + pending_quantity + cancelled_quantity = quantity",
                        name="check_quantity_balance"),
        Index("idx_order_id1", "order_id"),
        Index("idx_account_timestamp2", "account", "timestamp"),
        Index("idx_instrument2", "instrument_token"),
    )

    def __repr__(self):
        return (f"<Orders(id={self.id}, order_id={self.order_id}, tradingsymbol={self.tradingsymbol}, "
                f"status={self.status}, quantity={self.quantity}, price={self.price}, "
                f"filled_quantity={self.filled_quantity}, pending_quantity={self.pending_quantity}, "
                f"exchange='{self.exchange}', transaction_type='{self.transaction_type}', "
                f"order_type='{self.order_type}', validity='{self.validity}', modified={self.modified}, "
                f"source='{self.source}')>")
