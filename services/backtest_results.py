# Import utilities for timestamp handling and environment variables
from sqlalchemy import select

from models import BacktestResults
from utils.db_connect import DbConnect as Db


async def insert_result(result_data, sync=False):
    """
    Insert a new backtest result asynchronously.

    - This method takes a dictionary `result_data` with the required fields.
    - A new record is added to the database and committed.
    - The inserted record is refreshed and returned.

    :param session: SQLAlchemy async session for executing queries
    :param result_data: Dictionary containing backtest result data
    :return: The inserted `BacktestResults` object
    """
    with Db.get_session(sync) as session:
        new_result = BacktestResults(**result_data)  # Create an instance with provided data
        session.add(new_result)  # Add the new record to the session
        await session.commit()  # Commit the transaction to the database
        await session.refresh(new_result)  # Ensure the returned object is up-to-date
        return new_result  # Return the newly created record


async def get_all_results(account,sync=False):
    """
    Fetch all backtest results asynchronously.

    - If `account` is provided, fetches only results for that account.
    - If `account` is None, fetches all results from the table.

    :param session: SQLAlchemy async session for executing queries
    :param account: Optional account ID to filter results
    :return: List of backtest results matching the criteria
    """
    with Db.get_session(sync) as session:
        query = select(BacktestResults).order_by(BacktestResults.start_date.desc())  # Sort results by latest start_date
        if account:
            query = query.where(BacktestResults.account.is_(account))
    
        result = await session.execute(query)
        return result.scalars().all()
