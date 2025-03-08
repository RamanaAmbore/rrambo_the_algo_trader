from decimal import Decimal, ROUND_DOWN

from sqlalchemy import select

from models import OptionStrategies
from utils.db_connection import DbConnection as Db
from utils.utils_func import to_decimal


async def get_all_results(account, sync=False):
    """Fetch all backtest results asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(OptionStrategies).where(OptionStrategies.account.is_(account)))
        return result.scalars().all()


def from_api_data(data):
    """Convert API response data into an OptionStrategies instance."""
    return OptionStrategies(strategy_name=data["strategy_name"], legs=data["legs"],  # JSON format is assumed correct
                            max_profit=to_decimal(data.get("max_profit", 0.0)),
                            max_loss=to_decimal(data.get("max_loss", 0.0)),
                            breakeven_points=data.get("breakeven_points", []),  # Default to empty list
                            )
