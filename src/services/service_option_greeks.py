from sqlalchemy import select

from src.core.database_manager import DatabaseManager as Db
from src.helpers.utils import to_decimal
from src.models import OptionGreeks


async def get_all_results(account, sync=False):
    """Fetch all backtest results asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(OptionGreeks).where(OptionGreeks.account.is_(account)))
        return result.scalars().all()


def from_api_data(data):
    """Convert API response data into an OptionGreeks instance."""
    return OptionGreeks(instrument_token=int(data["instrument_token"]), delta=to_decimal(data.get("delta", 0.0)),
                        theta=to_decimal(data.get("theta", 0.0)), vega=to_decimal(data.get("vega", 0.0)),
                        gamma=to_decimal(data.get("gamma", 0.0)), iv=to_decimal(data.get("iv", 0.0), precision="0.01"),
                        # IV needs 2 decimal places
                        )
