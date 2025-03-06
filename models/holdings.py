from decimal import Decimal, ROUND_DOWN

from sqlalchemy import Column, Integer, String, DateTime, select, DECIMAL, text, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


def to_decimal(value):
    """Convert a float to a Decimal with 2 decimal places, rounding down."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class Holdings(Base):
    """
    Model to store portfolio holdings, structured to match Zerodha Kite API.

    This table maintains records of stocks held in a trading account,
    including trading symbol, exchange, quantity, average price, and
    profit/loss details.
    """
    __tablename__ = "holdings"

    # Primary key: Unique identifier for each holding entry
    id = Column(Integer, primary_key=True, autoincrement=True)

    # The account ID associated with the holdings (default: Zerodha username from environment settings)
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)

    # Stock details
    trading_symbol = Column(String, nullable=False, index=True)  # Indexed for faster searches
    exchange = Column(String, nullable=False)  # Exchange where the stock is listed (NSE/BSE)
    quantity = Column(Integer, nullable=False)  # Number of shares held

    # Price and performance metrics
    average_price = Column(DECIMAL(10, 2), nullable=False)  # Average buy price per share
    current_price = Column(DECIMAL(10, 2), nullable=True)  # Latest market price per share
    pnl = Column(DECIMAL(10, 2), nullable=True)  # Profit/Loss value

    # Additional metadata
    source = Column(String, nullable=True, default="SCHEDULE")  # Data source (e.g., scheduled sync)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)  # Flag to indicate warnings or errors
    msg = Column(String, nullable=True)  # Optional message or warning details

    def __repr__(self):
        """
        Returns a string representation of the object for debugging purposes.
        """
        return (f"<Holdings(id={self.id}, account_id='{self.account_id}', trading_symbol='{self.trading_symbol}', "
                f"exchange='{self.exchange}', quantity={self.quantity}, avg_price={self.average_price}, "
                f"current_price={self.current_price}, pnl={self.pnl}, source='{self.source}', "
                f"warning_error={self.warning_error}, msg='{self.msg}')>")

    @classmethod
    def from_api_data(cls, data):
        """
        Converts API response data into a Holdings instance with Decimal values.

        This method ensures that numeric fields are correctly converted
        to `Decimal` type to maintain precision.

        :param data: Dictionary containing holding details from API
        :return: `Holdings` instance
        """
        return cls(
            trading_symbol=data["tradingsymbol"],
            exchange=data["exchange"],
            quantity=int(data["quantity"]),
            average_price=to_decimal(data["average_price"]),
            current_price=to_decimal(data.get("last_price", 0.0)),
            pnl=to_decimal(data.get("pnl", 0.0)),
        )

    @classmethod
    async def get_all_holdings(cls, session: AsyncSession):
        """
        Fetch all holdings from the database asynchronously.

        :param session: SQLAlchemy async session for database queries
        :return: List of all holdings
        """
        result = await session.execute(select(cls))
        return result.scalars().all()
