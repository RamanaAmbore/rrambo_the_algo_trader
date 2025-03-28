from sqlalchemy import select

from src.models import Orders


async def get_all_results(account, sync=False):
    """
    Fetch all orders for a specific account asynchronously.

    :param session: SQLAlchemy async session for database queries
    :param account: User account ID (default: from environment)
    :return: List of all orders for the given account
    """
    with Db.get_session(sync) as session:
        result = await session.execute(select(Orders).where(Orders.account.is_(account)))
        return result.scalars().all()


def from_api_data(data):
    """
    Converts API response data into an Orders instance.

    This method enables direct creation of an `Orders` object from API data.

    :param data: Dictionary containing order details from the API
    :return: `Orders` instance
    """
    return Orders(**data)
