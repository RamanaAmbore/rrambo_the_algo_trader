from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, text, Boolean, ForeignKey, Enum

from utils.date_time_utils import timestamp_indian
from .base import Base

from model_utils import source
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
    account_id = Column(String(10), ForeignKey("broker_accounts.account_id", ondelete="CASCADE"), nullable=True)
    # Stock details
    trading_symbol = Column(String(20), nullable=False, index=True)  # Indexed for faster searches
    exchange = Column(String(10), nullable=False)  # Exchange where the stock is listed (NSE/BSE)
    quantity = Column(Integer, nullable=False)  # Number of shares held

    # Price and performance metrics
    average_price = Column(DECIMAL(10, 2), nullable=False)  # Average buy price per share
    current_price = Column(DECIMAL(10, 2), nullable=True)  # Latest market price per share
    pnl = Column(DECIMAL(10, 2), nullable=True)  # Profit/Loss value

    # Additional metadata
    source = Column(Enum(source), nullable=True, server_default="REPORTS")  # Token source (e.g., API)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))  # Record creation timestamp
    warning_error = Column(Boolean, default=False)  # Flag to indicate warnings or errors
    notes = Column(String(255), nullable=True)  # Optional message field for additional info

    def __repr__(self):
        """
        Returns a string representation of the object for debugging purposes.
        """
        return (f"<Holdings(id={self.id}, account_id='{self.account_id}', trading_symbol='{self.trading_symbol}', "
                f"exchange='{self.exchange}', quantity={self.quantity}, avg_price={self.average_price}, "
                f"current_price={self.current_price}, pnl={self.pnl}, source='{self.source}', "
                f"warning_error={self.warning_error}, notes='{self.notes}')>")
