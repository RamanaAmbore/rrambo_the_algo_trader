from sqlalchemy import select

from models import OptionGreeks
from utils.utils_func import to_decimal
from utils.db_connection import DbConnection as Db

async def get_all_results(account_id,sync=False):
    """Fetch all backtest results asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(OptionGreeks).where(OptionGreeks.account_id.is_(account_id)))
        return result.scalars().all()


def from_api_data(data):
    """Convert API response data into an OptionGreeks instance."""
    return OptionGreeks(instrument_token=int(data["instrument_token"]), delta=to_decimal(data.get("delta", 0.0)),
               theta=to_decimal(data.get("theta", 0.0)), vega=to_decimal(data.get("vega", 0.0)),
               gamma=to_decimal(data.get("gamma", 0.0)), iv=to_decimal(data.get("iv", 0.0), precision="0.01"),
               # IV needs 2 decimal places
               )
