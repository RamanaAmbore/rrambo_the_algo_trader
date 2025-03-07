from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Positions
# Custom utilities
from utils.settings_loader import Env
from utils.db_connection import DbConnection as Db

async def get_all_results(account_id, sync=False):
    """
    Fetch all backtest results asynchronously.

    Args:
        session (AsyncSession): SQLAlchemy AsyncSession instance.
        account_id (str): Account ID to filter the results. Defaults to Env.ZERODHA_USERNAME.

    Returns:
        list: List of all backtest results for the specified account ID.
    """
    with Db.get_session(sync) as session:
        result = await session.execute(select(Positions).where(Positions.account_id.is_(account_id)))
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
