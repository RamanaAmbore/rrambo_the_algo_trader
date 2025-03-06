from datetime import datetime

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, select, JSON, text
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


# def timestamp_indian():
#     """Returns the current timestamp (Indian timezone adjustment can be handled externally)."""
#     return datetime.now()


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
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)  # User account ID
    placed_by = Column(String, nullable=False)  # Who placed the order (User ID)
    order_id = Column(String, nullable=False, unique=True)  # Unique order ID
    exchange_order_id = Column(String, nullable=True)  # Exchange-specific order ID
    parent_order_id = Column(String, nullable=True)  # Parent order ID (for multi-leg orders)

    # Order status tracking
    status = Column(String, nullable=False)  # Current order status (e.g., "COMPLETE", "CANCELLED")
    status_message = Column(String, nullable=True)  # Readable status message
    status_message_raw = Column(String, nullable=True)  # Raw status message from API

    # Order timestamps
    order_timestamp = Column(DateTime, nullable=False)  # Timestamp when order was placed
    exchange_update_timestamp = Column(DateTime, nullable=True)  # Exchange update timestamp
    exchange_timestamp = Column(DateTime, nullable=True)  # Exchange execution timestamp

    # Order details
    variety = Column(String, nullable=False)  # Order variety (e.g., "regular", "bo", "co")
    modified = Column(Boolean, default=False)  # Whether order was modified
    exchange = Column(String, nullable=False)  # Exchange (NSE/BSE)
    tradingsymbol = Column(String, nullable=False)  # Trading symbol (stock/future/option)
    instrument_token = Column(Integer, nullable=False)  # Instrument token for the order
    order_type = Column(String, nullable=False)  # Order type (LIMIT, MARKET, SL, SLM)
    transaction_type = Column(String, nullable=False)  # Buy/Sell
    validity = Column(String, nullable=False)  # Order validity (DAY, IOC)
    validity_ttl = Column(Integer, default=0)  # TTL for validity (if applicable)
    product = Column(String, nullable=False)  # Product type (MIS, CNC, NRML)

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
    tag = Column(String, nullable=True)  # Custom order tag (if any)
    guid = Column(String, nullable=True)  # Unique identifier for the order request
    source = Column(String, nullable=True, default="API")  # Source of the order placement

    # Logging and tracking
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)  # Flag to indicate warnings/errors
    msg = Column(String, nullable=True)  # Optional message or error details

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

    @classmethod
    async def get_all_results(cls, session: AsyncSession, account_id=Env.ZERODHA_USERNAME):
        """
        Fetch all orders for a specific account asynchronously.

        :param session: SQLAlchemy async session for database queries
        :param account_id: User account ID (default: from environment)
        :return: List of all orders for the given account
        """
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        """
        Converts API response data into an Orders instance.

        This method enables direct creation of an `Orders` object from API data.

        :param data: Dictionary containing order details from the API
        :return: `Orders` instance
        """
        return cls(**data)
