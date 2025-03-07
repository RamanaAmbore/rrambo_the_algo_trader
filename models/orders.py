from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, JSON, text, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base
from model_utils import source




class Orders(Base):
    """
    Model to store order details as per Zerodha Kite API.

    This table captures all relevant details about an order, including
    timestamps, order type, price, status, and other metadata.
    """
    __tablename__ = "orders"

    # Primary key: Unique identifier for each order entry
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Account and order identifiers
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    placed_by = Column(String(10), nullable=False)  # Who placed the order (User ID)
    order_id = Column(String(20), nullable=False, unique=True)  # Unique order ID
    exchange_order_id = Column(String(20), nullable=True)  # Exchange-specific order ID
    parent_order_id = Column(String(20), nullable=True)  # Parent order ID (for multi-leg orders)

    # Order status tracking
    status = Column(String(15), nullable=False)  # Current order status (e.g., "COMPLETE", "CANCELLED")
    status_message = Column(String(255), nullable=True)  # Readable status message
    status_message_raw = Column(String(255), nullable=True)  # Raw status message from API

    # Order timestamps
    order_timestamp = Column(DateTime, nullable=False)  # Timestamp when order was placed
    exchange_update_timestamp = Column(DateTime, nullable=True)  # Exchange update timestamp
    exchange_timestamp = Column(DateTime, nullable=True)  # Exchange execution timestamp

    # Order details
    variety = Column(String(10), nullable=False)  # Order variety (e.g., "regular", "bo", "co")
    modified = Column(Boolean, default=False)  # Whether order was modified
    exchange = Column(String(10), nullable=False)  # Exchange (NSE/BSE)
    tradingsymbol = Column(String(20), nullable=False)  # Trading symbol (stock/future/option)
    instrument_token = Column(Integer, nullable=False)  # Instrument token for the order
    order_type = Column(String(10), nullable=False)  # Order type (LIMIT, MARKET, SL, SLM)
    transaction_type = Column(String(10), nullable=False)  # Buy/Sell
    validity = Column(String(10), nullable=False)  # Order validity (DAY, IOC)
    validity_ttl = Column(Integer, default=0)  # TTL for validity (if applicable)
    product = Column(String(10), nullable=False)  # Product type (MIS, CNC, NRML)

    # Price and quantity details
    quantity = Column(Integer, default=0)  # Total order quantity
    disclosed_quantity = Column(Integer, default=0)  # Disclosed quantity (visible to market)
    price = Column(Numeric(10, 2), default=0)  # Order price
    trigger_price = Column(Numeric(10, 2), default=0)  # Stop-loss trigger price
    average_price = Column(Numeric(10, 2), default=0)  # Average execution price
    filled_quantity = Column(Integer, default=0)  # Quantity already executed
    pending_quantity = Column(Integer, default=0)  # Remaining quantity to be executed
    cancelled_quantity = Column(Integer, default=0)  # Quantity canceled
    market_protection = Column(Integer, default=0)  # Protection for market orders

    # Additional metadata
    meta = Column(JSON, nullable=True)  # Any additional order metadata (JSON format)
    tag = Column(String(20), nullable=True)  # Custom order tag (if any)
    guid = Column(String(100), nullable=True)  # Unique identifier for the order request
    source = Column(Enum(source), nullable=True, server_default="API")  # Token source (e.g., API)

    # Logging and tracking
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)  # Flag to indicate warnings/errors
    notes = Column(String(255), nullable=True)  # Optional message or error details

    def __repr__(self):
        """
        Returns a string representation of the order for debugging.
        """
        return (f"<Orders(id={self.id}, order_id={self.order_id}, tradingsymbol={self.tradingsymbol}, "
                f"status={self.status}, quantity={self.quantity}, price={self.price}, "
                f"filled_quantity={self.filled_quantity}, pending_quantity={self.pending_quantity}, "
                f"exchange='{self.exchange}', transaction_type='{self.transaction_type}', "
                f"order_type='{self.order_type}', validity='{self.validity}', modified={self.modified}, "
                f"source='{self.source}', warning_error={self.warning_error})>")
