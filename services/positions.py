from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Positions
# Custom utilities
from utils.parms import Parms
from utils.db_connect import DbConnect as Db

async def get_all_results(account, sync=False):
    """
    Fetch all backtest results asynchronously.

    Args:
        session (AsyncSession): SQLAlchemy AsyncSession instance.
        account (str): Account ID to filter the results. Defaults to Env.ZERODHA_USERNAME.

    Returns:
        list: List of all backtest results for the specified account ID.
    """
    with Db.get_session(sync) as session:
        result = await session.execute(select(Positions).where(Positions.account.is_(account)))
        return result.scalars().all()


def from_api_data(data):
    """
    Create a Positions instance from API data.

    Args:
        data (dict): Data from the API.

    Returns:
        Positions: A new Positions instance populated with the provided data.
    """
    return Positions(**data)
