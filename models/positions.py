from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, select, text, Numeric, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from utils.date_time_utils import timestamp_indian
# Custom utilities
from utils.settings_loader import Env
from .base import Base


class Positions(Base):
    """
    Represents the positions held in a trading account.

    Attributes:
        id (int): Unique identifier for each position.
        account_id (str): Associated account ID.
        tradingsymbol (str): Trading symbol of the position.
        exchange (str): Exchange where the position is traded.
        instrument_token (int): Unique instrument token.
        product (str): Product type (e.g., MIS, CNC).
        quantity (int): Quantity of the position.
        overnight_quantity (int): Quantity held overnight.
        multiplier (int): Multiplier for the position.
        average_price (Decimal): Average price.
        close_price (Decimal): Closing price.
        last_price (Decimal): Last traded price.
        value (Decimal): Value of the position.
        pnl (Decimal): Profit and loss.
        m2m (Decimal): Mark-to-market value.
        unrealised (Decimal): Unrealised P&L.
        realised (Decimal): Realised P&L.
        buy_quantity (int): Buy quantity.
        buy_price (Decimal): Buy price.
        buy_value (Decimal): Buy value.
        buy_m2m (Decimal): Buy mark-to-market value.
        sell_quantity (int): Sell quantity.
        sell_price (Decimal): Sell price.
        sell_value (Decimal): Sell value.
        sell_m2m (Decimal): Sell mark-to-market value.
        day_buy_quantity (int): Day buy quantity.
        day_buy_price (Decimal): Day buy price.
        day_buy_value (Decimal): Day buy value.
        day_sell_quantity (int): Day sell quantity.
        day_sell_price (Decimal): Day sell price.
        day_sell_value (Decimal): Day sell value.
        source (str): Source of data.
        timestamp (datetime): Record creation timestamp.
        warning_error (bool): Warning or error flag.
        msg (str): Optional message.
    """
    __tablename__ = "positions"

    # Column definitions
    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier for each position
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)  # Associated account ID
    tradingsymbol = Column(String, nullable=False)  # Trading symbol of the position
    exchange = Column(String, nullable=False)  # Exchange where the position is traded
    instrument_token = Column(Integer, nullable=False, unique=True)  # Unique instrument token
    product = Column(String, nullable=False)  # Product type (e.g., MIS, CNC)
    quantity = Column(Integer, default=0)  # Quantity of the position
    overnight_quantity = Column(Integer, default=0)  # Quantity held overnight
    multiplier = Column(Integer, default=1)  # Multiplier for the position
    average_price = Column(Numeric(10, 2), default=0)  # Average price
    close_price = Column(Numeric(10, 2), default=0)  # Closing price
    last_price = Column(Numeric(10, 2), default=0)  # Last traded price
    value = Column(Numeric(12, 2), default=0)  # Value of the position
    pnl = Column(Numeric(12, 2), default=0)  # Profit and loss
    m2m = Column(Numeric(12, 2), default=0)  # Mark-to-market value
    unrealised = Column(Numeric(12, 2), default=0)  # Unrealised P&L
    realised = Column(Numeric(12, 2), default=0)  # Realised P&L
    buy_quantity = Column(Integer, default=0)  # Buy quantity
    buy_price = Column(Numeric(10, 2), default=0)  # Buy price
    buy_value = Column(Numeric(12, 2), default=0)  # Buy value
    buy_m2m = Column(Numeric(12, 2), default=0)  # Buy mark-to-market value
    sell_quantity = Column(Integer, default=0)  # Sell quantity
    sell_price = Column(Numeric(10, 2), default=0)  # Sell price
    sell_value = Column(Numeric(12, 2), default=0)  # Sell value
    sell_m2m = Column(Numeric(12, 2), default=0)  # Sell mark-to-market value
    day_buy_quantity = Column(Integer, default=0)  # Day buy quantity
    day_buy_price = Column(Numeric(10, 2), default=0)  # Day buy price
    day_buy_value = Column(Numeric(12, 2), default=0)  # Day buy value
    day_sell_quantity = Column(Integer, default=0)  # Day sell quantity
    day_sell_price = Column(Numeric(10, 2), default=0)  # Day sell price
    day_sell_value = Column(Numeric(12, 2), default=0)  # Day sell value
    source = Column(String, nullable=True, default="API")  # Source of data
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)  # Warning or error flag
    msg = Column(String, nullable=True)  # Optional message

    @classmethod
    async def get_all_results(cls, session, account_id=Env.ZERODHA_USERNAME):
        """
        Fetch all backtest results asynchronously.

        Args:
            session (AsyncSession): SQLAlchemy AsyncSession instance.
            account_id (str): Account ID to filter the results. Defaults to Env.ZERODHA_USERNAME.

        Returns:
            list: List of all backtest results for the specified account ID.
        """
        result = await session.execute(select(cls).where(cls.account_id == account_id))
        return result.scalars().all()

    @classmethod
    def from_api_data(cls, data):
        """
        Create a Positions instance from API data.

        Args:
            data (dict): Data from the API.

        Returns:
            Positions: A new Positions instance populated with the provided data.
        """
        return cls(**data)

    def __repr__(self):
        """
        Provides a string representation of the Positions instance.

        Returns:
            str: String representation of the Positions instance.
        """
        return f"<Positions(tradingsymbol={self.tradingsymbol}, exchange={self.exchange}, quantity={self.quantity})>"
