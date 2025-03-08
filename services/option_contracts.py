from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from models import OptionContracts
from utils.parameter_loader import sc
from utils.utils_func import to_decimal
from utils.db_connection import DbConnection as Db

async def get_all_results(account, sync=False):
    """Fetch all backtest results asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(OptionContracts).where(OptionContracts.account.is_(account)))
        return result.scalars().all()


def from_api_data(data):
    """Convert API response data into an OptionContracts instance."""
    return OptionContracts(instrument_token=int(data["instrument_token"]), trading_symbol=data["tradingsymbol"],
               expiry_date=datetime.strptime(data["expiry"], "%Y-%m-%d").replace(tzinfo=ZoneInfo(sc.INDIAN_TIMEZONE)),
               strike_price=to_decimal(data["strike"]), option_type=data["instrument_type"],  # CE / PE
               lot_size=int(data["lot_size"]), tick_size=to_decimal(data["tick_size"]), )
