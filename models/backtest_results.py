from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, text, String, Boolean
from sqlalchemy.future import select

# Import utilities for timestamp handling and environment variables
from utils.date_time_utils import timestamp_indian
from utils.settings_loader import Env
from .base import Base


class BacktestResults(Base):
    """
    Stores backtesting results for trading strategies.

    This table records the performance of different trading strategies
    over a specified period, storing key metrics such as profit/loss,
    drawdown, and win rate.
    """
    __tablename__ = "backtest_results"

    # Primary Key: Unique identifier for each backtest result
    id = Column(Integer, primary_key=True, autoincrement=True)

    # The account ID associated with the backtest (default to Zerodha username from environment settings)
    account_id = Column(String, nullable=False, default=Env.ZERODHA_USERNAME)

    # Foreign key linking the result to a specific strategy
    strategy_id = Column(Integer, ForeignKey("strategy_config.id"), nullable=False, index=True)

    # Start and end dates of the backtest period
    start_date = Column(DateTime(timezone=True), nullable=False)  # When the backtest started
    end_date = Column(DateTime(timezone=True), nullable=False)  # When the backtest ended

    # Key performance metrics of the backtest
    total_pnl = Column(DECIMAL(10, 2), nullable=False)  # Total profit/loss, stored with 2 decimal precision
    max_drawdown = Column(DECIMAL(10, 2), nullable=True)  # Maximum drawdown percentage (optional)
    win_rate = Column(DECIMAL(5, 2), nullable=True)  # Win rate percentage (e.g., 75.23%)

    # Source of the backtest data (e.g., "CODE" for programmatically generated backtests)
    source = Column(String, nullable=True, default="CODE")

    # Timestamp indicating when the record was created
    timestamp = Column(DateTime(timezone=True), nullable=False, default=timestamp_indian,
                       server_default=text("CURRENT_TIMESTAMP"))

    # Flags to indicate errors or warnings
    warning_error = Column(Boolean, default=False)  # Whether the backtest encountered warnings or errors
    msg = Column(String, nullable=True)  # Any additional messages or error details

    def __repr__(self):
        """
        Returns a string representation of the object for debugging purposes.
        """
        return (f"<BacktestResults(id={self.id}, account_id='{self.account_id}', strategy_id={self.strategy_id}, "
                f"start_date={self.start_date}, end_date={self.end_date}, total_pnl={self.total_pnl}, "
                f"max_drawdown={self.max_drawdown}, win_rate={self.win_rate}, source='{self.source}', "
                f"warning_error={self.warning_error}, msg='{self.msg}')>")

    @classmethod
    async def get_all_results(cls, session, account_id=None):
        """
        Fetch all backtest results asynchronously.

        - If `account_id` is provided, fetches only results for that account.
        - If `account_id` is None, fetches all results from the table.

        :param session: SQLAlchemy async session for executing queries
        :param account_id: Optional account ID to filter results
        :return: List of backtest results matching the criteria
        """
        query = select(cls)  # Base query to select all records
        if account_id is not None:
            query = query.where(cls.account_id == account_id)  # Apply filter if account_id is provided

        result = await session.execute(query)
        return result.scalars().all()  # Return all matching records as a list

    @classmethod
    async def insert_result(cls, session, result_data):
        """
        Insert a new backtest result asynchronously.

        - This method takes a dictionary `result_data` with the required fields.
        - A new record is added to the database and committed.
        - The inserted record is refreshed and returned.

        :param session: SQLAlchemy async session for executing queries
        :param result_data: Dictionary containing backtest result data
        :return: The inserted `BacktestResults` object
        """
        new_result = cls(**result_data)  # Create an instance with provided data
        session.add(new_result)  # Add the new record to the session
        await session.commit()  # Commit the transaction to the database
        await session.refresh(new_result)  # Ensure the returned object is up-to-date
        return new_result  # Return the newly created record

