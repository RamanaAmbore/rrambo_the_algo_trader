from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Holdings
from utils.utils_func import to_decimal
from utils.db_connect import DbConnect as Db

def from_api_data(data):
    """
    Converts API response data into a Holdings instance with Decimal values.

    This method ensures that numeric fields are correctly converted
    to `Decimal` type to maintain precision.

    :param data: Dictionary containing holding details from API
    :return: `Holdings` instance
    """
    return Holdings(
        trading_symbol=data["tradingsymbol"],
        exchange=data["exchange"],
        quantity=int(data["quantity"]),
        average_price=to_decimal(data["average_price"]),
        current_price=to_decimal(data.get("last_price", 0.0)),
        pnl=to_decimal(data.get("pnl", 0.0)),
    )


async def get_all_holdings(sync=False):
    """
    Fetch all holdings from the database asynchronously.

    :param session: SQLAlchemy async session for database queries
    :return: List of all holdings
    """
    with Db.get_session(sync) as session:
        result = await session.execute(select(Holdings))
        return result.scalars().all()